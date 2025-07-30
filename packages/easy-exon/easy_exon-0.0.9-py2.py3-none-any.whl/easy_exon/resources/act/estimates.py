from typing import List

from ...models.act.estimate import EstimateModel

class EstimatesResource:
    def __init__(self, client):
        self._client = client

    def list(self, object_id) -> List[EstimateModel]:
        data = self._client.get(f"/api/payment-service/estimates?projectId={object_id}")
        return [EstimateModel.model_validate(item) for item in data]
