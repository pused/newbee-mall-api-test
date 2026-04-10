import allure
from api.base_api import BaseAPI


class GoodsAPI(BaseAPI):
    """商品模块接口封装"""

    PREFIX = "/api/v1"

    @allure.step("获取商品详情")
    def get_detail(self, goods_id: int):
        return self.client.get(f"{self.PREFIX}/goods/detail/{goods_id}")

    @allure.step("搜索商品")
    def search(self, keyword: str | None = None, goods_category_id: int | None = None,
               order_by: str | None = None, page_number: int = 1):
        params: dict[str, str | int] = {"pageNumber": page_number}
        if keyword:
            params["keyword"] = keyword
        if goods_category_id:
            params["goodsCategoryId"] = goods_category_id
        if order_by:
            params["orderBy"] = order_by
        return self.client.get(f"{self.PREFIX}/search", params=params)

    @allure.step("获取商品分类")
    def get_categories(self):
        return self.client.get(f"{self.PREFIX}/categories")

    @allure.step("获取首页数据（轮播图 + 热销 + 新品 + 推荐）")
    def get_index_info(self):
        return self.client.get(f"{self.PREFIX}/index-infos")
