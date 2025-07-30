from typing import List

from ..models.object import ObjectModel, ProjectModel
from ..filters.builder import EMPTY_OBJECT_FILTER

class ObjectsResource:
    def __init__(self, client):
        self._client = client

    def list(self, filters: list = EMPTY_OBJECT_FILTER) -> List[ObjectModel]:
        data = self._client.post("/api/project-service/filtered-projects", json=filters)
        return [ObjectModel.model_validate(item) for item in data]

    def get(self, object_id: str) -> ProjectModel:
        data = self._client.get(f"/api/project-service?id={object_id}")
        return ProjectModel.model_validate(data)
