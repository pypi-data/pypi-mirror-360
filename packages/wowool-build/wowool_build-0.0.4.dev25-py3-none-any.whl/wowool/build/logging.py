from contextlib import contextmanager
from dataclasses import dataclass
from logging import (
    CRITICAL,
    DEBUG,
    ERROR,
    Formatter as StandardFormatter,
    INFO,
    Logger,
    StreamHandler,
    WARNING,
    basicConfig,
    getLogger as _getLogger,
)
from os import getcwd
from pathlib import Path
from tomllib import TOMLDecodeError, loads
from typing import Any, Union

_pyproject_tool_id = "wowool_build_logging"
_default_loggers_names = ["root", "wowool"]
_pyproject_toml_filename = "pyproject.toml"


def _get_fn_pyproject_toml_from_identifier(identifier: Union[str, Path, None] = None) -> Path:
    if identifier is None:
        identifier = getcwd()
    if isinstance(identifier, str):
        identifier = Path(identifier).parent.resolve()
    fn = identifier if identifier.is_file() else identifier / _pyproject_toml_filename
    if not fn.exists() or not fn.is_file():
        raise LoggingConfigError(f"Expected {fn} to be an existing file")
    return fn


# TODO: Once supoport for Python<3.11 is dropped, the imports can be moved to global scope
def _parse_pyproject_toml(fn_pyproject_toml: Path) -> dict:
    try:
        return loads(fn_pyproject_toml.read_text())
    except TOMLDecodeError as error:
        raise LoggingConfigError(f"Configuration error in {fn_pyproject_toml}: {error}")


class LoggingConfigError(RuntimeError):
    pass


@dataclass
class LoggerConfig:
    level: Union[str, int]
    format: str
    colored: bool


def configure_logger(logger_name: str, config: LoggerConfig):
    logger = _getLogger(logger_name)
    logger.propagate = False
    logger.handlers.clear()
    logger.setLevel(config.level)

    handler = StreamHandler()
    Formatter = ColoredFormatter if config.colored else StandardFormatter
    formatter = Formatter(config.format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def default_config():
    return LoggerConfig(
        level="INFO",
        format="%(levelname)-8s %(name)s: %(message)s",
        colored=False,
    )


def read_config(config_raw: dict) -> LoggerConfig:
    if not isinstance(config_raw, dict):
        raise LoggingConfigError(f"Incorrect logging configuration, most likely no logger was specified")

    def get_parameter(key: str, default_value: Any) -> Any:
        return config_raw[key] if key in config_raw else default_value

    defaults = default_config()
    return LoggerConfig(
        level=get_parameter("level", defaults.level),
        format=get_parameter("format", defaults.format),
        colored=get_parameter("colored", defaults.colored),
    )


class ColoredFormatter(StandardFormatter):
    def __init__(self, format: str):
        grey = "\x1b[0;30m"
        blue = "\x1b[0;34m"
        red = "\x1b[31;20m"
        red_bold = "\x1b[31;1m"
        yellow = "\x1b[33;20m"

        reset = "\x1b[0m"
        formats = {
            DEBUG: grey + format + reset,
            INFO: blue + format + reset,
            WARNING: yellow + format + reset,
            ERROR: red + format + reset,
            CRITICAL: red_bold + format + reset,
        }
        self.formatter = {level: StandardFormatter(config) for level, config in formats.items()}

    def format(self, record):
        return self.formatter[record.levelno].format(record)


def init_logging(configuration_path_identifier: Union[str, Path, None] = None, name: str = ""):
    fn_pyproject_toml = _get_fn_pyproject_toml_from_identifier(configuration_path_identifier)
    pyproject = _parse_pyproject_toml(fn_pyproject_toml)
    if not "tool" in pyproject or not _pyproject_tool_id in pyproject["tool"]:
        basicConfig(level="DEBUG")
    else:
        wowool_build_logging = pyproject["tool"][_pyproject_tool_id]
        logger_names = list(wowool_build_logging.keys())
        logger_names.extend(_default_loggers_names)
        logger_names = set(logger_names)
        for logger_name in logger_names:
            config = read_config(wowool_build_logging[logger_name]) if logger_name in wowool_build_logging else default_config()
            configure_logger(logger_name, config)

    if name:
        return _getLogger(name)


def get_logger(name: str, configuration_path_identifier: Union[str, Path, None] = None) -> Logger:
    if configuration_path_identifier is not None:
        init_logging(configuration_path_identifier)
    return _getLogger(name)


def getLogger(*args, **kwargs):
    return get_logger(*args, **kwargs)


@contextmanager
def set_logger_level(logger: Union[Logger, str], level):  # pyright: ignore
    if isinstance(logger, str):
        logger = _getLogger(logger)
    level_previous = logger.level
    try:
        logger.debug(f"Switching logger level to {level}")
        logger.setLevel(level)
        yield
    finally:
        logger.debug(f"Switching logger level to {level_previous}")
        logger.setLevel(level_previous)


def silence_logger(logger: Union[Logger, str], level=100):
    return set_logger_level(logger, level)
