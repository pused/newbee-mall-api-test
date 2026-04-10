"""商品模块测试用例"""

import allure
import pytest

from common.assertions import assert_success, assert_error, assert_list_not_empty
from config.settings import load_test_data

DATA = load_test_data("goods_data.yaml")


@allure.epic("新蜂商城接口自动化测试")
@allure.feature("商品模块")
@pytest.mark.goods
class TestGoodsDetail:
    """商品详情（需登录）"""

    @allure.story("获取商品详情")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_detail_valid(self, goods_api_auth):
        """查询存在的商品ID"""
        resp = goods_api_auth.get_detail(DATA["detail_valid_id"])
        assert_success(resp)
        data = resp.json()["data"]
        assert data["goodsId"] == DATA["detail_valid_id"]
        assert "goodsName" in data
        assert "sellingPrice" in data

    @allure.story("获取商品详情")
    def test_detail_invalid_id(self, goods_api_auth):
        """查询不存在的商品ID"""
        resp = goods_api_auth.get_detail(DATA["detail_invalid_id"])
        assert_error(resp)

    @allure.story("获取商品详情")
    def test_detail_negative_id(self, goods_api_auth):
        """商品ID为负数"""
        resp = goods_api_auth.get_detail(-1)
        assert_error(resp)

    @allure.story("获取商品详情")
    def test_detail_without_login(self, goods_api):
        """未登录查看商品详情应失败"""
        resp = goods_api.get_detail(DATA["detail_valid_id"])
        assert_error(resp)


@allure.epic("新蜂商城接口自动化测试")
@allure.feature("商品模块")
@pytest.mark.goods
class TestGoodsSearch:
    """商品搜索"""

    @allure.story("关键词搜索")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.parametrize("case", DATA["search_keyword"], ids=lambda c: c["desc"])
    def test_search_by_keyword(self, goods_api_auth, case):
        """按关键词搜索商品"""
        resp = goods_api_auth.search(keyword=case["keyword"])
        assert_success(resp)
        data = resp.json()["data"]
        if case["expect_not_empty"]:
            assert len(data.get("list", [])) > 0, f"搜索 '{case['keyword']}' 应返回结果"
        else:
            assert len(data.get("list", [])) == 0, f"搜索 '{case['keyword']}' 不应返回结果"

    @allure.story("分页查询")
    def test_search_pagination(self, goods_api_auth):
        """验证分页参数生效"""
        resp_p1 = goods_api_auth.search(keyword="手机", page_number=1)
        resp_p2 = goods_api_auth.search(keyword="手机", page_number=2)
        assert_success(resp_p1)
        assert_success(resp_p2)
        data_p1 = resp_p1.json()["data"]
        data_p2 = resp_p2.json()["data"]
        assert data_p1["currPage"] == 1
        assert data_p2["currPage"] == 2

    @allure.story("排序查询")
    @pytest.mark.parametrize("order_by", ["new", "price"])
    def test_search_order_by(self, goods_api_auth, order_by):
        """验证排序参数（按新品/按价格）"""
        resp = goods_api_auth.search(keyword="手机", order_by=order_by)
        assert_success(resp)

    @allure.story("异常搜索")
    def test_search_without_keyword(self, goods_api):
        """不传关键词搜索应失败"""
        resp = goods_api.search()
        assert_error(resp)


@allure.epic("新蜂商城接口自动化测试")
@allure.feature("商品模块")
@pytest.mark.goods
class TestGoodsCategory:
    """商品分类"""

    @allure.story("获取分类列表")
    @pytest.mark.smoke
    def test_get_categories(self, goods_api):
        """获取所有商品分类"""
        resp = goods_api.get_categories()
        assert_success(resp)
        data = resp.json()["data"]
        assert len(data) >= DATA["category_count_min"], "分类数量不足"

    @allure.story("首页数据")
    @pytest.mark.smoke
    def test_index_info(self, goods_api):
        """获取首页聚合数据"""
        resp = goods_api.get_index_info()
        assert_success(resp)
        data = resp.json()["data"]
        assert "carousels" in data, "缺少轮播图数据"
        assert "hotGoodses" in data, "缺少热销商品数据"
        assert "newGoodses" in data, "缺少新品数据"
        assert "recommendGoodses" in data, "缺少推荐商品数据"
