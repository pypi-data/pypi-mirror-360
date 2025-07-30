from typing import Optional, TYPE_CHECKING
from urllib.parse import urljoin

from common.api_utils import EndpointModel
from common.auth_utils import imbue_header_with_access_token
from tasx.mixins._shared import ClientBind

if TYPE_CHECKING:
    from tasx.interface_models import ServiceRead


class TaskReadMixin(ClientBind):
    name: str
    service: Optional["ServiceRead"]
    argument_schema: dict

    def build_endpoint(
        self, authorization: str | None = None, **endpoint_kwargs
    ) -> EndpointModel:
        if self.service is None:
            raise ValueError("Service is required to build the endpoint.")
        if self.service.provider is None:
            raise ValueError("Provider is required to build the endpoint.")
        base_url = self.service.provider.base_url
        url_postfix = self.service.provider.url_postfix
        provider_url = urljoin(base_url, url_postfix)
        headers = endpoint_kwargs.pop("headers", {})
        if authorization is not None:
            headers = imbue_header_with_access_token(authorization, headers)
        return EndpointModel(
            url=f"{provider_url}/{self.service.name}/{self.name}",
            method="POST",
            headers=headers,
            **endpoint_kwargs,
        )

    @property
    def endpoint(self):
        storage = self.get_or_create_transient_storage()
        endpoint = storage.get("endpoint")
        if endpoint is None:
            endpoint = self.build_endpoint()
            storage.set("endpoint", endpoint)
        return endpoint

    @property
    def task_address(self) -> str | None:
        if self.service is None:
            return None
        if self.service.provider is None:
            return None
        return f"{self.service.provider.name}/{self.service.name}/{self.name}"
