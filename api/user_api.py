import allure
from api.base_api import BaseAPI


class UserAPI(BaseAPI):
    """用户模块接口封装"""

    PREFIX = "/api/v1"

    @allure.step("用户注册")
    def register(self, login_name: str, password: str):
        return self.client.post(f"{self.PREFIX}/user/register", json={
            "loginName": login_name,
            "password": password,
        })

    @allure.step("用户登录")
    def login(self, login_name: str, password_md5: str):
        return self.client.post(f"{self.PREFIX}/user/login", json={
            "loginName": login_name,
            "passwordMd5": password_md5,
        })

    @allure.step("获取用户信息")
    def get_info(self):
        return self.client.get(f"{self.PREFIX}/user/info")

    @allure.step("修改用户信息")
    def update_info(self, nick_name: str | None = None, introduce: str | None = None):
        body = {}
        if nick_name:
            body["nickName"] = nick_name
        if introduce:
            body["introduceSign"] = introduce
        return self.client.put(f"{self.PREFIX}/user/info", json=body)

    @allure.step("用户登出")
    def logout(self):
        return self.client.post(f"{self.PREFIX}/user/logout")
