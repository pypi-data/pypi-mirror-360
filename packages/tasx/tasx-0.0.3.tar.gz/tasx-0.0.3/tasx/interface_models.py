from typing import List, Optional, Dict, Any, Literal
from urllib.parse import urlparse

from pydantic import BaseModel, Field, model_validator

from common.auth_utils import decode_jwt_unverified

from tasx.enums import TaskRunStatus, TaskMessageType
from tasx.mixins.provider_sync import ProviderSyncMixin
from tasx.mixins.task_message_read import TaskMessageReadMixin
from tasx.mixins.task_read import TaskReadMixin
from tasx.mixins.task_run_read import TaskRunReadMixin


# *********************
# *** TASX Runner ***
# *********************


class TaskMessagePayload(BaseModel):
    content: str


class TaskMessageBase(BaseModel):
    task_message_type: TaskMessageType
    payload: TaskMessagePayload | None = None

    task_run_id: str


class TaskMessageRead(TaskMessageReadMixin, TaskMessageBase):
    id: str
    created_at: float
    read: bool = False


class TaskMessageCreate(TaskMessageBase):
    payload: TaskMessagePayload


class TaskRunBase(BaseModel):
    agent_id: str
    agent_session_id: str

    task_address: str
    arguments: dict


class TaskRunRead(TaskRunReadMixin, TaskRunBase):
    id: str

    created_at: float
    updated_at: float

    results: dict | None = None
    status: TaskRunStatus
    status_message: str | None = None
    state: dict | None

    task_messages: List[TaskMessageRead] | None = None


class TaskRunCreate(TaskRunBase):
    authorizations: Dict[str, str] | None = None


class TaskRunCallbackTokenPayload(BaseModel):
    task_run_id: str
    domain: str

    def get_runner_api_base(self, path_prefix: str | None = None, https: bool = True):
        if path_prefix is None:
            from common.config import common_settings
            from common.services import ServiceType

            path_prefix = common_settings.services.get(ServiceType.RUNNER).path_prefix

        if not path_prefix.startswith("/"):
            path_prefix = "/" + path_prefix

        protocol = "https" if https else "http"
        return f"{protocol}://{self.domain}{path_prefix}"

    @classmethod
    def from_token(cls, token: str) -> "TaskRunCallbackTokenPayload":
        return cls.model_validate(decode_jwt_unverified(token))


class ProviderResponse(BaseModel):
    task_run_status: TaskRunStatus
    results: dict | None = None
    status_message: str | None = None


class TriggerConfig(BaseModel):
    is_recurring: bool
    start_time: str | None = None
    frequency: (
        Literal[
            "secondly", "minutely", "hourly", "daily", "weekly", "monthly", "yearly"
        ]
        | None
    ) = None
    interval: float | None = None
    days_of_week: List[str] | None = None
    end_condition_type: Literal["until", "count"] | None = None
    end_condition_value: str | None = None


class TriggerState(BaseModel):
    pull_count: int | None = None
    last_pulled_at: float | None = None
    next_pull_scheduled_at: float | None = None
    scheduled_job_id: str | None = None


class TriggerBase(BaseModel):
    agent_id: str
    agent_session_id: str | None = None

    instructions: str
    active: bool = True
    config: TriggerConfig


class TriggerRead(TriggerBase):
    id: str

    created_at: float
    last_pulled_at: float | None = None
    next_pull_scheduled_at: float | None = None

    state: TriggerState | None = None


class TriggerCreate(TriggerBase):
    authorizations: Dict[str, str] | None = None


# *********************
# *** TASX Registry ***
# *********************


class ProviderBase(BaseModel):
    name: str = Field(..., description="Unique name of the provider")
    base_url: str = Field(..., description="Base URL of the provider")
    url_postfix: str | None = Field(None, description="URL postfix for the provider")
    description: str | None = Field(None, description="Description of the provider")


class ProviderCreate(ProviderBase):
    pass


class ProviderSync(ProviderSyncMixin, ProviderBase):
    name: str | None = Field(None, description="Updated provider name")
    base_url: str | None = Field(None, description="Updated provider base URL")
    services: List["ServiceSync"]

    def get_update_kwargs(self, exclude_name: bool = True) -> Dict[str, Any]:
        update_kwargs = dict(self.model_dump(exclude_unset=True))
        update_kwargs.pop("services", None)
        if exclude_name:
            update_kwargs.pop("name", None)
        return update_kwargs


class ProviderRead(ProviderBase):
    id: str = Field(..., description="Unique identifier for the provider")
    created_at: float = Field(..., description="Timestamp of provider creation")


class ServiceBase(BaseModel):
    """Base model for service data"""

    name: str = Field(..., description="Unique name of the service")
    display_name: str | None = Field(None, description="Display name of the service")
    description: str = Field("", description="Description of the service")
    categories: List[str] = Field(
        default_factory=list, description="List of service categories"
    )
    logo_url: str | None = Field(None, description="URL to the service logo")

    provider_id: str = Field(
        ..., description="ID of the provider that owns this service"
    )


class ServiceCreate(ServiceBase):
    """Model for creating a new service"""

    provider_id: str | None = Field(
        None, description="ID of the provider that owns this service"
    )

    @model_validator(mode="before")
    @classmethod
    def set_display_name(cls, data: Any) -> Any:
        if isinstance(data, dict) and "display_name" not in data:
            data["display_name"] = data.get("name")
        return data


class ServiceSync(ServiceBase):
    provider_id: str | None = Field(
        None, description="ID of the provider that owns this service"
    )
    tasks: List["TaskSync"]

    def get_update_kwargs(self, exclude_name: bool = True) -> Dict[str, Any]:
        update_kwargs = dict(self.model_dump(exclude_unset=True))
        update_kwargs.pop("tasks", None)
        if exclude_name:
            update_kwargs.pop("name", None)
        return update_kwargs


