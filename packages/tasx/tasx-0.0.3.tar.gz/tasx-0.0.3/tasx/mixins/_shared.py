from typing import Optional, TYPE_CHECKING, Union

from common.core.utils import TransientStorageMixin

if TYPE_CHECKING:
    from tasx.tasx_client import TasxClient, TasxRunnerClient, TasxRegistryClient


class ClientBind(TransientStorageMixin):
    def bind_client(
        self,
        tasx_client: Union[
            "TasxClient", "TasxRunnerClient", "TasxRegistryClient", None
        ] = None,
    ) -> "ClientBind":
        storage = self.get_or_create_transient_storage()
        if tasx_client is None:
            # Check if there's an existing TasxClient in storage
            tasx_client = storage.get("tasx_client")
            if tasx_client is not None:
                # It's already bound, no need to rebind
                return self

            from tasx.tasx_client import TasxClient

            # Bind the default client
            tasx_client = TasxClient()
        storage.set("tasx_client", tasx_client)
        return self

    @property
    def tasx_client(self) -> "TasxClient":
        storage = self.get_or_create_transient_storage()
        tasx_client = storage.get("tasx_client")
        if tasx_client is None:
            tasx_client = self.bind_client().tasx_client
        return tasx_client
