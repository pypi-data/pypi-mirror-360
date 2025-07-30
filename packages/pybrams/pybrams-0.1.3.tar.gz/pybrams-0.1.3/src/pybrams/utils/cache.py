import os
import shutil
from typing import Any, Union, Dict, Literal
import logging
import datetime
import hashlib
from pybrams.utils.config import Config

logger = logging.getLogger(__name__)


class Cache:
    """A simple file-based caching utility for storing and retrieving data.

    The cache uses a `.pybrams_cache` directory to store cached files.
    It supports both JSON (text) and binary data.
    """

    root = os.path.join(".", ".pybrams_cache")
    data = {}

    @classmethod
    def clear(cls) -> None:
        """Clear all cached data from both memory and disk."""
        logger.info("Clearing cache")
        shutil.rmtree(cls.root, ignore_errors=True)
        cls.data = {}

    @classmethod
    def cache(cls, key: str, data: Any, json: bool = True) -> None:
        """Store data in the cache.

        Args:
            key (str): The cache key.
            data (Any): The data to cache.
            json (bool, optional): Whether to treat the data as JSON/text. Defaults to True.
        """
        if Config.get(__name__, "use"):
            if not os.path.exists(cls.root):
                os.mkdir(cls.root)

            path = f"{key}.json" if json else key
            mode = "w" if json else "wb"

            with open(os.path.join(cls.root, path), mode) as file:
                file.write(data)

            if json:
                cls.data[key] = data

            logger.info(f"Storing {key}")

    @classmethod
    def get(cls, key: str, json: bool = True) -> Union[Any, Literal[False]]:
        """Retrieve data from the cache.

        Args:
            key (str): The cache key.
            json (bool, optional): Whether to treat the data as JSON/text. Defaults to True.

        Returns:
            Union[Any, Literal[False]]: The cached data, or False if not found or disabled.
        """
        if Config.get(__name__, "use"):
            path = f"{key}.json" if json else key
            mode = "r" if json else "rb"

            if json and key in cls.data:
                return cls.data[key]

            if not os.path.exists(os.path.join(cls.root, path)):
                return False

            with open(os.path.join(cls.root, path), mode) as file:
                data = file.read()
                cls.data[key] = data
                logger.info(f"Retrieving {key}")
                return data

        return False

    @classmethod
    def remove(cls, key: str, json: bool = True) -> bool:
        """Remove a specific item from the cache.

        Args:
            key (str): The cache key.
            json (bool, optional): Whether to treat the data as JSON/text. Defaults to True.

        Returns:
            bool: True if the item was removed, False otherwise.
        """
        path = f"{key}.json" if json else key
        full_path = os.path.join(cls.root, path)

        if json and key in cls.data:
            del cls.data[key]

        if os.path.exists(full_path):
            os.remove(full_path)
            logger.info(f"Removed {key}")
            return True

        return False

    @classmethod
    def stats(cls) -> Dict[str, Union[int, float]]:
        """Return statistics about the current cache state.

        Returns:
            Dict[str, Union[int, float]]: A dictionary with the number of files
                and total size in bytes, kilobytes, and megabytes.
        """
        if not os.path.exists(cls.root):
            return {
                "number_of_files": 0,
                "total_size_bytes": 0,
                "total_size_kb": 0,
                "total_size_mb": 0,
            }

        total_size = 0
        file_count = 0

        for root, _, files in os.walk(cls.root):
            for file in files:
                file_count += 1
                total_size += os.path.getsize(os.path.join(root, file))

        return {
            "number_of_files": file_count,
            "total_size_bytes": total_size,
            "total_size_kb": round(total_size / 1024, 2),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }


def generate_key(payload: Dict[str, Any]) -> str:
    """Generate a deterministic SHA-256 key from a payload dictionary.

    Args:
        payload (Dict[str, Any]): A dictionary of values to generate the key from.
            Supports strings, lists of strings, and datetime objects.

    Returns:
        str: A SHA-256 hexadecimal hash string representing the payload.
    """
    result: list = []
    for key in sorted(payload.keys()):
        value = payload[key]
        if isinstance(value, datetime.datetime):
            result.append(f"{key}{value.strftime('%Y%m%d_%H%M')}")
        if isinstance(value, list):
            joined_list = "-".join(value)
            if joined_list:
                result.append(joined_list)
        if isinstance(value, str):
            result.append(value)
    return hashlib.sha256(("_".join(result)).encode()).hexdigest()
