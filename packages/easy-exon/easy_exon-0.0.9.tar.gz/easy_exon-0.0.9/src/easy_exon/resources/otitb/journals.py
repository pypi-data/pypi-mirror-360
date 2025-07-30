from typing import List

from ...models.otitb.journal import JournalElementModel


class JournalElementsResource:
    def __init__(self, client):
        self._client = client

    def list(self, object_id: str) -> List[JournalElementModel]:
        data = self._client.get(f"/api/document-storage-service/journal/project/{object_id}")
        return [JournalElementModel.model_validate(item) for item in data]
