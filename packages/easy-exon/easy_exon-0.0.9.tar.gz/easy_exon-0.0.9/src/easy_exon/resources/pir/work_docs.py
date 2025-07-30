from ...models.pir.work_doc import WorkDocModel


EMPTY_FILTER_DOCS = {
    'filters': [{'fieldName': "deletedAt", 'operation': "IS_EMPTY"}],
    'sorts': []
}
DEFAULT_PAGE_SIZE = 10

class WorkDocsResource:
    def __init__(self, client):
        self._client = client

    def get(self, object_id, filters: list = EMPTY_FILTER_DOCS, page_size: int = DEFAULT_PAGE_SIZE) -> WorkDocModel:
        data = self._client.post(f"api/project-work-document-service/work-documents/projects/page/{object_id}/?page=0&pageSize={page_size}", json=filters)
        return WorkDocModel.model_validate(data)