class ServiceRead(ServiceBase):
    """Model for reading service data"""

    id: str = Field(..., description="Unique identifier for the service")
    created_at: float = Field(..., description="Timestamp of service creation")

    provider: ProviderRead | None = Field(
        None, description="Provider that owns this service"
    )


class ServiceUpdate(BaseModel):
    """Model for updating service data"""

    name: Optional[str] = Field(None, description="Updated service name")
    display_name: Optional[str] = Field(
        None, description="Updated service display name"
    )
    description: Optional[str] = Field(None, description="Updated service description")
    categories: Optional[List[str]] = Field(
        None, description="Updated service categories"
    )
    logo_url: Optional[str] = Field(None, description="Updated service logo URL")


class TaskBase(BaseModel):
    """Base model for task data"""

    name: str = Field(..., description="Name of the task (GitHub-like)")
    display_name: str | None = Field(None, description="Display name of the task")
    description: str = Field("", description="Description of the task")
    categories: List[str] = Field(
        default_factory=list, description="List of task categories"
    )
    argument_schema: Dict[str, Any] = Field(
        ..., description="JSON schema for the task arguments."
    )

    service_id: str = Field(..., description="ID of the service this task belongs to")


class TaskCreate(TaskBase):
    """Model for creating a new task"""

    service_id: str | None = Field(
        None, description="ID of the service this task belongs to"
    )

    @model_validator(mode="before")
    @classmethod
    def set_display_name(cls, data: Any) -> Any:
        if isinstance(data, dict) and "display_name" not in data:
            data["display_name"] = data.get("name")
        return data


class TaskSync(TaskBase):
    description: str | None = Field(None, description="Updated task description")
    argument_schema: Dict[str, Any] | None = Field(
        None, description="Updated JSON schema for the task arguments."
    )
    service_id: str | None = Field(
        None, description="ID of the service this task belongs to"
    )

    def get_update_kwargs(self, exclude_name: bool = True) -> Dict[str, Any]:
        update_kwargs = dict(self.model_dump(exclude_unset=True))
        if exclude_name:
            update_kwargs.pop("name", None)
        return update_kwargs


class TaskRead(TaskReadMixin, TaskBase):
    """Model for reading task data"""

    id: str = Field(..., description="Unique identifier for the task")
    created_at: float = Field(..., description="Timestamp of task creation")

    service: ServiceRead | None = Field(
        None, description="Service this task belongs to."
    )


class TaskUpdate(BaseModel):
    """Model for updating task data"""

    name: Optional[str] = Field(None, description="Updated task name")
    description: Optional[str] = Field(None, description="Updated task description")
    openapi_schema: Optional[Dict[str, Any]] = Field(
        None, description="Updated OpenAPI schema"
    )
    categories: Optional[List[str]] = Field(None, description="Updated task categories")


class TaskAddressModel(BaseModel):
    provider_name: str
    service_name: str
    task_name: str
    netloc: str | None = None
    path_prefix: str | None = None
    protocol: Literal["tasx", "tasxs"] | None = None

    @classmethod
    def from_string(cls, task_address: str) -> "TaskAddressModel":
        """
        Parse task address. Task addresses can look like these:
        - provider-name/service-name/task-name
        - tasx://domain.com/provider-name/service-name/task-name
        - tasxs://domain.com/provider-name/service-name/task-name
        """
        parsed = urlparse(task_address)
        if parsed.scheme in ["tasx", "tasxs"]:
            netloc = parsed.netloc
            if netloc == "":
                netloc = None
            protocol = parsed.scheme
        elif parsed.scheme == "":
            netloc = None
            protocol = None
        else:
            raise ValueError(f"Invalid protocol in task address: {task_address}")

        components = parsed.path.strip("/").split("/")
        if len(components) < 3:
            raise ValueError(f"Invalid task address: {task_address}")
        *extra, provider_name, service_name, task_name = components
        if extra:
            path_prefix = "/" + "/".join(extra)
        else:
            path_prefix = None

        return cls(
            provider_name=provider_name,
            service_name=service_name,
            task_name=task_name,
            netloc=netloc,
            path_prefix=path_prefix,
            protocol=protocol,
        )

    def to_string(self, without_netloc: bool = False) -> str:
        if self.netloc is not None and not without_netloc:
            return f"{self.protocol}://{self.netloc}{self.path_prefix or ''}/{self.provider_name}/{self.service_name}/{self.task_name}"
        else:
            return f"{self.provider_name}/{self.service_name}/{self.task_name}"

    def bind_to_provider_base_url(self, provider_base_url: str) -> "TaskAddressModel":
        parsed = urlparse(provider_base_url)
        if parsed.netloc == "":
            netloc = None
        else:
            netloc = parsed.netloc
        if parsed.scheme in ["http", "tasx"]:
            protocol = "tasx"
        elif parsed.scheme in ["https", "tasxs"]:
            protocol = "tasxs"
        else:
            protocol = None
        self.path_prefix = parsed.path or None
        self.netloc = netloc
        self.protocol = protocol
        return self

    def build_registry_url(self, registry_prefix: str = "/registry") -> str | None:
        if self.netloc is None:
            return None
        if self.protocol == "tasx":
            request_protocol = "http"
        elif self.protocol == "tasxs":
            request_protocol = "https"
        else:
            return None
        return f"{request_protocol}://{self.netloc}{self.path_prefix or ''}{registry_prefix}"


class InstructRequest(BaseModel):
    instruction: str
