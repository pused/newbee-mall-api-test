"""自定义断言方法，统一校验格式"""

import allure
from requests import Response
from common.logger import log


def assert_status_code(resp: Response, expected: int = 200):
    assert resp.status_code == expected, (
        f"状态码错误: 期望 {expected}, 实际 {resp.status_code}"
    )


def assert_success(resp: Response):
    """校验接口返回成功（Newbee-Mall 的 resultCode == 200 表示成功）"""
    data = resp.json()
    assert data["resultCode"] == 200, (
        f"业务码错误: 期望 200, 实际 {data['resultCode']}, message: {data.get('message')}"
    )


def assert_error(resp: Response, expected_code: int | None = None):
    """校验接口返回失败"""
    data = resp.json()
    assert data["resultCode"] != 200, f"期望失败但返回了成功: {data}"
    if expected_code:
        assert data["resultCode"] == expected_code, (
            f"错误码不匹配: 期望 {expected_code}, 实际 {data['resultCode']}"
        )


def assert_field(resp: Response, field: str, expected: object):
    """校验响应中指定字段的值"""
    data = resp.json()
    actual: object = data.get("data", {})

    # 支持嵌套字段 (如 "data.nickName")
    for key in field.split("."):
        if isinstance(actual, dict):
            actual = actual.get(key)
        elif isinstance(actual, list) and key.isdigit():
            actual = actual[int(key)]
        else:
            actual = None
            break

    allure.dynamic.parameter("field", field)
    allure.dynamic.parameter("expected", str(expected))
    log.info(f"断言: {field} | 期望: {expected} | 实际: {actual}")
    assert actual == expected, f"字段 {field} 不匹配: 期望 {expected}, 实际 {actual}"


def assert_list_not_empty(resp: Response, list_field: str = "list"):
    """校验返回列表非空"""
    data = resp.json().get("data", {})
    items = data.get(list_field, [])
    assert len(items) > 0, f"列表 {list_field} 为空"
