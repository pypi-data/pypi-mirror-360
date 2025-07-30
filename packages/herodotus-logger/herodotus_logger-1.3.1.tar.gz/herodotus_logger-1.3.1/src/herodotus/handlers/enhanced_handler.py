import copy
from logging import Formatter, LogRecord, Handler
from typing import Callable


class EnhancedHandler(Handler):
    def __init__(self,
                 concurrent: bool = False,
                 level: int = 0,
                 strict_level: bool = False,
                 formatter: Formatter | None = None,
                 msg_func: Callable[[str], str] | None = None):
        super().__init__()
        self.concurrent = concurrent
        self.level = level
        self.strict_level = strict_level
        self.formatter = formatter
        self.msg_func = msg_func

        if type(self) != EnhancedHandler:
            if getattr(self, "handler", None) is None:
                raise NotImplementedError(f"{self.__class__.__name__} must define `self.handler` in __init__.")

    def emit(self, record: LogRecord) -> None:
        if not isinstance(record.msg, str):
            try:
                record.msg = str(record.msg) or repr(record.msg)
            except Exception:
                raise Exception("Cannot convert object of type", type(record.msg), "to string")
        if not self.strict_level or record.levelno == self.level:
            modified_record = copy.deepcopy(record)
            if self.msg_func:
                modified_record.msg = self.msg_func(modified_record.msg)
            getattr(self, "handler").emit(modified_record)
