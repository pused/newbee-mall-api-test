"""用例层 fixture — 提供各模块 API 实例"""

import pytest
from api.user_api import UserAPI
from api.goods_api import GoodsAPI
from api.cart_api import CartAPI
from api.order_api import OrderAPI


@pytest.fixture
def user_api(client):
    return UserAPI(client)


@pytest.fixture
def user_api_auth(auth_client):
    return UserAPI(auth_client)


@pytest.fixture
def goods_api(client):
    return GoodsAPI(client)


@pytest.fixture
def goods_api_auth(auth_client):
    return GoodsAPI(auth_client)


@pytest.fixture
def cart_api(auth_client):
    return CartAPI(auth_client)


@pytest.fixture
def order_api(auth_client):
    return OrderAPI(auth_client)
