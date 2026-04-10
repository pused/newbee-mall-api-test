from typing import Any
import pymysql
from config.settings import DB_CONFIG
from common.logger import log


class DBHelper:
    """MySQL 数据库操作辅助类，用于测试数据校验"""

    def __init__(self):
        self.config = DB_CONFIG

    def _connect(self):
        return pymysql.connect(
            host=self.config["host"],
            port=self.config["port"],
            user=self.config["user"],
            password=self.config["password"],
            database=self.config["database"],
            charset=self.config.get("charset", "utf8mb4"),
            cursorclass=pymysql.cursors.DictCursor,
        )

    def query(self, sql: str, params: Any = None) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                result = cursor.fetchall()
                log.debug(f"SQL: {sql} | 参数: {params} | 返回 {len(result)} 条")
                return list(result)
        finally:
            conn.close()

    def query_one(self, sql: str, params: Any = None) -> dict[str, Any] | None:
        result = self.query(sql, params)
        return result[0] if result else None

    def execute(self, sql: str, params=None) -> int:
        conn = self._connect()
        try:
            with conn.cursor() as cursor:
                affected = cursor.execute(sql, params)
                conn.commit()
                log.debug(f"SQL: {sql} | 影响 {affected} 行")
                return affected
        finally:
            conn.close()

    def count(self, table: str, where: str = "1=1", params=None) -> int:
        result = self.query_one(f"SELECT COUNT(*) as cnt FROM {table} WHERE {where}", params)
        return result["cnt"] if result else 0
