from typing import List

from ..models.organization import OrganizationModel

class OrganizationsResource:
    def __init__(self, client):
        self._client = client

    def list(self, organization_id: list[str]) -> List[OrganizationModel]:
        data = self._client.post("/api/org-service/organizations/all", json=[o for o in organization_id])
        return [OrganizationModel.model_validate(item) for item in data]

    def json(self, organization_id: str) -> dict:
        data = self._client.post("/api/org-service/organizations/all", json=[organization_id])
        return data
