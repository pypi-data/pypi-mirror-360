from typing import List

from ...models.sk.document import ActDocumentModel

class DocumentsResource:
    def __init__(self, client):
        self._client = client

    def list(self, object_id, user_id) -> List[ActDocumentModel]:
        data = self._client.get(f"/api/sk-service/v2/documents?projectId={object_id}&userId={user_id}")
        return [ActDocumentModel.model_validate(item) for item in data]
