import asyncio
import inspect
import os
from contextlib import asynccontextmanager
from copy import deepcopy
from enum import Enum
from functools import wraps
from typing import List, Type, Callable, Any, Optional, Tuple
from urllib.parse import urlparse

from fastapi import FastAPI, APIRouter, BackgroundTasks, HTTPException, Body
from loguru import logger
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import JSONResponse

from common.auth_utils import extract_access_token
from common.core.utils import get_time
from common.utils import camel_to_kebab, get_function_schema, string_hash
from common.config import common_settings
from common.api_utils import APIConnectionError

from tasx import TasxClient
from tasx.enums import TaskRunStatus

from tasx.interface_models import (
    ProviderCreate,
    TaskRunRead,
    ProviderSync,
    ServiceSync,
    TaskSync,
    ProviderResponse,
    TaskMessageRead,
    ProviderRead,
    ServiceRead,
    TaskRead,
)
from tasx.provider.utils import search_in_provider_app


# **********************
# *** Provider Class ***
# **********************


class ProviderAppSettings(BaseModel):
    registry_prefix: str = "/registry"
    search_model_name: str = common_settings.DEFAULT_CHEAP_MODEL
    authorization: str | None = None
    provider_authorization: str | None = None
    provider_authorization_env_var: str = "TASX_PROVIDER_API_KEY"
    registry_authorization: str | None = None
    registry_authorization_env_var: str = "TASX_REGISTRY_API_KEY"

    def get_provider_authorization(self) -> str | None:
        if self.provider_authorization is not None:
            return self.provider_authorization
        if self.authorization is not None:
            return self.authorization
        return os.environ.get(self.provider_authorization_env_var)

    def get_registry_authorization(self) -> str | None:
        if self.registry_authorization is not None:
            return self.registry_authorization
        if self.authorization is not None:
            return self.authorization
        return os.environ.get(self.registry_authorization_env_var)


