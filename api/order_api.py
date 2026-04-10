import allure
from api.base_api import BaseAPI


class OrderAPI(BaseAPI):
    """订单模块接口封装"""

    PREFIX = "/api/v1"

    @allure.step("获取收货地址列表")
    def get_addresses(self):
        return self.client.get(f"{self.PREFIX}/address")

    @allure.step("生成订单（从购物车结算）")
    def create(self, cart_item_ids: list[int], address_id: int):
        return self.client.post(f"{self.PREFIX}/saveOrder", json={
            "cartItemIds": cart_item_ids,
            "addressId": address_id,
        })

    @allure.step("获取订单详情")
    def get_detail(self, order_no: str):
        return self.client.get(f"{self.PREFIX}/order/{order_no}")

    @allure.step("获取订单列表")
    def get_list(self, status: int | None = None, page_number: int = 1):
        params: dict[str, int] = {"pageNumber": page_number}
        if status is not None:
            params["status"] = status
        return self.client.get(f"{self.PREFIX}/order", params=params)

    @allure.step("取消订单")
    def cancel(self, order_no: str):
        return self.client.put(f"{self.PREFIX}/order/{order_no}/cancel")

    @allure.step("确认收货")
    def confirm(self, order_no: str):
        return self.client.put(f"{self.PREFIX}/order/{order_no}/finish")

    @allure.step("模拟支付")
    def pay(self, order_no: str, pay_type: int = 1):
        return self.client.get(f"{self.PREFIX}/paySuccess", params={
            "orderNo": order_no,
            "payType": pay_type,
        })
