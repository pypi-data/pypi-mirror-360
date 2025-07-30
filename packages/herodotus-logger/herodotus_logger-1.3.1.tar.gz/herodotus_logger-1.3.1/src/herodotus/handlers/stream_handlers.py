from logging import StreamHandler, Formatter
from typing import Callable

from src.herodotus.handlers.enhanced_handler import EnhancedHandler


class EnhancedStreamHandler(EnhancedHandler):
    def __init__(
            self,
            stream=None,
            concurrent: bool = False,
            level: int = 0,
            strict_level: bool = False,
            formatter: Formatter | None = None,
            msg_func: Callable[[str], str] | None = None):
        self.handler = StreamHandler(stream=stream)
        super().__init__(concurrent, level, strict_level, formatter, msg_func)
