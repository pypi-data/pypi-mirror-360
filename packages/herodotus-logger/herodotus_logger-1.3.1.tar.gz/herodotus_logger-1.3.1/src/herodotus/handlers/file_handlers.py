import datetime
from logging import FileHandler, Formatter
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
from typing import Callable, Optional, Tuple

from concurrent_log_handler import ConcurrentRotatingFileHandler, ConcurrentTimedRotatingFileHandler

from src.herodotus.handlers.enhanced_handler import EnhancedHandler


class EnhancedFileHandler(EnhancedHandler):
    def __init__(
            self,
            filename,
            mode: str = "a",
            maxBytes: int = 0,
            backupCount: int = 0,
            encoding: Optional[str] = None,
            debug: Optional[bool] = False,
            delay: Optional[bool | None] = None,
            use_gzip: Optional[bool] = False,
            owner: Optional[Tuple[str, str]] = None,
            chmod: Optional[int] = None,
            umask: Optional[int] = None,
            newline: Optional[str] = None,
            terminator: str = "\n",
            unicode_error_policy: str = "ignore",
            lock_file_directory: Optional[str] = None,
            keep_file_open: bool = True,  # New parameter, default to True for better performance            mode='a',
            errors=None,
            concurrent: bool = False,
            level: int = 0,
            strict_level: bool = False,
            formatter: Formatter | None = None,
            msg_func: Callable[[str], str] | None = None):
        if concurrent:
            self.handler = ConcurrentRotatingFileHandler(
                filename,
                mode=mode,
                maxBytes=maxBytes,
                backupCount=backupCount,
                encoding=encoding,
                debug=debug,
                delay=delay,
                use_gzip=use_gzip,
                owner=owner,
                chmod=chmod,
                umask=umask,
                newline=newline,
                terminator=terminator,
                unicode_error_policy=unicode_error_policy,
                lock_file_directory=lock_file_directory,
                keep_file_open=keep_file_open,
            )
        else:
            self.handler = FileHandler(
                filename,
                mode=mode,
                encoding=encoding,
                delay=False if delay is None else True,
                errors=errors
            )
        super().__init__(concurrent, level, strict_level, formatter, msg_func)


class EnhancedTimedRotatingFileHandler(EnhancedHandler):
    def __init__(
            self,
            filename,
            when: str = "h",
            interval: int = 1,
            backupCount: int = 0,
            encoding: Optional[str] = None,
            delay: bool = False,
            utc: bool = False,
            atTime: Optional[datetime.time] = None,
            errors: Optional[str] = None,
            maxBytes: int = 0,
            use_gzip: bool = False,
            owner: Optional[Tuple[str, str]] = None,
            chmod: Optional[int] = None,
            umask: Optional[int] = None,
            newline: Optional[str] = None,
            terminator: str = "\n",
            unicode_error_policy: str = "ignore",
            lock_file_directory: Optional[str] = None,
            keep_file_open: bool = True,
            concurrent=False,
            level: int = 0,
            strict_level: bool = False,
            formatter: Formatter | None = None,
            msg_func: Callable[[str], str] | None = None):
        if concurrent:
            self.handler = ConcurrentTimedRotatingFileHandler(
                filename,
                when=when,
                interval=interval,
                backupCount=backupCount,
                encoding=encoding,
                delay=delay,
                utc=utc,
                atTime=atTime,
                errors=errors,
                maxBytes=maxBytes,
                use_gzip=use_gzip,
                owner=owner,
                chmod=chmod,
                umask=umask,
                newline=newline,
                terminator=terminator,
                unicode_error_policy=unicode_error_policy,
                lock_file_directory=lock_file_directory,
                keep_file_open=keep_file_open,
            )
        else:
            self.handler = TimedRotatingFileHandler(
                filename,
                when=when,
                interval=interval,
                backupCount=backupCount,
                encoding=encoding,
                delay=delay,
                utc=utc,
                atTime=atTime,
                errors=errors
            )
        super().__init__(concurrent, level, strict_level, formatter, msg_func)


class EnhancedSizeRotatingFileHandler(EnhancedHandler):
    def __init__(
            self,
            filename,
            mode: str = "a",
            maxBytes: int = 0,
            backupCount: int = 0,
            encoding: Optional[str] = None,
            debug: bool = False,
            delay: Optional[bool | None] = None,
            use_gzip: bool = False,
            owner: Optional[Tuple[str, str]] = None,
            chmod: Optional[int] = None,
            umask: Optional[int] = None,
            newline: Optional[str] = None,
            terminator: str = "\n",
            unicode_error_policy: str = "ignore",
            lock_file_directory: Optional[str] = None,
            keep_file_open: bool = True,
            errors=None,
            concurrent=False,
            level: int = 0,
            strict_level: bool = False,
            formatter: Formatter | None = None,
            msg_func: Callable[[str], str] | None = None):
        if concurrent:
            self.handler = ConcurrentRotatingFileHandler(
                filename,
                mode=mode,
                maxBytes=maxBytes,
                backupCount=backupCount,
                encoding=encoding,
                debug=debug,
                delay=delay,
                use_gzip=use_gzip,
                owner=owner,
                chmod=chmod,
                umask=umask,
                newline=newline,
                terminator=terminator,
                unicode_error_policy=unicode_error_policy,
                lock_file_directory=lock_file_directory,
                keep_file_open=keep_file_open,
            )
        else:
            self.handler = RotatingFileHandler(
                filename,
                mode=mode,
                maxBytes=maxBytes,
                backupCount=backupCount,
                encoding=encoding,
                delay=False if delay is None else True,
                errors=errors
            )
        super().__init__(concurrent, level, strict_level, formatter, msg_func)
