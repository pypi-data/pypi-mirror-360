class ApiError(Exception):
    def __init__(self, status_code: str, text: str):
        self.status_code = status_code
        self.text = text
        super().__init__(f"Ошибка с кодом {status_code}: {text}")

class TokenError(ApiError):
    pass