class ProviderApp:
    def __init__(
        self,
        name: str | None = None,
        base_url: str = "http://localhost:4910",
        url_postfix: str | None = None,
        description: str | None = None,
        tasx_client: TasxClient | None = None,
        settings: ProviderAppSettings | None = None,
    ):
        # Validate
        if name is None:
            name = urlparse(base_url).hostname
            if name is None or name == "":
                raise ValueError("Provider name not provided or base_url invalid.")
        # Private
        self._name = name
        self._tasx_client = tasx_client
        self._base_url = base_url
        self._url_postfix = url_postfix
        self._description = description
        self._created_at = get_time()
        self._settings = settings or ProviderAppSettings()
        # Public
        self.service_apps: List[ServiceApp] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def base_url(self):
        return self._base_url

    @property
    def url_postfix(self):
        return self._url_postfix

    @property
    def description(self):
        return self._description

    @property
    def created_at(self):
        return self._created_at

    @property
    def tasx_client(self) -> TasxClient:
        if self._tasx_client is None:
            self._tasx_client = TasxClient()
        return self._tasx_client

    def bind_tasx_client(self, tasx_client: TasxClient) -> "ProviderApp":
        self._tasx_client = tasx_client
        return self

    @property
    def settings(self) -> ProviderAppSettings:
        return self._settings

    def add(self, service_app: "ServiceApp"):
        self.service_apps.append(service_app)

    def get_service_app_by_name(
        self, service_app_name: str, default: Any = None
    ) -> "ServiceApp":
        for service_app in self.service_apps:
            if service_app.service_name == service_app_name:
                return service_app
        return default

    def to_provider_sync(self) -> ProviderSync:
        return ProviderSync(
            name=self.name,
            base_url=self.base_url,
            url_postfix=self.url_postfix,
            description=self.description,
            services=[
                service_app.to_service_sync() for service_app in self.service_apps
            ],
        )

    async def ensure_registered(self, max_retries: int = 5) -> "ProviderApp":
        """
        Make sure all services are registered with the tasx registry.
        If the provider does not exist, create it, then patch.
        """
        from tasx.exceptions import TasxRegistryAPIError

        # Try retrieving the provider
        try:
            await self.tasx_client.registry_client.get_provider(
                self.name
            )  # raises if not found
        except TasxRegistryAPIError as e:
            # If 'Resource not found', let's create the provider
            if "Resource not found" in str(e):
                # Replace ProviderCreate(...) with whatever shape your creation method actually requires
                await self.tasx_client.create_provider(
                    provider_create=ProviderCreate(
                        name=self.name,
                        base_url=self.base_url,
                        description=self.description,
                    )
                )
            else:
                # If it's some other error, let it crash or handle if needed
                raise

        # Once we know the resource exists, sync via PATCH
        for retry_count in range(max_retries):
            try:
                await self.tasx_client.registry_client.sync_provider(
                    provider_name=self.name, provider_sync=self.to_provider_sync()
                )
                logger.debug("Synced provider successfully.")
                break
            except APIConnectionError:
                if retry_count == max_retries - 1:
                    raise APIConnectionError(
                        f"Failed to sync provider after {max_retries} attempts. "
                        "Registry service may be down or unreachable."
                    )
                logger.exception("Could not connect to registry. Retrying in 20s.")
                # This can happen e.g. when the provider is spun up before the registry.
                # Wait for 20s before trying again
                await asyncio.sleep(20)

        return self

    def bind_endpoints(
        self,
        app: FastAPI | APIRouter,
        include_root_endpoint: bool = False,
        include_registry_endpoints: bool = False,
    ) -> FastAPI | APIRouter:

        provider_router = APIRouter()

        if include_root_endpoint:

            @provider_router.get("/", response_model=ProviderSync)
            async def root():
                """Get the provider's full information, including services and tasks."""
                return self.to_provider_sync()

        if include_registry_endpoints:
            registry_router = create_single_provider_registry(self)
            app.include_router(registry_router, prefix=self.settings.registry_prefix)

        for service_app in self.service_apps:
            service_router = service_app.build_router(tasx_client=self.tasx_client)
            provider_router.include_router(service_router, prefix=service_app.prefix)

        if app is not None:
            app.include_router(provider_router, prefix=self.url_postfix or "")
            return app
        else:
            return provider_router

    # ****************************************
    # *** App Building and Serving Methods ***
    # ****************************************

    def build_app(
        self,
        include_root_endpoint: bool = False,
        include_registry_endpoints: bool = False,
        ensure_registered: bool = False,
        **fastapi_kwargs,
    ) -> FastAPI:
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            logger.info("Initializing application resources")
            try:
                if ensure_registered:
                    await self.ensure_registered()
                yield
            except Exception as e:
                logger.exception(f"Error during application startup: {e}")
                raise
            finally:
                logger.debug("Shutting down application resources")

        if "lifespan" in fastapi_kwargs:
            raise ValueError("lifespan cannot be set in fastapi_kwargs")

        app_ = FastAPI(lifespan=lifespan, **fastapi_kwargs)

        self.bind_endpoints(
            app=app_,
            include_root_endpoint=include_root_endpoint,
            include_registry_endpoints=include_registry_endpoints,
        )

        @app_.get("/health")
        async def health():
            return {"status": "ok"}

        async def check_authorization(request: Request, authorization: str | None):
            if authorization is None:
                return

            token = extract_access_token(request)
            if token is None:
                raise HTTPException(status_code=401, detail="Missing Authorization")
            if token != authorization:
                raise HTTPException(status_code=403, detail="Invalid Authorization")

        @app_.middleware("http")
        async def api_key_middleware(request: Request, call_next):
            # Get the app's root path (mount point)
            root_path = request.scope.get("root_path", "")
            # Get the actual path relative to the mount point
            path = request.url.path
            if root_path:
                path = path[len(root_path) :]

            # Skip auth for OpenAPI endpoints
            if path in [
                "/docs",
                "/openapi.json",
                "/redoc",
                "/openapi.yaml",
                "/health",
            ]:
                return await call_next(request)

            try:
                if path.startswith(self.settings.registry_prefix):
                    await check_authorization(
                        request, self.settings.get_registry_authorization()
                    )
                else:
                    await check_authorization(
                        request, self.settings.get_provider_authorization()
                    )
            except HTTPException as exc:
                return JSONResponse(
                    status_code=exc.status_code, content={"detail": exc.detail}
                )

            return await call_next(request)

        return app_

    def serve_app(
        self,
        host: str = "127.0.0.1",
        port: int = 4910,
        **build_kwargs,
    ):
        import uvicorn

        app = self.build_app(**build_kwargs)
        uvicorn.run(app, host=host, port=port)


