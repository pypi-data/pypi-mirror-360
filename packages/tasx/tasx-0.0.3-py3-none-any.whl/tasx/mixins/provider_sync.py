from typing import TYPE_CHECKING

from common.api_utils import EndpointModel

if TYPE_CHECKING:
    from tasx.interface_models import ProviderSync


class ProviderSyncMixin:
    @classmethod
    async def from_provider_url(cls, url: str) -> "ProviderSync":
        endpoint = EndpointModel(url=url, method="GET")
        response = await endpoint()
        return cls.model_validate(response.payload)  # noqa
