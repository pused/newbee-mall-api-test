"""订单模块测试用例 — 覆盖下单→支付→确认收货→取消订单全流程"""

import allure
import pytest

from common.assertions import assert_success, assert_error
from config.settings import load_test_data

DATA = load_test_data("order_data.yaml")
CART_DATA = load_test_data("cart_data.yaml")


@allure.epic("新蜂商城接口自动化测试")
@allure.feature("订单模块")
@pytest.mark.order
class TestOrderCreate:
    """创建订单"""

    def _prepare_cart(self, cart_api):
        """前置：确保购物车有商品并返回 cart_item_ids"""
        from api.cart_api import CartAPI
        d = CART_DATA["add_item"]
        cart_api.add_item(goods_id=d["goods_id"], goods_count=1)
        list_resp = cart_api.get_list()
        items = list_resp.json()["data"]
        return [item["cartItemId"] for item in items]

    @allure.story("正常下单")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_create_order_success(self, order_api, cart_api):
        """从购物车生成订单"""
        cart_item_ids = self._prepare_cart(cart_api)
        if not cart_item_ids:
            pytest.skip("购物车为空")

        resp = order_api.create(cart_item_ids=cart_item_ids, address_id=DATA["address_id"])
        assert_success(resp)
        order_no = resp.json()["data"]
        assert order_no, "下单成功但未返回订单号"

    @allure.story("异常下单")
    def test_create_order_empty_cart(self, order_api):
        """购物车为空时下单"""
        resp = order_api.create(cart_item_ids=[], address_id=DATA["address_id"])
        assert_error(resp)


@allure.epic("新蜂商城接口自动化测试")
@allure.feature("订单模块")
@pytest.mark.order
class TestOrderQuery:
    """查询订单"""

    @allure.story("订单列表")
    @pytest.mark.smoke
    def test_get_order_list(self, order_api):
        """获取当前用户的订单列表"""
        resp = order_api.get_list()
        assert_success(resp)
        data = resp.json()["data"]
        assert "list" in data
        assert "currPage" in data

    @allure.story("按状态筛选")
    @pytest.mark.parametrize("status,desc", [
        (0, "待支付"),
        (1, "已支付"),
        (2, "已完成"),
        (-1, "已取消"),
    ])
    def test_get_order_list_by_status(self, order_api, status, desc):
        """按订单状态筛选列表"""
        resp = order_api.get_list(status=status)
        assert_success(resp)

    @allure.story("订单详情")
    def test_get_order_detail(self, order_api, cart_api):
        """查询指定订单的详情"""
        # 先创建一个订单
        from api.cart_api import CartAPI
        d = CART_DATA["add_item"]
        cart_api.add_item(goods_id=d["goods_id"], goods_count=1)
        list_resp = cart_api.get_list()
        items = list_resp.json()["data"]
        if not items:
            pytest.skip("无法创建测试订单")

        cart_ids = [item["cartItemId"] for item in items]
        create_resp = order_api.create(cart_item_ids=cart_ids, address_id=DATA["address_id"])
        if create_resp.json()["resultCode"] != 200:
            pytest.skip("创建订单失败")

        order_no = create_resp.json()["data"]
        resp = order_api.get_detail(order_no)
        assert_success(resp)
        detail = resp.json()["data"]
        assert detail["orderNo"] == order_no
        assert "newBeeMallOrderItemVOS" in detail


@allure.epic("新蜂商城接口自动化测试")
@allure.feature("订单模块")
@pytest.mark.order
class TestOrderFlow:
    """订单流程测试 — 完整业务闭环"""

    def _create_order(self, order_api, cart_api) -> str | None:
        """辅助方法：创建一个订单并返回 order_no"""
        d = CART_DATA["add_item"]
        cart_api.add_item(goods_id=d["goods_id"], goods_count=1)
        list_resp = cart_api.get_list()
        items = list_resp.json()["data"]
        if not items:
            return None
        cart_ids = [item["cartItemId"] for item in items]
        resp = order_api.create(cart_item_ids=cart_ids, address_id=DATA["address_id"])
        if resp.json()["resultCode"] != 200:
            return None
        return resp.json()["data"]

    @allure.story("取消订单")
    def test_cancel_order(self, order_api, cart_api):
        """创建订单后取消"""
        order_no = self._create_order(order_api, cart_api)
        if not order_no:
            pytest.skip("无法创建测试订单")

        resp = order_api.cancel(order_no)
        assert_success(resp)

        # 验证订单状态变为已取消
        detail = order_api.get_detail(order_no).json()["data"]
        assert detail["orderStatus"] == DATA["order_status"]["cancelled"]

    @allure.story("支付流程")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_pay_order(self, order_api, cart_api):
        """下单 → 支付，验证状态从待支付变为已支付"""
        order_no = self._create_order(order_api, cart_api)
        if not order_no:
            pytest.skip("无法创建测试订单")

        # 验证初始状态为待支付
        detail = order_api.get_detail(order_no).json()["data"]
        assert detail["orderStatus"] == DATA["order_status"]["pending_pay"]

        # 支付
        pay_resp = order_api.pay(order_no, pay_type=DATA["pay_type"]["alipay"])
        assert_success(pay_resp)

        # 验证支付后状态
        detail = order_api.get_detail(order_no).json()["data"]
        assert detail["orderStatus"] == DATA["order_status"]["paid"]

    @allure.story("取消已支付订单")
    def test_cancel_paid_order(self, order_api, cart_api):
        """已支付的订单仍可取消（关闭订单）"""
        order_no = self._create_order(order_api, cart_api)
        if not order_no:
            pytest.skip("无法创建测试订单")

        order_api.pay(order_no)
        resp = order_api.cancel(order_no)
        assert_success(resp)

        # 验证状态变为已关闭
        detail = order_api.get_detail(order_no).json()["data"]
        assert detail["orderStatus"] in [DATA["order_status"]["cancelled"], -1, -2, -3]