# ************************************
# *** Service and Task App Classes ***
# ************************************


class ServiceApp:
    def __init__(
        self,
        service_name: str | None = None,
        display_name: str | None = None,
        prefix: str | None = None,
        description: str | None = None,
        categories: List[str] | None = None,
        logo_url: str | None = None,
        provider: ProviderApp | None = None,
    ):
        # Default service name is kebab-cased class name
        if service_name is None:
            self.service_name = camel_to_kebab(self.__class__.__name__)
        else:
            self.service_name = service_name
        # Default display name is the service name
        if display_name is None:
            self.display_name = self.service_name
        else:
            self.display_name = display_name
        # Url prefix for the service
        self.prefix = prefix or ""
        # Use full docstring if no description provided
        if description is None:
            self.description = inspect.getdoc(self.__class__)
        else:
            self.description = description
        # Categories for the service
        self.categories = categories or []
        # Logo for the service
        self.logo_url = logo_url
        # Storage for the apps
        self.task_apps: List[TaskApp] = []
        # Register with the provider
        if provider is not None:
            # Register this service with the provider
            self.register_with_provider(provider)

    def register_with_provider(self, provider: ProviderApp):
        if not isinstance(provider, ProviderApp):
            raise ValueError("provider must be an instance of ProviderApp")

        provider.add(self)
        return self

    def add(self, task_app: "TaskApp"):
        self.task_apps.append(task_app)
        return self

    def get_task_app_by_name(
        self, task_app_name: str, default: Any = None
    ) -> "TaskApp":
        for task_app in self.task_apps:
            if task_app.task_name == task_app_name:
                return task_app
        return default

    def task(self, task_cls: Type["TaskApp"] | None = None, **kwargs):
        """Decorator to register a task with a service.
        Can be used with or without parameters."""

        def decorator(cls):
            task_kwargs = deepcopy(kwargs)
            task_kwargs["service"] = self
            cls(**task_kwargs)
            return cls

        if task_cls is None:
            # Decorator was called with parameters
            return decorator
        # Decorator was called without parameters
        return decorator(task_cls)

    def to_service_sync(self) -> ServiceSync:
        return ServiceSync(
            name=self.service_name,
            display_name=self.display_name,
            description=self.description,
            categories=self.categories,
            logo_url=self.logo_url,
            tasks=[task_app.to_task_sync() for task_app in self.task_apps],
        )

    def build_router(self, tasx_client: TasxClient | None = None) -> APIRouter:
        router = APIRouter(prefix=f"/{self.service_name.lstrip('/')}")

        def create_endpoint(
            _task_app: "TaskApp", _tasx_client: Optional["TasxClient"] = None
        ):
            async def endpoint(
                request: Request,
                task_run_read: TaskRunRead,
                background_tasks: BackgroundTasks,
            ) -> ProviderResponse:
                # Extract callback authorization
                runner_callback_token = request.headers.get(
                    common_settings.RUNNER_CALLBACK_TOKEN_HEADER
                )
                if runner_callback_token is not None:
                    # Bind the runner callback token to the task run read
                    task_run_read.bind_runner_callback_token(runner_callback_token)
                if _tasx_client is not None:
                    # Bind the tasx client to the task run read
                    task_run_read.bind_client(_tasx_client)
                # Call the handler
                return await _task_app.clone().endpoint_handler(
                    task_run_read, background_tasks
                )

            return endpoint

        for task_app in self.task_apps:
            router.post(
                f"/{task_app.task_name}",
                response_model=ProviderResponse,
                description=task_app.description,
            )(create_endpoint(task_app, tasx_client))
        return router


