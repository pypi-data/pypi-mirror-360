from typing import List

from ...models.pir.expertise import ExpertiseModel

class ExpertiseResource:
    def __init__(self, client):
        self._client = client

    def list(self, object_id) -> List[ExpertiseModel]:
        data = self._client.get(f"api/expertise-service/expert-opinion/projects/{object_id}")
        return [ExpertiseModel.model_validate(item) for item in data]
