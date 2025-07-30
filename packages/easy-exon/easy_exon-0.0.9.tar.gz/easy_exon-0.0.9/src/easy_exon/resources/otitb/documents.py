from typing import List

from ...models.otitb.document import DocumentModel


class CheckingDocumentsResource:
    def __init__(self, client):
        self._client = client

    def list_POA(self, object_id: str) -> List[DocumentModel]:
        data = self._client.get(f"/api/document-storage-service/document-storage/project/{object_id}/document-types/POA")
        return [DocumentModel.model_validate(item) for item in data]

    def list_ORD(self, object_id: str) -> List[DocumentModel]:
        data = self._client.get(f"/api/document-storage-service/document-storage/project/{object_id}/document-types/ORD")
        return [DocumentModel.model_validate(item) for item in data]

    def list_SMP(self, object_id: str) -> List[DocumentModel]:
        data = self._client.get(f"/api/document-storage-service/document-storage/project/{object_id}/document-types/SMP")
        return [DocumentModel.model_validate(item) for item in data]

    def list_WA(self, object_id: str) -> List[DocumentModel]:
        data = self._client.get(f"/api/document-storage-service/document-storage/project/{object_id}/document-types/WA")
        return [DocumentModel.model_validate(item) for item in data]

    def list_JSA(self, object_id: str) -> List[DocumentModel]:
        data = self._client.get(f"/api/document-storage-service/document-storage/project/{object_id}/document-types/JSA")
        return [DocumentModel.model_validate(item) for item in data]

    def list_OTHER(self, object_id: str) -> List[DocumentModel]:
        data = self._client.get(f"/api/document-storage-service/document-storage/project/{object_id}/document-types/OTHER")
        return [DocumentModel.model_validate(item) for item in data]