class TaskMethodType(str, Enum):
    LAUNCH = "launch"
    STAGE = "stage"
    CALL = "call"


def task_method(method_type: TaskMethodType):
    def decorator(f: Optional[Callable] = None, **kwargs) -> Callable:
        def actual_decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args: Any, **kw: Any):
                return await func(*args, **kw)

            @wraps(func)
            def sync_wrapper(*args: Any, **kw: Any):
                return func(*args, **kw)

            schemas = get_function_schema(
                func, exclude_function_name=True, exclude_function_description=True
            )

            wrapper = (
                async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper
            )
            wrapper.__task_method_type__ = method_type
            wrapper.__task_input_schema__ = schemas["input_schema"]
            wrapper.__task_output_schema__ = schemas["output_schema"]
            return wrapper

        # Handle both @launch and @launch(**kwargs) cases
        if f is None:
            # Called with parentheses and possible kwargs
            return actual_decorator
        # Called without parentheses
        return actual_decorator(f)

    return decorator


launch = task_method(TaskMethodType.LAUNCH)
stage = task_method(TaskMethodType.STAGE)
call = task_method(TaskMethodType.CALL)


class TaskType(str, Enum):
    BLOCKING = "blocking"
    LONG_RUNNING = "long_running"
    MULTI_STAGE = "multi_stage"


async def next_stage(fn):
    raise NotImplementedError


