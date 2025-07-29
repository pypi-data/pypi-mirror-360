"""Define the CodeData class, to store code analysis data."""

from dataclasses import dataclass
from typing import Iterable


@dataclass
class CodeData:
    """
    A class to hold code analysis data.
    """

    valid: bool | None
    error: str | None
    std_libs: list[str]
    ext_libs: list[str]
    lib_usage: dict[str, list[dict]]

    def __init__(
        self,
        valid: bool | None = None,
        error: str | None = None,
        std_libs: Iterable | None = None,
        ext_libs: Iterable | None = None,
        lib_usage: dict[str, list[dict]] | None = None,
    ):
        self.valid = valid
        self.error = error
        self.std_libs = self._format_list(std_libs) if std_libs else []
        self.ext_libs = self._format_list(ext_libs) if ext_libs else []
        self.lib_usage = lib_usage if lib_usage is not None else {}

    def _format_list(self, _list: Iterable[str]) -> list[str]:
        """
        Format a list of strings for consistency.
        """
        return sorted(set(_l.lower() for _l in _list))
