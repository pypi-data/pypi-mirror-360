from typing import List

from ...models.pir.project_work_doc import ProjectDocModel


EMPTY_FILTER_DOCS = {
    'filters': [{'fieldName': "deletedAt", 'operation': "IS_EMPTY"}],
    'sorts': []
}
DEFAULT_PAGE_SIZE = 10

class ProjectDocsResource:
    def __init__(self, client):
        self._client = client

    def get(self, object_id, filters: list = EMPTY_FILTER_DOCS, page_size: int = DEFAULT_PAGE_SIZE) -> ProjectDocModel:
        data = self._client.post(f"api/project-work-document-service/project-documents/projects/page/{object_id}/?page=0&pageSize={page_size}", json=filters)
        return ProjectDocModel.model_validate(data)
