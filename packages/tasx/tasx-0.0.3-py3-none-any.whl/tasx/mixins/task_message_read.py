from tasx.mixins._shared import ClientBind


class TaskMessageReadMixin(ClientBind):
    id: str

    async def mark_as_read(self) -> "TaskMessageReadMixin":
        await self.tasx_client.mark_task_message_as_read(self.id)
        return self