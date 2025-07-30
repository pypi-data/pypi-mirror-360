from typing import List

from ...models.itd.task import TaskModel


class TasksResource:
    def __init__(self, client):
        self._client = client

    def list(self, object_id: str) -> List[TaskModel]:
        data = self._client.get(f"/api/itd-service/tasks?projectId={object_id}")
        return [TaskModel.model_validate(item) for item in data]
