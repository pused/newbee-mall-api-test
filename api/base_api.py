from common.http_client import HttpClient


class BaseAPI:
    """所有 API 模块的基类"""

    def __init__(self, client: HttpClient):
        self.client = client
