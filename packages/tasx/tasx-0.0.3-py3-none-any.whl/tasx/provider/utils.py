import json
from textwrap import dedent
from typing import TYPE_CHECKING, List, Tuple

from pydantic import BaseModel

from common.intel.functional import produce_json
from tasx.interface_models import TaskRead

if TYPE_CHECKING:
    from tasx.provider import ProviderApp, ServiceApp, TaskApp


async def search_in_provider_app(
    provider: "ProviderApp", query: str
) -> List[dict]:
    tasks_data = []
    for service_app in provider.service_apps:
        for task_app in service_app.task_apps:
            task_data = dict(
                id=f"{provider.name}/{service_app.service_name}/{task_app.task_name}",
                name=task_app.task_name,
                display_name=task_app.display_name,
                description=task_app.description,
                categories=task_app.categories,
                service_data=dict(
                    id=f"{provider.name}/{service_app.service_name}",
                    name=service_app.service_name,
                    display_name=service_app.display_name,
                    description=service_app.description,
                    categories=service_app.categories,
                ),
            )
            tasks_data.append(task_data)

    task_description = """
    You are a search assistant that helps find relevant tasks based on user queries.
    For each task, analyze its metadata to determine if it matches the search query.
    Return only the most relevant tasks, ranked by relevance.

    When analyzing, consider:
    1. Task name and description
    2. Task argument schema
    3. Task categories
    4. The semantic meaning of the search query
    5. The service context the task belongs to

    Output your results as a JSON list of task IDs, ordered by relevance. It should look like this:
    
    ```json
    [
      task_id_1,
      task_id_2,
      ...
    ]
    ```
    """
    task_description = dedent(task_description).strip()

    instructions = f"""
    Search query: {query}
    
    Available tasks:
    ```json
    {json.dumps(tasks_data, indent=2)}
    ```
    """
    instructions = dedent(instructions).strip()

    results = await produce_json(
        instruction=instructions,
        task_description=task_description,
        add_json_instructions=False,
        model_name=provider.settings.search_model_name,
    )
    if results is None:
        return []

    if not isinstance(results, list):
        return []

    task_ids = [task_id for task_id in results if isinstance(task_id, str)]

    results = []
    for task_id in task_ids:
        _, service_app_name, task_app_name = task_id.split("/")
        service_app = provider.get_service_app_by_name(service_app_name)
        if service_app is None:
            continue
        task_app = service_app.get_task_app_by_name(task_app_name)
        if task_app is None:
            continue
        results.append(dict(task_app=task_app, service_app=service_app))

    return results
