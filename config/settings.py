import os
from typing import Any
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV = os.getenv("TEST_ENV", "dev")


def load_config() -> dict[str, Any]:
    config_path = os.path.join(BASE_DIR, "config", "env", f"{ENV}.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_test_data(filename: str) -> dict[str, Any]:
    data_path = os.path.join(BASE_DIR, "data", filename)
    with open(data_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


CONFIG = load_config()

# 快捷访问
BASE_URL = CONFIG["api"]["base_url"]
DB_CONFIG = CONFIG.get("database", {})
