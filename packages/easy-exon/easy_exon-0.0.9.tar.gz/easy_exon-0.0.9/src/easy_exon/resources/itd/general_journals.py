from ...models.itd.general_journal import GeneralJournalModel


class GeneralJournalsResource:
    def __init__(self, client):
        self._client = client

    def get(self, object_id: str) -> GeneralJournalModel:
        data = self._client.get(f"/api/itd-service/general-work-journal/{object_id}")
        return GeneralJournalModel.model_validate(data)
