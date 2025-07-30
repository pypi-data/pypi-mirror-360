from .brams import adsb, file, location, system
from . import brams, event, optical, processing, trajectory, utils, scripts
import logging
import sys

__all__ = [
    "brams",
    "event",
    "optical",
    "processing",
    "trajectory",
    "utils",
    "adsb",
    "file",
    "location",
    "system",
    "enable_logging",
    "disable_logging",
    "enable_cache",
    "disable_cache",
    "clear_cache",
    "scripts",
]

logging.basicConfig(
    stream=sys.stdout,
    level=logging.CRITICAL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def enable_logging(level=logging.DEBUG) -> None:
    logging.getLogger().setLevel(level)


def disable_logging() -> None:
    logging.getLogger().setLevel(logging.CRITICAL)


def enable_cache() -> None:
    from pybrams.utils import Config

    Config.set("pybrams.utils.cache", "use", True)


def disable_cache() -> None:
    from pybrams.utils import Config

    Config.set("pybrams.utils.cache", "use", False)


def clear_cache() -> None:
    from pybrams.utils import Cache

    Cache.clear()


def enable_brams_archive() -> None:
    from .brams.fetch.archive import is_archive_reachable

    file.use_brams_archive = is_archive_reachable()


def disable_brams_archive() -> None:
    file.use_brams_archive = False
