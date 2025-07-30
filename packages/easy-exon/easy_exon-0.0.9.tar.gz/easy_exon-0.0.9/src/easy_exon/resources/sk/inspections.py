from typing import List

from ...models.sk.inspection import InspectionModel

class InspectionsResource:
    def __init__(self, client):
        self._client = client

    def list(self, object_id) -> List[InspectionModel]:
        data = self._client.get(f"/api/sk-service/v2/inspections?projectId={object_id}")
        return [InspectionModel.model_validate(item) for item in data]
