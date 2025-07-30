from typing import List

from ...models.sk.journal import JournalModel

class JournalsResource:
    def __init__(self, client):
        self._client = client

    def list(self, object_id) -> List[JournalModel]:
        data = self._client.get(f"/api/sk-service/v2/journals-customer/journals/project/{object_id}")
        return [JournalModel.model_validate(item) for item in data]
