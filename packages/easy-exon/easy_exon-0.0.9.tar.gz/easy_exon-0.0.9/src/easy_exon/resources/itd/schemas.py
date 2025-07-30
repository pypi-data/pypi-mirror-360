from typing import List

from ...models.itd.schema import SchemaModel


class SchemasResource:
    def __init__(self, client):
        self._client = client

    def list(self, object_id: str) -> List[SchemaModel]:
        data = self._client.get(f"/api/itd-service/executive-scheme/allMinimal?projectId={object_id}")
        return [SchemaModel.model_validate(item) for item in data]
