"""
Handles communication with the BRAMS downloader endpoint.

Provides a function to perform GET requests with optional payload parameters.
"""

from typing import Dict, Any, Optional
from pybrams.utils.http import get
import requests
import logging

logger = logging.getLogger(__name__)

base_url = "https://brams.aeronomie.be/downloader.php"


def request(payload: Optional[Dict[str, Any]] = None) -> requests.Response:
    """
    Send a GET request to the BRAMS downloader endpoint.

    Args:
        payload (Optional[Dict[str, Any]]): Optional query parameters to include in the request.

    Returns:
        requests.Response: The HTTP response from the downloader endpoint.
    """
    logger.debug(f"Calling downloader with payload {payload}")
    return get(base_url, payload)
