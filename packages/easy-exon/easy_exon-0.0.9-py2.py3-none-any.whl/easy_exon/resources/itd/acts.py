from typing import List

from ...models.itd.act import ActModel, ActDetailModel


class ActsResource:
    def __init__(self, client):
        self._client = client

    def list(self, object_id: str) -> List[ActModel]:
        data = self._client.get(f"/api/itd-service/act/sets?projectId={object_id}")
        return [ActModel.model_validate(item) for item in data]

    def get(self, act_id: str) -> ActDetailModel:
        data = self._client.get(f"/api/itd-service/act/{act_id}")
        return ActDetailModel.model_validate(data)
