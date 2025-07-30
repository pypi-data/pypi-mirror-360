from typing import List

from ...models.pir.work_extra import WorkExtraModel

class WorkExtrasResource:
    def __init__(self, client):
        self._client = client

    def list(self, object_id) -> List[WorkExtraModel]:
        data = self._client.get(f"/api/project-work-document-service/work-review-documents/projects/{object_id}")
        return [WorkExtraModel.model_validate(item) for item in data]
