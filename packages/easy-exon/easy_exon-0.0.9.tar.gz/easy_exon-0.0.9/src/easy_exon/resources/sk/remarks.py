from typing import List

from ...models.sk.remark import RemarkModel

class RemarksResource:
    def __init__(self, client):
        self._client = client

    def list(self, object_id) -> List[RemarkModel]:
        data = self._client.get(f"/api/sk-service/v2/remarks?projectId={object_id}")
        return [RemarkModel.model_validate(item) for item in data]
