from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Mapping
    from types import TracebackType


@dataclass
class TimeAwareLogger(logging.Logger):
    """A logger class that formats datetime objects into human-readable strings."""

    logger: logging.Logger

    def __getattr__(self, item: Any) -> Any:
        """Delegate attribute access to the underlying logger object.

        This handles cases where the logger's method is called directly on this class instance.
        """
        return getattr(self.logger, item)

    @staticmethod
    def _format_args(*args: Any) -> list[Any]:
        from polykit.time import get_pretty_time

        return [get_pretty_time(arg) if isinstance(arg, datetime) else arg for arg in args]

    def debug(
        self,
        msg: object,
        *args: object,
        exc_info: bool
        | tuple[type[BaseException], BaseException, TracebackType | None]
        | tuple[None, None, None]
        | BaseException
        | None = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        """Log 'msg % args' with severity 'DEBUG'.

        To pass exception information, use the keyword argument exc_info with a true value, e.g.

        logger.debug("Houston, we have a %s", "thorny problem", exc_info=True)
        """
        formatted_args = self._format_args(*args)
        self.logger.debug(
            msg,
            *formatted_args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel + 1,
            extra=extra,
        )

    def info(
        self,
        msg: object,
        *args: object,
        exc_info: bool
        | tuple[type[BaseException], BaseException, TracebackType | None]
        | tuple[None, None, None]
        | BaseException
        | None = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        """Log 'msg % args' with severity 'INFO'.

        To pass exception information, use the keyword argument exc_info with a true value, e.g.

        logger.info("Houston, we have a %s", "notable problem", exc_info=True)
        """
        formatted_args = self._format_args(*args)
        self.logger.info(
            msg,
            *formatted_args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel + 1,
            extra=extra,
        )

    def warning(
        self,
        msg: object,
        *args: object,
        exc_info: bool
        | tuple[type[BaseException], BaseException, TracebackType | None]
        | tuple[None, None, None]
        | BaseException
        | None = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        """Log 'msg % args' with severity 'WARNING'.

        To pass exception information, use the keyword argument exc_info with a true value, e.g.

        logger.warning("Houston, we have a %s", "bit of a problem", exc_info=True)
        """
        formatted_args = self._format_args(*args)
        self.logger.warning(
            msg,
            *formatted_args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel + 1,
            extra=extra,
        )

    def error(
        self,
        msg: object,
        *args: object,
        exc_info: bool
        | tuple[type[BaseException], BaseException, TracebackType | None]
        | tuple[None, None, None]
        | BaseException
        | None = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        """Log 'msg % args' with severity 'ERROR'.

        To pass exception information, use the keyword argument exc_info with a true value, e.g.

        logger.error("Houston, we have a %s", "major problem", exc_info=True)
        """
        formatted_args = self._format_args(*args)
        self.logger.error(
            msg,
            *formatted_args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel + 1,
            extra=extra,
        )
