import logging
from enum import Enum
from typing import Any, final

from pythonjsonlogger.core import RESERVED_ATTRS
from pythonjsonlogger.json import JsonFormatter
from rich.logging import RichHandler

from .utils import FinalMeta


@final
class StructLogAdapter(metaclass=FinalMeta):
    def __init__(
        self,
        logger: logging.Logger,
        bound: dict[str, Any] | None = None,
    ):
        self._logger = logger
        self._opts: dict[str, Any] = dict(stacklevel=1)
        self._bound: dict[str, Any] = bound or {}

    def bind(self, **kwargs):
        return self.__class__(logger=self._logger, bound={**self._bound, **kwargs})

    def __log(self, level, msg, opts: dict[str, Any] | None = None, /, **kwargs):
        merged_opts = self._opts.copy()
        merged_opts.update(opts or {})
        merged_opts["stacklevel"] += 2
        merged_opts.setdefault("extra", {}).update(kwargs)
        self._logger.log(level, msg, **merged_opts)

    def log(self, level, msg, opts: dict[str, Any] | None = None, /, **kwargs):
        self.__log(level, msg, opts, **kwargs)

    def debug(self, msg, opts: dict[str, Any] | None = None, **kwargs):
        self.__log(logging.DEBUG, msg, opts, **kwargs)

    def info(self, msg, opts: dict[str, Any] | None = None, **kwargs):
        self.__log(logging.INFO, msg, opts, **kwargs)

    def warning(self, msg, opts: dict[str, Any] | None = None, **kwargs):
        self.__log(logging.WARNING, msg, opts, **kwargs)

    def error(self, msg, opts: dict[str, Any] | None = None, **kwargs):
        self.__log(logging.ERROR, msg, opts, **kwargs)

    def critical(self, msg, opts: dict[str, Any] | None = None, **kwargs):
        self.__log(logging.CRITICAL, msg, opts, **kwargs)

    def __getattr__(self, name):
        return getattr(self._logger, name)


class ExtraFormatter(logging.Formatter):
    def format(self, record):
        base = super().format(record)
        extra = "".join(
            f" {k}={v}" for k, v in record.__dict__.items() if k not in RESERVED_ATTRS
        )
        return f"{base:40s}{extra}"


class LoggingType(Enum):
    CONSOLE = "console"
    JSON = "json"


def make_logging_handler(type_: LoggingType) -> logging.Handler:
    match type_:
        case LoggingType.CONSOLE:
            handler = RichHandler(markup=True, rich_tracebacks=True)
            formatter = ExtraFormatter("%(message)s")
            handler.setFormatter(formatter)
        case LoggingType.JSON:
            # noinspection SpellCheckingInspection
            rename_fields = {
                "name": "logger",
                "levelname": "level",
                "filename": "file",
                "lineno": "line",
                "funcName": "func",
                "process": "pid",
                "thread": "tid",
            }
            handler = logging.StreamHandler()
            formatter = JsonFormatter(
                timestamp=True,
                exc_info_as_array=True,
                stack_info_as_array=True,
                reserved_attrs=set(RESERVED_ATTRS) - rename_fields.keys(),
                rename_fields=rename_fields,
            )
            handler.setFormatter(formatter)
        case _:
            handler = logging.NullHandler()
    return handler