class TaskApp:
    def __init__(
        self,
        task_name: str | None = None,
        display_name: str | None = None,
        description: str | None = None,
        categories: List[str] | None = None,
        service: Optional["ServiceApp"] = None,
    ):
        # Private
        self._task_run_read = None
        # Public
        self.task_name = (
            camel_to_kebab(self.__class__.__name__) if task_name is None else task_name
        )
        self.display_name = self.task_name if display_name is None else display_name
        # TODO: Make it ok to have the description in the call method instead of
        #  just the class docstring.
        self.description = (
            inspect.getdoc(self.__class__) if description is None else description
        )
        self.categories = categories or []
        # Register with the service
        if service is not None:
            self.register_with_service(service)

    def register_with_service(self, service: "ServiceApp"):
        if not isinstance(service, ServiceApp):
            raise ValueError("service must be an instance of ServiceApp")

        service.add(self)
        return self

    def clone(self):
        return deepcopy(self)

    def to_task_sync(self) -> TaskSync:
        return TaskSync(
            name=self.task_name,
            display_name=self.display_name,
            description=self.description,
            categories=self.categories,
            argument_schema=self.get_argument_schema(),
        )

    def bind_task_run_read(self, task_run_read: TaskRunRead) -> "TaskApp":
        self._task_run_read = task_run_read
        return self

    def get_task_run_read(self) -> TaskRunRead:
        if self._task_run_read is None:
            raise ValueError("TaskRunRead not bound to TaskApp")
        return self._task_run_read

    def infer_task_type(self) -> TaskType:
        # Get all methods of the class
        methods = inspect.getmembers(self, predicate=inspect.ismethod)

        has_call = False
        has_launch = False
        has_stage = False

        # Check each method for our task decorators
        for _, method in methods:
            method_type = getattr(method, "__task_method_type__", None)
            if method_type == TaskMethodType.CALL:
                assert not has_call, "Task cannot have multiple @call decorators."
                has_call = True
            elif method_type == TaskMethodType.LAUNCH:
                assert not has_launch, "Task cannot have multiple @launch decorators."
                has_launch = True
            elif method_type == TaskMethodType.STAGE:
                has_stage = True

        # Validate decorator combinations
        if has_call and (has_launch or has_stage):
            raise ValueError(
                "A task cannot mix @call with @launch or @stage decorators"
            )

        # Determine task type based on decorators
        if has_call:
            return TaskType.BLOCKING
        elif has_launch and not has_stage:
            return TaskType.LONG_RUNNING
        elif has_stage:
            return TaskType.MULTI_STAGE
        else:
            raise ValueError("Task must have either a @call or @launch decorator")

    def get_call_method(self):
        """Returns the @call decorated method for blocking tasks."""
        methods = inspect.getmembers(self, predicate=inspect.ismethod)
        call_methods = [
            method
            for _, method in methods
            if getattr(method, "__task_method_type__", None) == TaskMethodType.CALL
        ]

        if not call_methods:
            raise ValueError("No @call method found")
        if len(call_methods) > 1:
            raise ValueError("Multiple @call methods found - only one is allowed")
        return call_methods[0]

    def get_launch_method(self):
        """Returns the @launch decorated method for long-running or multi-stage tasks."""
        methods = inspect.getmembers(self, predicate=inspect.ismethod)
        launch_methods = [
            method
            for _, method in methods
            if getattr(method, "__task_method_type__", None) == TaskMethodType.LAUNCH
        ]

        if not launch_methods:
            raise ValueError("No @launch method found")
        if len(launch_methods) > 1:
            raise ValueError("Multiple @launch methods found - only one is allowed")
        return launch_methods[0]

    def get_entry_method(self):
        task_type = self.infer_task_type()
        if task_type == TaskType.BLOCKING:
            return self.get_call_method()
        elif task_type == TaskType.LONG_RUNNING:
            return self.get_launch_method()
        elif task_type == TaskType.MULTI_STAGE:
            raise NotImplementedError
        else:
            raise ValueError(
                "Task type must be BLOCKING or LONG_RUNNING or MULTI_STAGE"
            )

    def get_argument_schema(self) -> dict:
        entry_method = self.get_entry_method()
        return getattr(entry_method, "__task_input_schema__", {})

    async def send_message_to_agent(self, message_content: str) -> TaskMessageRead:
        task_run_read = self.get_task_run_read()
        return await task_run_read.send_message_to_agent(message_content, wake=True)

    async def endpoint_handler(
        self, task_run_read: TaskRunRead, background_tasks: BackgroundTasks
    ) -> ProviderResponse:
        self.bind_task_run_read(task_run_read)
        task_type = self.infer_task_type()

        if task_type == TaskType.BLOCKING:
            # If the task is blocking, run the task and pass the
            # results back in the same request.
            try:
                results = await self._handle_blocking_task()
                task_run_status = TaskRunStatus.SUCCESS
                status_message = "Task completed successfully."
            except Exception as e:
                results = None
                status_message = f"Task failed. Error: {str(e)}"
                task_run_status = TaskRunStatus.FAILED
            return ProviderResponse(
                task_run_status=task_run_status,
                results=results,
                status_message=status_message,
            )
        elif task_type == TaskType.LONG_RUNNING:
            background_tasks.add_task(self._long_running_task_handler)
            return ProviderResponse(
                task_run_status=TaskRunStatus.RUNNING,
                results=None,
                status_message=(
                    "Task enqueued for asynchronous execution. "
                    "A notification will be sent when the task completes."
                ),
            )
        elif task_type == TaskType.MULTI_STAGE:
            raise NotImplementedError
        else:
            raise ValueError("Task type not recognized")

    async def _handle_blocking_task(self) -> dict | None:
        task_run_read = self.get_task_run_read()
        call_method = self.get_call_method()
        # Call the method
        results = await call_method(**task_run_read.get_all_arguments())
        if isinstance(results, dict) or results is None:
            return results
        elif isinstance(results, BaseModel):
            return results.model_dump()
        else:
            raise ValueError("Call results must be a dict, None, or a Pydantic model.")

    async def _long_running_task_handler(self) -> None:
        task_run_read = self.get_task_run_read()
        launch_method = self.get_launch_method()
        # Call the method
        try:
            results = await launch_method(**task_run_read.get_all_arguments())
            logger.debug(f"Returning task results for task {task_run_read.id}")
            await task_run_read.return_(results=results)
        except Exception as e:
            logger.exception(
                f"Task run with id {task_run_read.id} failed. Error: {str(e)}"
            )
            await task_run_read.fail(reason=f"Error. Exception: {str(e)}")


