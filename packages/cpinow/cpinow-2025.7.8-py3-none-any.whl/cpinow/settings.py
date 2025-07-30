# -*- coding: utf-8 -*-
"""Project settings."""

import logging
from enum import Enum, IntEnum
from pathlib import Path
from typing import Optional

from dotenv import find_dotenv, load_dotenv
from pydantic import BaseSettings


def init_dotenv():
    """Loc n' load dotenv file.

    Sets the location for a dotenv file containig envvars loads its
    contents.

    Returns:
        Location of the dotenv file.

    """

    candidate = find_dotenv(usecwd=True)

    if not candidate:
        print(".env file not found, env vars must be seted manually")
        return

    load_dotenv(candidate)


class LogLevel(IntEnum):
    """Explicitly define allowed logging levels."""

    CRITICAL = logging.CRITICAL

    ERROR = logging.ERROR

    WARNING = logging.WARNING

    INFO = logging.INFO

    DEBUG = logging.DEBUG

    TRACE = 1 + logging.NOTSET

    NOTSET = logging.NOTSET


class LogDest(Enum):
    """Define allowed destinations for logs."""

    CONSOLE = "CONSOLE"
    """Log to console"""

    FILE = "FILE"
    """Log to file"""


class LogFormatter(Enum):
    """Define allowed destinations for logs."""

    JSON = "JSON"
    """JSONs, eg for filebeat or similar, for machines."""

    COLOR = "COLOR"
    """pprinted, colored, for humans"""


class Settings(BaseSettings):
    """Project settings variables."""

    PACKAGE_PATH = Path(__file__).parent
    """Package path (python files)."""

    PROJECT_PATH = PACKAGE_PATH.parent
    """Project path (all files)."""

    LOG_PATH: Optional[Path]
    """Path to logfile, only works if ``LOG_DESTINATION=FILE``."""

    LOG_FORMAT: LogFormatter = LogFormatter.JSON.value
    """Log style."""

    LOG_LEVEL: LogLevel = LogLevel.INFO.value
    """Log level from ``logging`` module."""

    LOG_DESTINATION: LogDest = LogDest.CONSOLE.value
    """Destination for logs."""

    COLOMBIA_LOCAL_PATH: Path = Path(PACKAGE_PATH, "data", "colombia.csv")
    """Path to local file with Colombia CPI data."""

    PERU_LOCAL_PATH: Path = Path(PACKAGE_PATH, "data", "peru.csv")
    """Path to local file with Peru CPI data."""

    class Config:
        """Inner configuration."""

        env_prefix = "CPINOW_"
        use_enum_values = True


def init_settings() -> Settings:
    """Initilize project settings"""
    init_dotenv()
    return Settings()
