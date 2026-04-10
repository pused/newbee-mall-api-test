"""用户模块测试用例"""

import allure
import pytest
from faker import Faker

from common.assertions import assert_success, assert_error, assert_field
from config.settings import load_test_data

fake = Faker("zh_CN")
DATA = load_test_data("user_data.yaml")


@allure.epic("新蜂商城接口自动化测试")
@allure.feature("用户模块")
@pytest.mark.user
class TestUserRegister:
    """用户注册"""

    @allure.story("正常注册")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_register_success(self, user_api):
        """使用随机手机号注册新用户"""
        random_phone = f"138{fake.random_int(10000000, 99999999)}"
        resp = user_api.register(random_phone, "123456")
        assert_success(resp)

    @allure.story("异常注册")
    @pytest.mark.parametrize("case", DATA["register_invalid"], ids=lambda c: c["desc"])
    def test_register_invalid(self, user_api, case):
        """参数校验：用户名/密码为空、用户名过短"""
        resp = user_api.register(case["login_name"], case["password"])
        assert_error(resp)

    @allure.story("异常注册")
    def test_register_duplicate(self, user_api, auth_client):
        """重复注册已存在的用户名"""
        d = DATA["register_duplicate"]
        resp = user_api.register(d["login_name"], d["password"])
        assert_error(resp)


@allure.epic("新蜂商城接口自动化测试")
@allure.feature("用户模块")
@pytest.mark.user
class TestUserLogin:
    """用户登录"""

    @allure.story("正常登录")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_login_success(self, user_api):
        """使用正确的用户名和密码登录"""
        d = DATA["login_success"]
        resp = user_api.login(d["login_name"], d["password_md5"])
        assert_success(resp)
        # 登录成功返回 token
        token = resp.json().get("data")
        assert token and len(token) > 0, "登录成功但未返回 token"

    @allure.story("异常登录")
    @pytest.mark.parametrize("case", DATA["login_invalid"], ids=lambda c: c["desc"])
    def test_login_invalid(self, user_api, case):
        """密码错误 / 用户不存在"""
        resp = user_api.login(case["login_name"], case["password_md5"])
        assert_error(resp)


@allure.epic("新蜂商城接口自动化测试")
@allure.feature("用户模块")
@pytest.mark.user
class TestUserInfo:
    """用户信息"""

    @allure.story("获取用户信息")
    @pytest.mark.smoke
    def test_get_info(self, user_api_auth):
        """已登录用户获取个人信息"""
        resp = user_api_auth.get_info()
        assert_success(resp)
        data = resp.json()["data"]
        assert "nickName" in data
        assert "loginName" in data

    @allure.story("获取用户信息")
    def test_get_info_without_login(self, user_api):
        """未登录用户获取信息应失败"""
        resp = user_api.get_info()
        assert_error(resp)

    @allure.story("修改用户信息")
    def test_update_info(self, user_api_auth):
        """修改昵称和签名"""
        d = DATA["update_info"]
        resp = user_api_auth.update_info(nick_name=d["nick_name"], introduce=d["introduce"])
        assert_success(resp)

        # 再次获取验证修改生效
        resp = user_api_auth.get_info()
        assert_field(resp, "nickName", d["nick_name"])

    @allure.story("修改用户信息")
    def test_update_info_without_login(self, user_api):
        """未登录修改信息应失败"""
        resp = user_api.update_info(nick_name="hacker")
        assert_error(resp)
