import httpx
from loguru import logger
from tasx.base_client import BaseTasxClient
from tasx.exceptions import TasxRegistryAPIError, TaskNotFoundError
from tasx.interface_models import (
    TaskCreate,
    TaskUpdate,
    TaskRead,
    ServiceCreate,
    ServiceRead,
    ServiceUpdate,
    ProviderRead,
    ProviderSync,
    ProviderCreate,
    TaskAddressModel,
)
from typing import List, Optional, Literal, Tuple
import asyncio


class TasxRegistryClient(BaseTasxClient):

    async def _handle_response(self, response: httpx.Response, path: str) -> dict:
        if response.status_code == 404:
            if "task" in path:
                raise TaskNotFoundError("Task not found")
            raise TasxRegistryAPIError("Resource not found")
        elif response.status_code >= 400:
            raise TasxRegistryAPIError(f"API request failed: {response.text}")

        return response.json() if response.status_code != 204 else None

    # Provider endpoints
    async def create_provider(self, provider_create: ProviderCreate) -> ProviderRead:
        """Create a new provider in the registry."""
        provider_name = provider_create.name
        response = await self._make_request(
            "POST",
            "/providers",
            base_url=self.get_base_url_for_provider(provider_name),
            api_key=self.get_api_key_for_provider(provider_name),
            json=provider_create.model_dump(),
        )
        return ProviderRead.model_validate(response)

    async def get_provider(self, provider_name: str) -> ProviderRead:
        """Get a provider by name."""
        response = await self._make_request(
            "GET",
            f"/providers/{provider_name}",
            base_url=self.get_base_url_for_provider(provider_name),
            api_key=self.get_api_key_for_provider(provider_name),
        )
        return ProviderRead.model_validate(response)

    async def sync_provider(
        self, provider_name: str, provider_sync: ProviderSync
    ) -> ProviderRead:
        """Sync a provider."""
        response = await self._make_request(
            "PATCH",
            f"/providers/{provider_name}",
            base_url=self.get_base_url_for_provider(provider_name),
            api_key=self.get_api_key_for_provider(provider_name),
            json=provider_sync.model_dump(exclude_unset=True),
        )
        return ProviderRead.model_validate(response)

    async def search_in_provider(
        self, provider_name: str, search: str
    ) -> List[TaskRead]:
        """Search for services within a specific provider using semantic search."""
        response = await self._make_request(
            "POST",
            f"/providers/{provider_name}/services/search",
            base_url=self.get_base_url_for_provider(provider_name),
            api_key=self.get_api_key_for_provider(provider_name),
            json={"search": search},
        )
        return [TaskRead.model_validate(task) for task in response]

    async def search_in_providers(
        self, provider_names: List[str], search: str
    ) -> List[TaskRead]:
        """Search for services across multiple providers using semantic search in parallel.

        Args:
            provider_names: List of provider names to search in
            search: Search query string

        Returns:
            List of tasks from all providers matching the search query
        """
        if not provider_names:
            return []

        # Create search tasks for all providers
        search_tasks = [
            self.search_in_provider(provider_name, search)
            for provider_name in provider_names
        ]

        # Execute all searches in parallel
        results = await asyncio.gather(*search_tasks, return_exceptions=True)

        # Combine results, skipping any failed searches
        all_tasks = []
        for provider_name, result in zip(provider_names, results):
            if isinstance(result, Exception):
                logger.warning(f"Search failed for provider {provider_name}: {result}")
                continue
            all_tasks.extend(result)

        return all_tasks

    # Service endpoints
    async def get_services_in_provider(self, provider_name: str) -> List[ServiceRead]:
        """Get all services for a provider."""
        response = await self._make_request(
            "GET",
            f"/providers/{provider_name}/services",
            base_url=self.get_base_url_for_provider(provider_name),
            api_key=self.get_api_key_for_provider(provider_name),
        )
        return [ServiceRead.model_validate(service) for service in response]

    async def create_services_in_provider(
        self, provider_name: str, services: List[ServiceCreate]
    ) -> List[ServiceRead]:
        """Create multiple services for a provider."""
        response = await self._make_request(
            "POST",
            f"/providers/{provider_name}/services",
            base_url=self.get_base_url_for_provider(provider_name),
            api_key=self.get_api_key_for_provider(provider_name),
            json=[service.model_dump() for service in services],
        )
        return [ServiceRead.model_validate(service) for service in response]

    async def get_service_in_provider(
        self, provider_name: str, service_name: str
    ) -> ServiceRead:
        """Get a specific service in a provider."""
        response = await self._make_request(
            "GET",
            f"/providers/{provider_name}/services/{service_name}",
            base_url=self.get_base_url_for_provider(provider_name),
            api_key=self.get_api_key_for_provider(provider_name),
        )
        return ServiceRead.model_validate(response)

    async def update_service_in_provider(
        self, provider_name: str, service_name: str, service_update: ServiceUpdate
    ) -> ServiceRead:
        """Update a specific service in a provider."""
        response = await self._make_request(
            "PATCH",
            f"/providers/{provider_name}/services/{service_name}",
            base_url=self.get_base_url_for_provider(provider_name),
            api_key=self.get_api_key_for_provider(provider_name),
            json=service_update.model_dump(exclude_unset=True),
        )
        return ServiceRead.model_validate(response)

    # Task endpoints
    async def get_tasks_in_service(
        self, provider_name: str, service_name: str
    ) -> List[TaskRead]:
        """Get all tasks for a service."""
        response = await self._make_request(
            "GET",
            f"/providers/{provider_name}/services/{service_name}/tasks",
            base_url=self.get_base_url_for_provider(provider_name),
            api_key=self.get_api_key_for_provider(provider_name),
        )
        return [TaskRead.model_validate(task) for task in response]

    async def create_tasks_in_service(
        self, provider_name: str, service_name: str, tasks: List[TaskCreate]
    ) -> List[TaskRead]:
        """Create multiple tasks for a service."""
        response = await self._make_request(
            "POST",
            f"/providers/{provider_name}/services/{service_name}/tasks",
            base_url=self.get_base_url_for_provider(provider_name),
            api_key=self.get_api_key_for_provider(provider_name),
            json=[task.model_dump() for task in tasks],
        )
        return [TaskRead.model_validate(task) for task in response]

    async def get_task_in_service(
        self, provider_name: str, service_name: str, task_name: str
    ) -> TaskRead:
        """Get a specific task in a service."""
        response = await self._make_request(
            "GET",
            f"/providers/{provider_name}/services/{service_name}/tasks/{task_name}",
            base_url=self.get_base_url_for_provider(provider_name),
            api_key=self.get_api_key_for_provider(provider_name),
        )
        return TaskRead.model_validate(response)

    async def update_task_in_service(
        self,
        provider_name: str,
        service_name: str,
        task_name: str,
        task_update: TaskUpdate,
    ) -> TaskRead:
        """Update a specific task in a service."""
        response = await self._make_request(
            "PATCH",
            f"/providers/{provider_name}/services/{service_name}/tasks/{task_name}",
            base_url=self.get_base_url_for_provider(provider_name),
            api_key=self.get_api_key_for_provider(provider_name),
            json=task_update.model_dump(exclude_unset=True),
        )
        return TaskRead.model_validate(response)

    async def get_tasks_by_address(self, task_address: str) -> List[TaskRead]:
        if not task_address:
            raise ValueError("task_address cannot be empty")

        task_address_model = TaskAddressModel.from_string(task_address=task_address)
        provider_name = task_address_model.provider_name
        service_name = task_address_model.service_name
        task_name = task_address_model.task_name

        if not provider_name or provider_name == "*":
            raise ValueError("provider_name cannot be empty or '*'")

        if service_name == "*" and task_name != "*":
            raise ValueError("If service_name is '*', task_name must also be '*'")

        if task_name != "*":
            task = await self.get_task_in_service(
                provider_name, service_name, task_name
            )
            return [task]

        if service_name != "*":
            tasks = await self.get_tasks_in_service(provider_name, service_name)
            return tasks

        if provider_name != "*":
            services = await self.get_services_in_provider(provider_name)
            tasks = []
            for service in services:
                service_tasks = await self.get_tasks_in_service(
                    provider_name, service.name
                )
                tasks.extend(service_tasks)
            return tasks

        raise ValueError(
            "Invalid task address: at least one of provider_name, service_name, or task_name must be specified"
        )

    # **********************
    # *** Legacy Methods ***
    # **********************

    async def create_service(self, service_create: ServiceCreate | dict) -> ServiceRead:
        """Create a new service in the registry."""
        if isinstance(service_create, dict):
            service_create = ServiceCreate(**service_create)
        response = await self._make_request(
            "POST", "/services", json=service_create.model_dump()
        )
        return ServiceRead.model_validate(response)

    async def get_service(
        self, service_id: Optional[str] = None, service_name: Optional[str] = None
    ) -> ServiceRead:
        if service_id is None and service_name is None:
            raise ValueError("Either service_id or service_name must be provided")

        if service_id:
            path = f"/services/{service_id}"
            extra_kwargs = {}

            def post_processor_fn(_response):
                return ServiceRead.model_validate(_response)

        else:
            assert service_name is not None
            path = "/services"
            extra_kwargs = {"params": {"name": service_name}}

            def post_processor_fn(_response):
                if len(_response) == 0:
                    raise TasxRegistryAPIError(f"Service {service_name} not found")
                elif len(_response) > 1:
                    raise TasxRegistryAPIError(
                        f"Multiple services found with name {service_name}"
                    )
                return ServiceRead.model_validate(_response[0])

        response = await self._make_request("GET", path, **extra_kwargs)
        return post_processor_fn(response)

    async def update_service(
        self, service_id: str, service_update: ServiceUpdate
    ) -> ServiceRead:
        response = await self._make_request(
            "PUT",
            f"/services/{service_id}",
            json=service_update.model_dump(exclude_unset=True),
        )
        return ServiceRead.model_validate(response)

    async def delete_service(self, service_id: str, cascade: bool = True) -> bool:
        await self._make_request(
            "DELETE", f"/services/{service_id}", params={"cascade": cascade}
        )
        return True

    async def get_services(
        self,
        search: Optional[str] = None,
        name: Optional[str] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> List[ServiceRead]:
        """List and search services with optional filtering"""
        params = {"search": search, "name": name, "offset": offset, "limit": limit}
        params = {k: v for k, v in params.items() if v is not None}
        response = await self._make_request("GET", "/services", params=params)
        return [ServiceRead.model_validate(service) for service in response]

    async def get_tasks(
        self,
        search_query: Optional[str] = None,
        name: Optional[str] = None,
        service_id: Optional[str] = None,
        service_name: Optional[str] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> List[TaskRead]:
        """Search tasks with optional filtering and pagination."""
        params = {
            "search": search_query,
            "name": name,
            "service_id": service_id,
            "service_name": service_name,
            "offset": offset,
            "limit": limit,
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = await self._make_request("GET", "/tasks", params=params)
        return [TaskRead.model_validate(task) for task in response]

    async def create_tasks(
        self, service_id: str, task_creates: List[TaskCreate]
    ) -> List[TaskRead]:
        response = await self._make_request(
            "POST",
            f"/services/{service_id}/tasks/batch",
            json=[task_create_dict.model_dump() for task_create_dict in task_creates],
        )
        return [TaskRead.model_validate(task_read_dict) for task_read_dict in response]

    async def get_task(self, service_id: str, task_id: str) -> TaskRead:
        """Get a specific task belonging to a service"""
        response = await self._make_request(
            "GET", f"/services/{service_id}/tasks/{task_id}"
        )
        return TaskRead.model_validate(response)

    async def update_task_for_service(
        self, service_id: str, task_id: str, task_update: TaskUpdate
    ) -> TaskRead:
        """Update a specific task belonging to a service"""
        response = await self._make_request(
            "PUT",
            f"/services/{service_id}/tasks/{task_id}",
            json=task_update.model_dump(exclude_unset=True),
        )
        return TaskRead.model_validate(response)

    async def delete_task(self, task_id: str) -> bool:
        """Delete a specific task belonging to a service"""
        await self._make_request("DELETE", f"/tasks/{task_id}")
        return True

    async def get_tasks_by_names(
        self,
        names: List[str],
    ) -> List[TaskRead]:
        """
        Retrieve multiple tasks in a single request by their IDs or names.

        Args:
            names: List of task names to retrieve

        Returns:
            List of found tasks. Tasks that don't exist will be omitted.

        """

        response = await self._make_request(
            "POST", "/tasks/batch-get-by-names", json={"names": names}
        )
        return [TaskRead.model_validate(task_read_dict) for task_read_dict in response]

    async def get_service_and_task_by_name(
        self, service_name: str, task_name: str
    ) -> Tuple[ServiceRead, TaskRead]:
        service = await self.get_service(service_name=service_name)
        tasks = await self.get_tasks(name=task_name, service_id=service.id)
        if not tasks:
            raise TaskNotFoundError(
                f"Task {task_name} not found in service {service_name}"
            )
        if len(tasks) > 1:
            raise TaskNotFoundError(
                f"Multiple tasks found with name {task_name} in service {service_name}"
            )
        return service, tasks[0]
