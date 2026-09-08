from __future__ import annotations

import ast
import sys

from .base import AdapterStatus


class PythonAdapter:
    language = "Python"

    def detect(self) -> AdapterStatus:
        return AdapterStatus(
            language=self.language,
            available=True,
            version=sys.version.split()[0],
            executable=sys.executable,
            detail="current OPUS runtime interpreter",
        )

    def check_syntax(self, source: str) -> tuple[bool, str]:
        try:
            ast.parse(source)
        except SyntaxError as exc:
            return False, f"{exc.msg} at line {exc.lineno}"
        return True, "syntax OK"