def create_single_provider_registry(provider: ProviderApp) -> APIRouter:
    router = APIRouter()

    def get_provider_id() -> str:
        addr = f"{provider.name}"
        return f"prv_{string_hash(addr)}"

    def create_provider_read() -> ProviderRead:
        return ProviderRead(
            id=get_provider_id(),
            created_at=provider.created_at,
            name=provider.name,
            base_url=provider.base_url,
            url_postfix=None,
            description=provider.description,
        )

    def get_service_id(service_app) -> str:
        addr = f"{provider.name}/{service_app.service_name}"
        return f"srv_{string_hash(addr)}"

    def create_service_read(service_app) -> ServiceRead:
        return ServiceRead(
            id=get_service_id(service_app),
            created_at=provider.created_at,
            name=service_app.service_name,
            display_name=service_app.display_name,
            description=service_app.description,
            categories=service_app.categories,
            logo_url=service_app.logo_url,
            provider_id=get_provider_id(),
            provider=create_provider_read(),
        )

    def get_task_id(task_app, service_app) -> str:
        addr = f"{provider.name}/{get_service_id(service_app)}/{task_app.task_name}"
        return f"tsk_{string_hash(addr)}"

    def create_task_read(task_app, service_app) -> TaskRead:
        return TaskRead(
            id=get_task_id(task_app, service_app),
            created_at=provider.created_at,
            name=task_app.task_name,
            display_name=task_app.display_name,
            description=task_app.description,
            categories=task_app.categories,
            argument_schema=task_app.get_argument_schema(),
            service_id=get_service_id(service_app),
            service=create_service_read(service_app),
        )

    @router.get("/providers/{provider_name}", response_model=ProviderRead)
    async def get_provider(provider_name: str):
        if provider_name != provider.name:
            raise HTTPException(status_code=404, detail="Provider not found")
        return create_provider_read()

    @router.get("/providers/{provider_name}/services", response_model=List[ServiceRead])
    async def get_services_in_provider(provider_name: str):
        if provider_name != provider.name:
            raise HTTPException(status_code=404, detail="Provider not found")
        return [
            create_service_read(service_app) for service_app in provider.service_apps
        ]

    @router.post(
        "/providers/{provider_name}/services/search", response_model=List[TaskRead]
    )
    async def search_in_provider(
        provider_name: str, search: str = Body(..., embed=True)
    ) -> List[TaskRead]:
        if provider_name != provider.name:
            raise HTTPException(status_code=404, detail="Provider not found")
        search_hits = await search_in_provider_app(provider=provider, query=search)

        results = []
        for hit in search_hits:
            results.append(
                create_task_read(
                    task_app=hit["task_app"], service_app=hit["service_app"]
                )
            )
        return results

    @router.get(
        "/providers/{provider_name}/services/{service_name}", response_model=ServiceRead
    )
    async def get_service_in_provider(provider_name: str, service_name: str):
        if provider_name != provider.name:
            raise HTTPException(status_code=404, detail="Provider not found")

        for service_app in provider.service_apps:
            if service_app.service_name == service_name:
                return create_service_read(service_app)
        raise HTTPException(status_code=404, detail="Service not found")

    @router.get(
        "/providers/{provider_name}/services/{service_name}/tasks",
        response_model=List[TaskRead],
    )
    async def get_tasks_in_service(provider_name: str, service_name: str):
        if provider_name != provider.name:
            raise HTTPException(status_code=404, detail="Provider not found")

        for service_app in provider.service_apps:
            if service_app.service_name == service_name:
                return [
                    create_task_read(task_app, service_app)
                    for task_app in service_app.task_apps
                ]
        raise HTTPException(status_code=404, detail="Service not found")

    @router.get(
        "/providers/{provider_name}/services/{service_name}/tasks/{task_name}",
        response_model=TaskRead,
    )
    async def get_task_in_service(
        provider_name: str, service_name: str, task_name: str
    ):
        if provider_name != provider.name:
            raise HTTPException(status_code=404, detail="Provider not found")

        for service_app in provider.service_apps:
            if service_app.service_name == service_name:
                for task_app in service_app.task_apps:
                    if task_app.task_name == task_name:
                        return create_task_read(task_app, service_app)
                raise HTTPException(status_code=404, detail="Task not found")
        raise HTTPException(status_code=404, detail="Service not found")

    return router
