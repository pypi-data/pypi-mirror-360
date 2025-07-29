from typing import Optional

from pydantic import UUID4

from galileo_core.constants.request_method import RequestMethod
from galileo_core.constants.routes import Routes
from galileo_core.exceptions.http import GalileoHTTPException
from galileo_core.helpers.logger import logger
from galileo_core.schemas.base_config import GalileoConfig
from galileo_core.schemas.core.collaboration_role import CollaboratorRole
from galileo_core.schemas.core.collaborator import GroupCollaboratorCreate
from galileo_core.schemas.core.integration.group_integration import (
    GroupIntegrationCollaboratorResponse,
)


def share_integration_with_group(
    integration_id: UUID4,
    group_id: UUID4,
    config: Optional[GalileoConfig] = None,
) -> GroupIntegrationCollaboratorResponse:
    config = config or GalileoConfig.get()
    logger.debug(f"Sharing integration {integration_id} with group {group_id} with role {CollaboratorRole.viewer}...")
    response_dict = config.api_client.request(
        RequestMethod.POST,
        Routes.integration_groups.format(integration_id=integration_id),
        json=[GroupCollaboratorCreate(group_id=group_id).model_dump(mode="json")],
    )
    group_shared = [GroupIntegrationCollaboratorResponse.model_validate(group) for group in response_dict]
    logger.debug(f"Shared integration {integration_id} with group {group_id} with role {CollaboratorRole.viewer}.")

    try:
        return group_shared[0]
    except IndexError:
        raise GalileoHTTPException(
            message="Galileo API returned empty response.",
            status_code=422,
            response_text=f"Response body {group_shared}",
        )
