from urllib.parse import urljoin

from common.config import common_settings as settings
from common.services import ServiceType
from tasx.registry import TasxRegistryClient
from tasx.runner import TasxRunnerClient


class TasxClient:
    def __init__(
        self,
        api_base: str | None = None,
        registry_url: str | None = None,
        runner_url: str | None = None,
        registry_api_key: str | None = None,
        runner_api_key: str | None = None,
        service_type: str | None = None,
        service_key: str | None = None,
    ):
        if api_base is not None:
            assert (
                registry_url is None and runner_url is None
            ), "Cannot specify both api_base and registry_url/runner_url"
            registry_url = urljoin(
                api_base, settings.services.get_path_prefix(ServiceType.REGISTRY)
            )
            runner_url = urljoin(
                api_base, settings.services.get_path_prefix(ServiceType.RUNNER)
            )
        else:
            registry_url = registry_url or settings.services.get_internal_url(
                ServiceType.REGISTRY
            )
            runner_url = runner_url or settings.services.get_internal_url(
                ServiceType.RUNNER
            )

        self._registry_client = TasxRegistryClient(
            base_url=registry_url,
            api_key=registry_api_key,
            service_type=service_type,
            service_key=service_key,
        )
        self._runner_client = TasxRunnerClient(
            base_url=runner_url,
            api_key=runner_api_key,
            service_type=service_type,
            service_key=service_key,
        )

    @property
    def registry_client(self) -> TasxRegistryClient:
        return self._registry_client

    @property
    def runner_client(self) -> TasxRunnerClient:
        return self._runner_client

    def __getattr__(self, item):
        if isinstance(item, str) and item.startswith("__") and item.endswith("__"):
            # This is needed for deepcopy to work correctly
            raise AttributeError(f"Attribute {item} not found in TasxClient")
        
        try:
            if hasattr(self._registry_client, item):
                return getattr(self._registry_client, item)
        except AttributeError:
            # _registry_client doesn't exist, skip it
            pass
        
        try:
            if hasattr(self._runner_client, item):
                return getattr(self._runner_client, item)
        except AttributeError:
            # _runner_client doesn't exist, skip it
            pass
        
        raise AttributeError(f"Attribute {item} not found in TasxClient")
