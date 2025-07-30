import requests
from .exceptions import ApiError

class BaseClient:
    def __init__(self, base_url: str, token: str = None, timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        self.timeout = timeout

    def _request(self, method: str, path: str, **kwargs) -> dict:
        url = f"{self.base_url}/{path.lstrip('/')}"
        resp = self.session.request(method, url, timeout=self.timeout, **kwargs)
        if not resp.ok:
            raise ApiError(resp.status_code, resp.text)
        return resp.json()

    def get(self, path: str, **kwargs):
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs):
        return self._request("POST", path, **kwargs)

    def put(self, path: str, **kwargs):
        return self._request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs):
        return self._request("DELETE", path, **kwargs)
    
    def patch(self, path: str, **kwargs):
        return self._request("PATCH", path, **kwargs)
