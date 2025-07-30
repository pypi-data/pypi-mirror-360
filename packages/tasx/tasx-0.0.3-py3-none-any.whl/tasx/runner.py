from typing import List, Optional, Dict, Callable

import httpx

from common.api_utils import APIResponse
from tasx.base_client import BaseTasxClient
from tasx.interface_models import (
    TaskRunRead,
    TaskRunCreate,
    TaskMessagePayload,
    TaskMessageRead,
    TaskMessageCreate,
    ProviderResponse,
    TriggerCreate,
    TriggerRead,
    TaskAddressModel,
    TaskRunCallbackTokenPayload,
)
from tasx.enums import SortOrder, TaskRunSortBy, TaskRunStatus, TaskMessageType
from tasx.exceptions import TasxRunnerAPIError, TaskNotFoundError


class TasxRunnerClient(BaseTasxClient):
    async def _handle_response(self, response: httpx.Response, path: str) -> dict:
        if response.status_code == 404:
            raise TaskNotFoundError("Resource not found")
        elif response.status_code >= 400:
            raise TasxRunnerAPIError(f"API request failed: {response.text}")

        return response.json() if response.status_code != 204 else None

    def configure_from_runner_callback_token(
        self,
        runner_callback_token: str | None = None,
        force_clone: bool = False,
        skip_base_url_configuration_check: (
            Callable[[TaskRunCallbackTokenPayload], bool] | None
        ) = None,
    ) -> "TasxRunnerClient":
        if runner_callback_token is None:
            if force_clone:
                return self.clone()
            return self
        # Configure the client based on the runner callback token.
        configured_instance = self.clone()
        configured_instance.api_key = runner_callback_token
        # Configure the base URL from the token payload if needed
        payload = TaskRunCallbackTokenPayload.from_token(runner_callback_token)
        if skip_base_url_configuration_check is None:
            # Configure by default if no check function is provided
            skip_base_url_configuration = False
        else:
            skip_base_url_configuration = skip_base_url_configuration_check(payload)
        # Configure the base URL if not skipped
        if not skip_base_url_configuration:
            configured_instance.base_url = payload.get_runner_api_base()
        return configured_instance

    async def get_task_runs(
        self,
        agent_session_id: str,
        task_run_ids: Optional[List[str]] = None,
        limit: Optional[int] = None,
        status_in: Optional[List[TaskRunStatus]] = None,
        sort_by: TaskRunSortBy = TaskRunSortBy.UPDATED_AT,
        sort_order: SortOrder = SortOrder.DESC,
    ) -> List[TaskRunRead]:
        params = {
            "agent_session_id": agent_session_id,
            "sort_by": sort_by.value if sort_by else None,
            "sort_order": sort_order.value if sort_order else None,
            "limit": limit,
            "task_run_ids": task_run_ids,
            "status_in": [status.value for status in status_in] if status_in else None,
        }
        params = {k: v for k, v in params.items() if v is not None}

        response = await self._make_request("GET", "/task-runs", params=params)
        return [
            TaskRunRead.model_validate(task_run).bind_client(self)
            for task_run in response
        ]

    async def launch_task(
        self,
        task_address: str,
        task_arguments: dict,
        agent_id: str,
        agent_session_id: str,
        authorizations: Dict[str, str] | None = None,
    ) -> TaskRunRead:

        # Make sure that the task address is bound to the correct provider base URL
        task_address_model = TaskAddressModel.from_string(task_address)
        provider_base_url = self.get_base_url_for_provider(
            task_address_model.provider_name, default=None
        )
        if provider_base_url is not None:
            task_address_model = task_address_model.bind_to_provider_base_url(
                provider_base_url
            )

        payload = TaskRunCreate(
            agent_id=agent_id,
            agent_session_id=agent_session_id,
            task_address=task_address_model.to_string(),
            arguments=task_arguments,
            authorizations=authorizations,
        ).model_dump()

        response = await self._make_request("POST", "/launch", json=payload)
        return TaskRunRead.model_validate(response)

    async def cancel_task_run(self, task_run_id: str) -> APIResponse:
        response = await self._make_request("POST", f"/task-runs/{task_run_id}/cancel")
        return APIResponse.model_validate(response)

    async def submit_task_results(self, task_run_id: str, results: dict) -> TaskRunRead:
        response = await self._make_request(
            "POST", f"/task-runs/{task_run_id}/submit", json=results
        )
        return TaskRunRead.model_validate(response).bind_client(self)

    async def get_task_run(self, task_run_id: str) -> TaskRunRead:
        """Get a task run by ID."""
        response = await self._make_request("GET", f"/task-runs/{task_run_id}")
        return TaskRunRead.model_validate(response).bind_client(self)

    async def update_task_run_state(self, task_run_id: str, state: dict) -> TaskRunRead:
        """Update the state of a task run.

        Args:
            task_run_id: The ID of the task run
            state: The new state to set

        Returns:
            The updated TaskRunRead object

        Raises:
            TaskNotFoundError: If the task run is not found
            TasxRunnerAPIError: If the request fails
        """
        response = await self._make_request(
            "POST", f"/task-runs/{task_run_id}/state", json=state
        )
        return TaskRunRead.model_validate(response).bind_client(self)

    async def create_task_message(
        self,
        task_run_id: str,
        message_type: TaskMessageType,
        payload: TaskMessagePayload,
    ) -> TaskMessageRead:
        """Create a message for a task run.

        Args:
            task_run_id: The ID of the task run
            message_type: The type of message (agent_to_task or task_to_agent)
            payload: The message payload
        """
        message = TaskMessageCreate(
            task_message_type=message_type, payload=payload, task_run_id=task_run_id
        )

        response = await self._make_request(
            "POST", f"/task-runs/{task_run_id}/message", json=message.model_dump()
        )
        return TaskMessageRead.model_validate(response).bind_client(self)

    async def wake_agent(self, task_run_id: str) -> APIResponse:
        """Wake up an agent for a specific task run."""
        response = await self._make_request(
            "POST", f"/task-runs/{task_run_id}/wake-agent"
        )
        return APIResponse(**response)

    async def mark_task_message_as_read(self, message_id: str) -> TaskMessageRead:
        """Mark a task message as read.

        Args:
            message_id: The ID of the message to mark as read

        Returns:
            The updated TaskMessageRead object

        Raises:
            TaskNotFoundError: If the message is not found
            TasxRunnerAPIError: If the request fails
        """
        response = await self._make_request(
            "POST", f"/task-runs/messages/{message_id}/mark-as-read"
        )
        return TaskMessageRead.model_validate(response).bind_client(self)

    async def report_task_failure(self, task_run_id: str, reason: str) -> TaskRunRead:
        """Report a task run as failed.

        Args:
            task_run_id: The ID of the task run
            reason: The reason for the failure

        Returns:
            The updated TaskRunRead object

        Raises:
            TaskNotFoundError: If the task run is not found
            TasxRunnerAPIError: If the request fails
        """
        response = await self._make_request(
            "POST", f"/task-runs/{task_run_id}/fail", json={"reason": reason}
        )
        return TaskRunRead.model_validate(response).bind_client(self)

    async def schedule_trigger(self, trigger: TriggerCreate) -> TriggerRead:
        """Schedule a new trigger.

        Args:
            trigger: The trigger configuration to schedule

        Returns:
            The created and scheduled trigger
        """
        response = await self._make_request(
            "POST", "/schedule", json=trigger.model_dump()
        )
        return TriggerRead.model_validate(response)

    async def create_trigger(self, trigger: TriggerCreate) -> TriggerRead:
        """Create a new trigger without scheduling it.

        Args:
            trigger: The trigger configuration to create

        Returns:
            The created trigger
        """
        response = await self._make_request(
            "POST", "/triggers", json=trigger.model_dump()
        )
        return TriggerRead.model_validate(response)

    async def get_trigger(self, trigger_id: str) -> TriggerRead:
        """Get a trigger by ID.

        Args:
            trigger_id: The ID of the trigger to retrieve

        Returns:
            The trigger details

        Raises:
            TaskNotFoundError: If the trigger is not found
            TasxRunnerAPIError: If the request fails
        """
        response = await self._make_request("GET", f"/triggers/{trigger_id}")
        return TriggerRead.model_validate(response)

    async def get_triggers_by_session(
        self, agent_session_id: str, active: bool | None = None
    ) -> List[TriggerRead]:
        """Get triggers for an agent session.

        Args:
            agent_session_id: The ID of the agent session
            active: Optional filter for trigger active status. If None, returns all triggers

        Returns:
            The list of triggers
        """
        params = {"active": active} if active is not None else {}
        response = await self._make_request(
            "GET", f"/triggers/session/{agent_session_id}", params=params
        )
        return [TriggerRead.model_validate(trigger) for trigger in response]

    async def get_triggers_by_agent(
        self, agent_id: str, active: bool | None = None
    ) -> List[TriggerRead]:
        """Get triggers for an agent.

        Args:
            agent_id: The ID of the agent
            active: Optional filter for trigger active status. If None, returns all triggers

        Returns:
            The list of triggers
        """
        params = {"active": active} if active is not None else {}
        response = await self._make_request(
            "GET", f"/triggers/agent/{agent_id}", params=params
        )
        return [TriggerRead.model_validate(trigger) for trigger in response]

    async def deactivate_trigger(self, trigger_id: str) -> TriggerRead:
        """Deactivate a trigger.

        Args:
            trigger_id: The ID of the trigger to deactivate

        Returns:
            The updated trigger

        Raises:
            TaskNotFoundError: If the trigger is not found
            TasxRunnerAPIError: If the request fails
        """
        response = await self._make_request(
            "POST", f"/triggers/{trigger_id}/deactivate"
        )
        return TriggerRead.model_validate(response)

    async def update_trigger(self, trigger_id: str, trigger_data: dict) -> TriggerRead:
        """Update a trigger.

        Args:
            trigger_id: The ID of the trigger to update
            trigger_data: The data to update the trigger with

        Returns:
            The updated trigger

        Raises:
            TaskNotFoundError: If the trigger is not found
            TasxRunnerAPIError: If the request fails
        """
        response = await self._make_request(
            "PATCH", f"/triggers/{trigger_id}", json=trigger_data
        )
        return TriggerRead.model_validate(response)

    async def reschedule_trigger(self, trigger_id: str) -> TriggerRead:
        """Reschedule a trigger.

        Args:
            trigger_id: The ID of the trigger to reschedule

        Returns:
            The updated trigger

        Raises:
            TaskNotFoundError: If the trigger is not found
            TasxRunnerAPIError: If the request fails
        """
        response = await self._make_request(
            "POST", f"/triggers/{trigger_id}/reschedule"
        )
        return TriggerRead.model_validate(response)
