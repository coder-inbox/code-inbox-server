"""
A fully async based server for Code Inbox built using FastAPI,
MongoDB, pydantic, ODMantic, and Deta.
"""

from src import (
    nylas,
    users,
    utils,
)

from src.main import (
    get_app,
    serve
)
__author__ = """Mahmoud Harmouch"""
__email__ = "oss@wiseai.com"
__version__ = "0.1.0"


__all__ = [
    "nylas",
    "users",
    "utils",
    "get_app",
    "serve",
]
