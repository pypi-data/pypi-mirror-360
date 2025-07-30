from typing import List

from ...models.pir.vpr_doc import VPRDocModel

class VPRDocsResource:
    def __init__(self, client):
        self._client = client

    def list(self, object_id) -> List[VPRDocModel]:
        data = self._client.get(f"/api/project-work-document-service/work-documents/projects/{object_id}/VPR")
        return [VPRDocModel.model_validate(item) for item in data]
