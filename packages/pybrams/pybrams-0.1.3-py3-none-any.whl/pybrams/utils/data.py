from pathlib import Path
import json


class Data:
    """Utility class for loading and caching static data files from the package's `data` directory."""

    _files: dict[Path, str | dict | list] = {}

    @classmethod
    def load(cls, section: str, key: str, from_json=True) -> str | dict | list:
        """Load a data file from the `data` directory, optionally parsing it as JSON.

        The path to the file is constructed from the section and key parameters, e.g.:
        `section="brams.settings", key="config.json"` → `data/brams/settings/config.json`.

        Files are cached in memory after first load to avoid redundant I/O.

        Args:
            section (str): Dotted path indicating subdirectories inside the `data` directory.
            key (str): The file name to load (e.g., "config.json").
            from_json (bool, optional): Whether to parse the file as JSON. Defaults to True.

        Returns:
            str | dict | list: The contents of the file, either as a raw string or parsed JSON.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            PermissionError: If the file cannot be read due to permissions.
        """
        filepath = (
            Path(__file__).resolve().parents[1]
            / "data"
            / Path(*section.split("."))
            / key
        )

        if filepath in cls._files:
            return cls._files[filepath]

        if not filepath.exists():
            raise FileNotFoundError(f"File not found : {filepath}")

        try:
            with open(filepath, "r") as f:
                data: str | dict | list = json.load(f) if from_json else f.read()
        except PermissionError:
            raise PermissionError(f"Permission denied : {filepath}")

        cls._files[filepath] = data
        return data
