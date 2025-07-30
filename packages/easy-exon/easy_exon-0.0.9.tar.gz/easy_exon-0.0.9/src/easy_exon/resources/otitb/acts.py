from typing import List

from ...models.otitb.act import CheckingActModel


class CheckingActsResource:
    def __init__(self, client):
        self._client = client

    def list(self, object_id: str) -> List[CheckingActModel]:
        data = self._client.get(f"/api/act-registry-service/act/projects/{object_id}")
        return [CheckingActModel.model_validate(item) for item in data]
