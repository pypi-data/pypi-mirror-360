from ssl import SSLContext
from typing import Any, Dict, Union
from urllib.parse import urljoin

from httpx import AsyncClient, HTTPError, Response, Timeout
from pydantic import BaseModel, ConfigDict, HttpUrl, SecretStr

from galileo_core.constants.http_headers import HttpHeaders
from galileo_core.constants.request_method import RequestMethod
from galileo_core.exceptions.http import GalileoHTTPException
from galileo_core.helpers.execution import async_run
from galileo_core.helpers.logger import logger


class ApiClient(BaseModel):
    host: HttpUrl
    jwt_token: SecretStr
    ssl_context: Union[SSLContext, bool] = True

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def auth_header(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.jwt_token.get_secret_value()}"}

    @staticmethod
    def validate_response(response: Response) -> None:
        for header, value in response.headers.items():
            # Log all Galileo headers. These are headers that start with `Galileo-Request-`.
            # These can be in any case, so we lower-case them for comparison.
            if header.lower().startswith("galileo-request-"):
                logger.debug(f"{header.title()}: {value}.")
        try:
            response.raise_for_status()
        except HTTPError:
            raise GalileoHTTPException(
                f"Galileo API returned HTTP status code {response.status_code}. Error was: {response.text}",
                response.status_code,
                response.text,
            )

    @staticmethod
    async def make_request(
        request_method: RequestMethod,
        base_url: str,
        endpoint: str,
        ssl_context: Union[SSLContext, bool] = True,
        read_timeout: float = 60.0,
        return_raw_response: bool = False,
        **kwargs: Any,
    ) -> Any:
        url = urljoin(base_url, endpoint)
        logger.debug(f"Making request to {url}.")
        async with AsyncClient(
            base_url=base_url, timeout=Timeout(read_timeout, connect=5.0), verify=ssl_context
        ) as client:
            response = await client.request(method=request_method.value, url=url, timeout=read_timeout, **kwargs)
            ApiClient.validate_response(response)
            logger.debug(f"Response was received from {url}.")
            # If the caller asked for the raw Response object, just return it.
            if return_raw_response:
                return response

            # Some successful responses (e.g. HTTP 204 No Content) legitimately have no body.
            # Attempting to call `response.json()` in these cases raises a JSONDecodeError.
            # We treat 204 responses or any response with an empty body as having no payload
            # and return `None` to the caller.
            if response.status_code == 204 or not response.content:
                return None

            # Otherwise attempt to parse the response as JSON. If this fails, fall back to
            # returning the raw text content so the caller still receives the payload.
            try:
                return response.json()
            except ValueError:
                return response.text

    def request(
        self,
        method: RequestMethod,
        path: str,
        content_headers: Dict[str, str] = HttpHeaders.json(),
        **kwargs: Any,
    ) -> Any:
        return async_run(self.arequest(method=method, path=path, content_headers=content_headers, **kwargs))

    async def arequest(
        self,
        method: RequestMethod,
        path: str,
        content_headers: Dict[str, str] = HttpHeaders.json(),
        **kwargs: Any,
    ) -> Any:
        return await ApiClient.make_request(
            request_method=method,
            base_url=self.host.unicode_string(),
            endpoint=path,
            headers={**content_headers, **self.auth_header},
            ssl_context=self.ssl_context,
            **kwargs,
        )
