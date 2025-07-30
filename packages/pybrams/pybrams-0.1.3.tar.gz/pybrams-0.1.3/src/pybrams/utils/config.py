import json
from typing import Any, Dict
from collections import defaultdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Config:
    """A configuration manager that loads, merges, retrieves, and persists hierarchical configuration data.

    Configuration is loaded from two sources:
    - A default config file: `<package_root>/config/config.json`
    - A user-defined config file: `<cwd>/pybrams.json`
    """

    _config = defaultdict(dict)
    _default_config_path = (
        Path(__file__).resolve().parents[1] / "config" / "config.json"
    )
    _user_defined_config_path = Path.cwd() / "pybrams.json"

    @classmethod
    def load(cls):
        """Load configuration from both default and user-defined files.

        Later sources override earlier ones in case of key collisions.
        """
        cls.load_dict_from_file(cls._default_config_path)
        cls.load_dict_from_file(cls._user_defined_config_path)

    @classmethod
    def load_dict_from_file(cls, file_path: Path) -> None:
        """Load configuration from a file and merge it into the current config.

        Args:
            file_path (Path): The path to the JSON file to load.
        """
        if file_path.exists():
            with open(file_path, "r") as f:
                cls.load_dict(json.load(f))
        else:
            logger.info(
                f"Config file {file_path} not found. Using default configuration."
            )

    @classmethod
    def load_dict(cls, config_dict: Dict[str, Any]) -> None:
        """Merge a dictionary into the current configuration.

        Args:
            config_dict (Dict[str, Any]): A dictionary to merge into the config.
        """

        def merge_dict(target: dict[str, Any], source: dict[str, Any]):
            for key, value in source.items():
                if isinstance(value, dict) and isinstance(target.get(key), dict):
                    merge_dict(target[key], value)
                else:
                    target[key] = value

        merge_dict(cls._config, config_dict)

    @classmethod
    def save(cls, file_path: Path | None = None) -> None:
        """Save the current configuration to a file.

        Args:
            file_path (Path | None, optional): Path to save the config.
                Defaults to the user-defined path (`pybrams.json`).
        """
        if file_path is None:
            file_path = cls._user_defined_config_path
        with open(file_path, "w") as f:
            json.dump(cls._config, f, indent=4)

        logger.info(f"Configuration saved to {file_path}")

    @classmethod
    def get(cls, section: str, key: str) -> Any:
        """Retrieve a configuration value by section and key.

        Args:
            section (str): Dot-delimited section name (e.g., "brams.options").
            key (str): The key to retrieve inside the section.

        Returns:
            Any: The corresponding configuration value.

        Raises:
            KeyError: If the section or key does not exist.
        """
        value = cls._config
        for section_key in section.split("."):
            if not isinstance(value, dict) or section_key not in value:
                raise KeyError(f"Section '{section}' or key '{section_key}' not found.")
            value = value[section_key]
        if key not in value:
            raise KeyError(f"Key '{key}' not found in section '{section}'.")
        return value[key]

    @classmethod
    def set(cls, section: str, key: str, value, save_to_disk=True):
        """Set a configuration value and optionally persist it to disk.

        Args:
            section (str): Dot-delimited section name (e.g., "brams.options").
            key (str): The key to set.
            value (Any): The value to store.
            save_to_disk (bool, optional): Whether to save changes to disk. Defaults to True.
        """
        keys = section.split(".")
        config = cls._config

        for section_key in keys:
            if section_key not in config or not isinstance(config[section_key], dict):
                config[section_key] = {}
            config = config[section_key]

        config[key] = value

        if save_to_disk:
            cls.save()

    @classmethod
    def __getitem__(cls, section):
        """Allow direct dictionary-style access to configuration sections.

        Args:
            section (str): The section name.

        Returns:
            Dict[str, Any]: The corresponding section dictionary.
        """
        return cls._config[section]

    @classmethod
    def __getattr__(cls, section):
        """Allow attribute-style access to configuration sections.

        Args:
            section (str): The section name.

        Returns:
            Dict[str, Any]: The corresponding section dictionary.

        Raises:
            AttributeError: If the section does not exist.
        """
        if section in cls._config:
            return cls._config[section]
        raise AttributeError(f"'Config' object has no attribute '{section}'")
