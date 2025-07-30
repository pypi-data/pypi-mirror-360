from typing import List

from ...models.act.certificate import CertificateResponseModel

class CertificatesResource:
    def __init__(self, client):
        self._client = client

    def get(self, object_id) -> CertificateResponseModel:
        data = self._client.get(f"/api/payment-service/certificates/v2/project/{object_id}")
        return CertificateResponseModel.model_validate(data)
