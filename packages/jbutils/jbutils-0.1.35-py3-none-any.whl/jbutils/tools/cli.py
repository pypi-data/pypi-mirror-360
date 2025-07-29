"""CLI Testing tool for checking local functionality"""

import json
import os

from dataclasses import dataclass

from ptpython import embed

from jbutils.utils.config import Configurator
from jbutils import jbutils

# from .config import Configurator
sample_files_1 = ["init.json", "test.yaml"]
sample_files_2 = {
    "common": {
        "tools": {
            "test1.json": {"a": 5, "b": "b", "c": {"c1": 1, "c2": False}},
            "test2.yaml": {"a": 10, "b": "B", "c": [{"c1": 2, "c2": True}]},
        }
    },
    "init.yaml": {"a": 15, "b": "test", "c": {"c1": 3, "c2": "true"}},
}


@dataclass
class TestC:
    c1: int = -1
    c2: bool = True


@dataclass
class Test1:
    a: int = -1
    b: str = ""
    c: TestC | dict = None

    def __post_init__(self) -> None:
        if isinstance(self.c, dict):
            self.c = TestC(**self.c)


def main() -> None:
    cfg = Configurator(app_name="cfgtest")
    dpath = "saved_data.test3.yaml"
    embed(
        globals=globals(), locals=locals(), history_filename="jbutils_cli.history"
    )


if __name__ == "__main__":
    main()
