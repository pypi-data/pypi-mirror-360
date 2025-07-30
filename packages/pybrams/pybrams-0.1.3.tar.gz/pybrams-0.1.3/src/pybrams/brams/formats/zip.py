import zipfile
import io
import logging
import hashlib
from collections import OrderedDict
from typing import Union, Dict

logger = logging.getLogger(__name__)


class ZipExtractor:
    """
    A utility class to extract files from a ZIP archive provided as a file path or bytes.

    Args:
        zippath (Union[str, bytes]): Path to the ZIP file on disk or bytes representing a ZIP archive.

    Attributes:
        zippath (Union[str, bytes]): The source ZIP file path or bytes.
        zip_file (zipfile.ZipFile | None): Internal ZipFile object, opened on demand.
    """

    _max_cache_size = 10
    _handler_cache: "OrderedDict[str, zipfile.ZipFile]" = OrderedDict()

    def __init__(self, zippath: Union[str, bytes]):
        self.zippath = zippath
        self.zip_file: zipfile.ZipFile | None = None
        self._key = self._get_cache_key(zippath)
        if isinstance(self.zippath, str):
            logger.info(f"ZipExtractor initialized with path: {zippath}")
        else:
            logger.info("ZipExtractor initialized with bytes")

    @classmethod
    def _get_cache_key(cls, zippath: Union[str, bytes]) -> str:
        if isinstance(zippath, str):
            return f"path::{zippath}"
        else:
            return f"bytes::{hashlib.sha256(zippath).hexdigest()}"

    def _open_zip(self) -> None:
        """
        Opens the ZIP archive if it is not already opened.

        Raises:
            RuntimeError: If the file is not a valid ZIP archive.
        """
        if self.zip_file:
            return

        if self._key in self._handler_cache:
            self.zip_file = self._handler_cache.pop(self._key)
            self._handler_cache[self._key] = self.zip_file  # move to end
            logger.info(f"Reusing cached ZIP handler: {self._key}")
            return
        try:
            if isinstance(self.zippath, str):
                self.zip_file = zipfile.ZipFile(self.zippath, "r")
                logger.info(f"Opened ZIP file from path: {self.zippath}")
            else:
                self.zip_file = zipfile.ZipFile(io.BytesIO(self.zippath))
                logger.info("Opened ZIP file from byte content.")

            self._add_to_cache(self._key, self.zip_file)

        except zipfile.BadZipFile as e:
            logger.error("The provided file is not a valid ZIP archive.")
            raise RuntimeError("The provided file is not a valid ZIP archive.") from e

    @classmethod
    def _add_to_cache(cls, key: str, handler: zipfile.ZipFile):
        logger.info(f"Caching ZIP handler: {key}")
        cls._handler_cache[key] = handler
        if len(cls._handler_cache) > cls._max_cache_size:
            old_key, old_handler = cls._handler_cache.popitem(last=False)
            old_handler.close()
            logger.info(f"Evicted ZIP handler: {old_key}")

    def extract_file(self, filename: str) -> bytes:
        """
        Extracts a single file from the ZIP archive by name.

        Args:
            filename (str): The name of the file to extract from the ZIP.

        Returns:
            bytes: The content of the extracted file.

        Raises:
            FileNotFoundError: If the specified file is not found in the ZIP archive.
            RuntimeError: If the ZIP archive could not be opened.
            Exception: For any other errors during extraction.
        """
        self._open_zip()
        if self.zip_file is None:
            raise RuntimeError("Failed to open the ZIP archive.")

        try:
            if filename in self.zip_file.namelist():
                with self.zip_file.open(filename) as extracted_file:
                    content = extracted_file.read()
                    logger.info(f"Successfully extracted file: {filename}")
                    return content
            else:
                logger.warning(f"File not found in ZIP archive: {filename}")
                raise FileNotFoundError(f"{filename} not found in the ZIP archive.")
        except Exception:
            logger.exception("An error occurred while extracting a file.")
            raise

    def extract_all(self) -> Dict[str, bytes]:
        """
        Extracts all files from the ZIP archive.

        Returns:
            Dict[str, bytes]: A dictionary mapping file names to their extracted byte content.

        Raises:
            RuntimeError: If the ZIP archive could not be opened.
            Exception: For any other errors during extraction.
        """
        self._open_zip()

        if self.zip_file is None:
            raise RuntimeError("Failed to open the ZIP archive.")

        try:
            files = {
                name: self.zip_file.read(name) for name in self.zip_file.namelist()
            }
            logger.info(f"Successfully extracted {len(files)} files.")
            return files
        except Exception:
            logger.exception("An error occurred while extracting all files.")
            raise

    @classmethod
    def clear_cache(cls):
        for handler in cls._handler_cache.values():
            handler.close()
        cls._handler_cache.clear()
        logger.info("Cleared ZIP handler cache.")
