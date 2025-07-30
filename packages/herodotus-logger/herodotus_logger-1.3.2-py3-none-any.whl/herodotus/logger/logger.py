import logging
from time import gmtime
from typing import List


class Logger(logging.Logger):
    def __init__(
            self,
            name: str,
            level: int = logging.INFO,
            formatter: logging.Formatter | None = None,
            handlers: List[logging.Handler] | None = None,
            use_gmtime: bool = True):
        super().__init__(name, level)

        self.formatter = formatter or logging.Formatter(
            datefmt="%Y-%m-%dT%H:%M:%S",
            fmt="%(asctime)s|%(name)s|%(levelname)s|%(message)s"
        )
        self.logger: logging.Logger = self.__create_logger__(level)
        self.__set_handlers__(handlers)

        if use_gmtime:
            self.formatter.converter = gmtime

    def __create_logger__(self, level: int):
        logger = logging.getLogger(self.name)
        logger.setLevel(level)
        return logger

    def __set_handlers__(self, handlers: List[logging.Handler]):
        if self.logger.hasHandlers():  # remove previous handlers
            self.logger.handlers.clear()
        for handler in handlers:
            if not handler.formatter:
                handler.setFormatter(self.formatter)
            self.logger.addHandler(handler)
