from copy import deepcopy
from urllib.parse import urlparse

import httpx
from typing import Optional, Any

from pydantic import BaseModel

from common.api_utils import APIConnectionError
from common.auth_utils import (
    imbue_header_with_service_type,
    imbue_header_with_service_key,
    imbue_header_with_access_token,
)


class ProviderSpecificConfig(BaseModel):
    base_url: str | None = None
    api_key: str | None = None


class BaseTasxClient:
    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        service_type: str | None = None,
        service_key: str | None = None,
        provider_configs: dict[str, ProviderSpecificConfig] | None = None,
        handle_ngrok: bool = True,
    ):
        self.base_url = base_url
        self.api_key = api_key
        self.service_type = service_type
        self.service_key = service_key
        self.provider_configs = provider_configs or {}
        self.handle_ngrok = handle_ngrok

    def clone(self):
        return deepcopy(self)

    def get_base_url_for_provider(self, provider_name: str, default: Any = None) -> str:
        config = self.provider_configs.get(provider_name)
        return config.base_url if config else default

    def get_api_key_for_provider(self, provider_name: str, default: Any = None) -> str:
        config = self.provider_configs.get(provider_name)
        return config.api_key if config else default

    def configure_provider(
        self,
        provider_name: str,
        base_url: str | None = None,
        api_key: str | None = None,
    ) -> "BaseTasxClient":
        self.provider_configs[provider_name] = ProviderSpecificConfig(
            base_url=base_url, api_key=api_key
        )
        return self

    async def _make_request(
        self,
        method: str,
        path: str,
        base_url: str | None = None,
        api_key: str | None = None,
        **kwargs,
    ) -> dict:
        # Build the url
        if base_url is None:
            base_url = self.base_url

        url = f"{base_url}{path}"

        headers = {}
        # Use provided api_key if available, otherwise fall back to default
        if api_key:
            headers = imbue_header_with_access_token(api_key, headers)
        elif self.api_key:
            headers = imbue_header_with_access_token(self.api_key, headers)

        if self.service_type:
            headers = imbue_header_with_service_type(self.service_type, headers)

        if self.service_key:
            headers = imbue_header_with_service_key(self.service_key, headers)

        if self.handle_ngrok:
            netloc = urlparse(url).netloc
            if "ngrok" in netloc:
                headers["ngrok-skip-browser-warning"] = "true"

        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.request(method, url, headers=headers, **kwargs)
            except httpx.ConnectError as e:
                raise APIConnectionError(f"Failed to connect to {url}") from e

            return await self._handle_response(response, path)

    async def _handle_response(self, response: httpx.Response, path: str) -> dict:
        raise NotImplementedError("Subclasses must implement _handle_response")
