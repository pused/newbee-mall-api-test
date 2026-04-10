# -*- coding: utf-8 -*-
"""全局 fixture - 提供 HTTP 客户端、已登录客户端、数据库连接"""

import sys
import os
import pytest

# 将项目根目录加入 sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common.http_client import HttpClient
from common.db_helper import DBHelper
from common.logger import log
from api.user_api import UserAPI

# auth_client 使用独立账号，避免与登录测试用例互相冲掉 token
AUTH_PHONE = "13800002222"
AUTH_PASSWORD = "123456"
AUTH_PASSWORD_MD5 = "e10adc3949ba59abbe56e057f20f883e"


@pytest.fixture(scope="session")
def client():
    """未登录的 HTTP 客户端"""
    return HttpClient()


@pytest.fixture(scope="session")
def auth_client():
    """已登录的 HTTP 客户端（session 级别，使用独立测试账号）"""
    c = HttpClient()
    user_api = UserAPI(c)

    # 先注册（已存在会失败，忽略即可）
    user_api.register(AUTH_PHONE, AUTH_PASSWORD)  # type: ignore[reportCallIssue]

    # 登录获取 token
    resp = user_api.login(AUTH_PHONE, AUTH_PASSWORD_MD5)  # type: ignore[reportCallIssue]
    token = resp.json().get("data")
    assert token, f"登录失败，无法获取 token: {resp.json()}"

    c.set_token(token)
    log.info(f"全局登录成功，token: {token[:20]}...")

    # 创建默认收货地址（下单需要）
    c.post("/api/v1/address", json={
        "userName": "测试用户",
        "userPhone": AUTH_PHONE,
        "defaultFlag": 1,
        "provinceName": "北京市",
        "cityName": "北京市",
        "regionName": "朝阳区",
        "detailAddress": "测试地址123号",
    })

    return c


@pytest.fixture(scope="session")
def db():
    """数据库连接"""
    return DBHelper()
