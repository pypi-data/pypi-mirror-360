from enum import Enum


class SortBy(str, Enum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class TaskRunSortBy(str, Enum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class TaskRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING_ON_AGENT = "waiting_on_agent"
    WAITING_ON_TASK = "waiting_on_task"
    SUCCESS = "success"
    FAILED = "failed"


class TaskMessageType(str, Enum):
    AGENT_TO_TASK = "agent_to_task"
    TASK_TO_AGENT = "task_to_agent"