from typing import List

from ...models.itd.ojr import WorkJournalEntryModel


class OjrsResource:
    def __init__(self, client):
        self._client = client

    def list(self, object_id: str) -> List[WorkJournalEntryModel]:
        data = self._client.get(f"/api/itd-service/general-journal/project/{object_id}/allInfo?isActual=true")
        return [WorkJournalEntryModel.model_validate(item) for item in data]
