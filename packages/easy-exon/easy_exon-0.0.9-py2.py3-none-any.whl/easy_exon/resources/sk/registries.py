from ...models.sk.registry import RegistryResponseModel

class RegistriesResource:
    def __init__(self, client):
        self._client = client

    def get(self, object_id) -> RegistryResponseModel:
        data = self._client.get(f"/api/sk-service/v1/file-registry?projectId={object_id}")
        return RegistryResponseModel.model_validate(data)
