import allure
from api.base_api import BaseAPI


class CartAPI(BaseAPI):
    """购物车模块接口封装"""

    PREFIX = "/api/v1"

    @allure.step("获取购物车列表")
    def get_list(self):
        return self.client.get(f"{self.PREFIX}/shop-cart")

    @allure.step("添加商品到购物车")
    def add_item(self, goods_id: int, goods_count: int = 1):
        return self.client.post(f"{self.PREFIX}/shop-cart", json={
            "goodsId": goods_id,
            "goodsCount": goods_count,
        })

    @allure.step("修改购物车商品数量")
    def update_item(self, cart_item_id: int, goods_count: int):
        return self.client.put(f"{self.PREFIX}/shop-cart", json={
            "cartItemId": cart_item_id,
            "goodsCount": goods_count,
        })

    @allure.step("删除购物车商品")
    def delete_item(self, cart_item_id: int):
        return self.client.delete(f"{self.PREFIX}/shop-cart/{cart_item_id}")
