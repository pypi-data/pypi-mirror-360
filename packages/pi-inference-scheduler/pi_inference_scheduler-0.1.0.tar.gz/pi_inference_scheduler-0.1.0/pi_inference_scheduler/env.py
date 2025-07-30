from typing import TYPE_CHECKING, Any, List
import os

if TYPE_CHECKING:
    AUTH_TOKEN: str = ""

_env = {
    "AUTH_TOKEN": lambda: os.getenv("AUTH_TOKEN", ""),
}


def __getattr__(name: str) -> Any:
    if name not in _env:
        raise AttributeError(f"Invalid environment variable: {name}")
    return _env[name]()


def __dir__() -> List[str]:
    return list(_env.keys())