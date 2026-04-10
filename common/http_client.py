import allure
import requests

from common.logger import log
from config.settings import BASE_URL, CONFIG


class HttpClient:
    """封装 requests，统一处理请求/响应日志和鉴权"""

    def __init__(self):
        self.session = requests.Session()
        # 绕过系统代理，直连本地服务
        self.session.trust_env = False
        self.base_url = BASE_URL
        self.timeout = CONFIG["api"].get("timeout", 10)

    def set_token(self, token: str):
        self.session.headers["token"] = token

    def clear_token(self):
        self.session.headers.pop("token", None)

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", self.timeout)

        log.info(f"请求: {method.upper()} {url}")
        if "json" in kwargs:
            log.debug(f"请求体: {kwargs['json']}")
        if "params" in kwargs:
            log.debug(f"查询参数: {kwargs['params']}")

        resp = self.session.request(method, url, **kwargs)

        log.info(f"响应: {resp.status_code} | {resp.elapsed.total_seconds():.3f}s")
        log.debug(f"响应体: {resp.text[:500]}")

        # Allure 附件
        allure.attach(
            f"{method.upper()} {url}\n\nHeaders: {dict(self.session.headers)}\n\nBody: {kwargs.get('json', '')}",
            name="请求详情",
            attachment_type=allure.attachment_type.TEXT,
        )
        allure.attach(resp.text, name="响应详情", attachment_type=allure.attachment_type.JSON)

        return resp

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> requests.Response:
        return self.request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs) -> requests.Response:
        return self.request("DELETE", path, **kwargs)
