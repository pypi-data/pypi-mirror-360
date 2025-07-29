from typing import Optional

from pydantic import UUID4

from galileo_core.constants.request_method import RequestMethod
from galileo_core.constants.routes import Routes
from galileo_core.exceptions.http import GalileoHTTPException
from galileo_core.helpers.logger import logger
from galileo_core.schemas.base_config import GalileoConfig
from galileo_core.schemas.core.collaboration_role import CollaboratorRole
from galileo_core.schemas.core.collaborator import UserCollaboratorCreate
from galileo_core.schemas.core.integration.user_integration import (
    UserIntegrationCollaboratorResponse,
)


def share_integration_with_user(
    integration_id: UUID4,
    user_id: UUID4,
    config: Optional[GalileoConfig] = None,
) -> UserIntegrationCollaboratorResponse:
    config = config or GalileoConfig.get()
    logger.debug(f"Sharing integration {integration_id} with user {user_id} with role {CollaboratorRole.viewer}...")
    response_dict = config.api_client.request(
        RequestMethod.POST,
        Routes.integration_users.format(integration_id=integration_id),
        json=[UserCollaboratorCreate(user_id=user_id).model_dump(mode="json")],
    )
    user_shared = [UserIntegrationCollaboratorResponse.model_validate(user) for user in response_dict]
    logger.debug(f"Shared integration {integration_id} with user {user_id} with role {CollaboratorRole.viewer}.")

    try:
        return user_shared[0]
    except IndexError:
        raise GalileoHTTPException(
            message="Galileo API returned empty response.",
            status_code=422,
            response_text=f"Response body {user_shared}",
        )
