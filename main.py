"""Entrypoint for Deta Micros"""

from sys import path

path.append(".")

from src import (
    get_app,
)

app = get_app()
