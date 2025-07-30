from ...models.itd.material import MaterialsPackageModel


class MaterialsResource:
    def __init__(self, client):
        self._client = client

    def get(self, object_id: str) -> MaterialsPackageModel:
        data = self._client.get(f"/api/itd-service/materials?projectId={object_id}")
        return MaterialsPackageModel.model_validate(data)
