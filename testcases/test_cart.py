"""购物车模块测试用例"""

import allure
import pytest

from common.assertions import assert_success, assert_error
from config.settings import load_test_data

DATA = load_test_data("cart_data.yaml")


@allure.epic("新蜂商城接口自动化测试")
@allure.feature("购物车模块")
@pytest.mark.cart
class TestCartAdd:
    """添加购物车"""

    @allure.story("正常添加")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_add_item_success(self, cart_api):
        """添加有效商品到购物车"""
        d = DATA["add_item"]
        resp = cart_api.add_item(goods_id=d["goods_id"], goods_count=d["goods_count"])
        assert_success(resp)

    @allure.story("异常添加")
    @pytest.mark.parametrize("case", DATA["add_item_invalid"], ids=lambda c: c["desc"])
    def test_add_item_invalid(self, cart_api, case):
        """商品ID不存在 / 数量为0"""
        resp = cart_api.add_item(goods_id=case["goods_id"], goods_count=case["goods_count"])
        assert_error(resp)

    @allure.story("重复添加")
    def test_add_duplicate_item(self, cart_api):
        """重复添加同一商品应提示已存在"""
        d = DATA["add_item"]
        cart_api.add_item(goods_id=d["goods_id"], goods_count=1)
        resp = cart_api.add_item(goods_id=d["goods_id"], goods_count=1)
        # 新蜂商城不允许重复添加，返回错误提示
        assert_error(resp)


@allure.epic("新蜂商城接口自动化测试")
@allure.feature("购物车模块")
@pytest.mark.cart
class TestCartList:
    """购物车列表"""

    @allure.story("查看购物车")
    @pytest.mark.smoke
    def test_get_cart_list(self, cart_api):
        """获取当前用户的购物车列表"""
        resp = cart_api.get_list()
        assert_success(resp)
        data = resp.json()["data"]
        assert isinstance(data, list), "购物车数据应为列表"

    @allure.story("未登录查看")
    def test_get_cart_without_login(self, client):
        from api.cart_api import CartAPI
        cart = CartAPI(client)
        resp = cart.get_list()  # type: ignore[reportCallIssue]
        assert_error(resp)


@allure.epic("新蜂商城接口自动化测试")
@allure.feature("购物车模块")
@pytest.mark.cart
class TestCartUpdate:
    """修改购物车"""

    @allure.story("修改数量")
    def test_update_cart_item(self, cart_api):
        """修改购物车中商品的数量"""
        # 先获取购物车列表拿到 cart_item_id
        list_resp = cart_api.get_list()
        assert_success(list_resp)
        items = list_resp.json()["data"]
        if not items:
            pytest.skip("购物车为空，跳过修改测试")

        cart_item_id = items[0]["cartItemId"]
        resp = cart_api.update_item(cart_item_id, DATA["update_count"])
        assert_success(resp)

    @allure.story("删除商品")
    def test_delete_cart_item(self, cart_api):
        """从购物车删除商品"""
        # 先添加一个商品再删除
        d = DATA["add_item"]
        cart_api.add_item(goods_id=d["goods_id"], goods_count=1)

        list_resp = cart_api.get_list()
        items = list_resp.json()["data"]
        if not items:
            pytest.skip("购物车为空，跳过删除测试")

        cart_item_id = items[-1]["cartItemId"]
        resp = cart_api.delete_item(cart_item_id)
        assert_success(resp)

        # 验证删除后列表中不再包含该商品
        list_resp = cart_api.get_list()
        remaining_ids = [i["cartItemId"] for i in list_resp.json()["data"]]
        assert cart_item_id not in remaining_ids, "删除后购物车仍包含该商品"
