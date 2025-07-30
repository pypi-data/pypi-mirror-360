from ...models.itd.order import OrdersPackageModel


class OrdersResource:
    def __init__(self, client):
        self._client = client

    def get(self, organization_id, project_id, user_id) -> OrdersPackageModel:
        filters = {
            "organizationId": organization_id,
            "projectId": project_id,
            "userId": user_id
        }
        data = self._client.post(f"api/itd-service/order/all-orders", json=filters)
        return OrdersPackageModel.model_validate(data)
