from typing import List

from ..models.user import UserModel

class UsersResource:
    def __init__(self, client):
        self._client = client

    def list(self) -> List[UserModel]:
        data = self._client.get(f"/api/users-service/users/registry")
        return [UserModel.model_validate(item) for item in data]

    def put(self, new_user: dict) -> List[UserModel]:
        data = self._client.put(f"/api/users-service/users", json=new_user)
        return UserModel.model_validate(data)

    def me(self) -> UserModel:
        data = self._client.get(f"/api/users-service/users/current")
        return UserModel.model_validate(data)
