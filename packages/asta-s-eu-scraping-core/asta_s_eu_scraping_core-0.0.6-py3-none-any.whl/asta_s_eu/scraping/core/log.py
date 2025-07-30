from typing import Any, Optional, Type, TypeVar

import datetime
import logging
import sys
from logging import Logger, getLogger
from pathlib import Path

import yaml

from .config import CONFIG_DIR

LOG = logging.getLogger(__name__)

T = TypeVar('T', bound='LogConfig')

class LogConfig:
    """Add logging configuration from config"""
    _instance = None

    def __new__(cls: Type[T], *args: Any, **kwargs: Any) -> T:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config: dict[str, Any]) -> None:
        if hasattr(self, '_initialized') and self._initialized: # pylint: disable=access-member-before-definition
            LOG.warning('Prevented re-initialization on subsequent instantiations '
                        'for log configuration')
            return

        self._config = config
        self._initialized: bool = True


    @property
    def _formatters(self) -> dict[str, logging.Formatter]:
        formatters: dict[str, logging.Formatter] = {}
        for k, v in self._config["formatters"].items():
            formatters[k] = logging.Formatter(
                v['format']
            )
        return formatters

    @property
    def _handlers(self) -> dict[str, logging.Handler]:
        formatters = self._formatters
        handlers: dict[str, logging.Handler] = {}
        for k, v in self._config["handlers"].items():
            handler: logging.Handler

            if v['class'] == 'logging.StreamHandler':
                if v['stream'] == 'ext://sys.stdout':
                    stream = sys.stdout
                else:
                    raise NotImplementedError(v['stream'])

                handler = logging.StreamHandler(stream)

            elif v['class'] == 'logging.FileHandler':
                handler = logging.FileHandler(v['filename'])
            else:
                raise NotImplementedError(v['class'])

            handler.setFormatter(formatters[v['formatter']])
            handler.setLevel(v['level'])

            handlers[k] = handler
        return handlers

    @property
    def _loggers(self) -> dict[str, logging.Logger]:
        handlers = self._handlers
        loggers: dict[str, logging.Logger] = {}
        for k, v in self._config["loggers"].items():
            logger = logging.getLogger(k)
            logger.setLevel(v['level'])

            if 'propagate' in v:
                logger.propagate = v['propagate']

            for handler in v['handlers']:
                logger.addHandler(handlers[handler])

            loggers[k] = logger

        return loggers

    def set_root(self) -> None:
        """Add handlers, log level and propagation to the root logger"""
        handlers = self._handlers
        root = self._config["root"]

        logger = logging.getLogger()
        logger.setLevel(root['level'])

        if 'propagate' in root:
            logger.propagate = root['propagate']

        for handler in root['handlers']:
            logger.addHandler(handlers[handler])


def get_loggers(module_path: Path,
                logging_yaml: Path,
                logger_name: Optional[str] = None
                ) -> tuple[Logger, Optional[Path]]:
    """
    Create a logger out of yaml log configuration.
    :returns: log and path to alarm log file
    """
    _log_config = yaml.safe_load(logging_yaml.read_text().format(
        now=datetime.datetime.now(datetime.UTC),
        CONFIG_DIR=CONFIG_DIR,
    ))

    LogConfig(_log_config).set_root()

    alarm_log = None
    if 'alert' in _log_config['handlers']:
        alarm_log = Path(_log_config['handlers']['alert']['filename'])

    return getLogger(logger_name or module_path.name), alarm_log


class MakeRetryAsInfo(Logger):
    """
    Wrapper for retry lib how retry times in logs
    """
    def warning(self, *args: Any, **kwargs: Any) -> None:
        print("MY_INFO ====== ", *args, **kwargs)
        super().info(*args, **kwargs)
