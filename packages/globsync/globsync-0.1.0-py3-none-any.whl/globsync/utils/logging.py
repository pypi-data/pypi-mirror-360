import sys
from rich.logging import RichHandler
from rich.console import Console
import logging
from logging import Logger, Formatter
from logging.handlers import RotatingFileHandler
# from colorlog import ColoredFormatter  # StreamHandler
from pythonjsonlogger.jsonlogger import JsonFormatter
import getpass
from typing import Optional, Any


level_str2int: dict[str, int] = {'debug': logging.DEBUG, 'info': logging.INFO, 'warning': logging.WARNING, 'error': logging.ERROR, 'critical': logging.CRITICAL}
loggers: dict[str, Logger] = {}
fmts: dict[str, Any] = {}
handlers: dict[str, Any] = {}
console = Console()

fmts["plain"] = Formatter("%(name)s: %(asctime)s | %(levelname)s | %(module)s:%(funcName)s:%(lineno)s | %(process)d | %(user)s \n %(message)s")
# fmts["color"] = ColoredFormatter("%(name)s: %(white)s%(asctime)s%(reset)s | %(log_color)s%(levelname)s%(reset)s | %(blue)s%(filename)s:%(lineno)s%(reset)s | %(process)d | %(user)s >>> %(log_color)s%(message)s%(reset)s")
fmts["rich"] = Formatter("%(message)s")
fmts["json"] = JsonFormatter("%(name)s %(asctime)s %(levelname)s %(module)s %(funcName) %(lineno)s %(process)d %(user)s %(message)s")

# handlers["stdout"] = StreamHandler(stream=sys.stdout)
# handlers["stdout"].setFormatter(fmts["color"])
# handlers["stdout"].setLevel(logging.INFO)

handlers["stdout"] = RichHandler(level=logging.INFO, show_time=False, show_level=True, show_path=False, rich_tracebacks=True)


def init_file_handler(log_file: str) -> None:
    """Initialize the file handler."""
    handlers["file"] = RotatingFileHandler(log_file, backupCount=2, maxBytes=5000000)
    handlers["file"].setFormatter(fmts["json"])
    handlers["file"].setLevel(logging.DEBUG)
    for logger in loggers.values():
        logger.addHandler(handlers["file"])


def get_logger(name: Optional[str] = None) -> Logger:
    """Get the logger."""
    if name is None:
        name = 'globsync'
    if name not in loggers:
        logger = loggers[name] = logging.getLogger(name)
        for handler in handlers.values():
            logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    return loggers[name]


def log(level: int | str, msg: Optional[str] = "", name: Optional[str] = None, logger: Optional[Logger] = None, stacklevel=2, **kwargs) -> None:
    """Log a message."""
    if logger is None:
        logger = get_logger(name)
    if isinstance(level, str):
        level = level_str2int[level.lower()]
    logger.log(level, msg, extra={"user": getpass.getuser()}, stacklevel=stacklevel, **kwargs)


def handle_exception(exc_type, exc_value, exc_traceback):
    """Log an uncaught exception."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    log(logging.CRITICAL, "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception
