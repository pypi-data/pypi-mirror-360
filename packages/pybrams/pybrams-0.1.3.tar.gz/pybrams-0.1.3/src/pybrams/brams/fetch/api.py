"""
Provides a simple interface for making POST requests to the BRAMS API.

Uses the base URL defined in the config and logs each request.
"""

from typing import Dict, Any, Optional
import requests
from pybrams.utils.http import post
import logging
from pybrams.utils import Config

logger = logging.getLogger(__name__)

base_url = Config.get(__name__, "base_url")


def request(
    endpoint: str, payload: Optional[Dict[str, Any]] = None
) -> requests.Response:
    """
    Send a POST request to a configured BRAMS API endpoint.

    Args:
        endpoint (str): The API endpoint path to call (e.g., "/stations/get").
        payload (dict, optional): A dictionary of parameters to send in the body.

    Returns:
        requests.Response: The HTTP response object returned by the API.

    Logs:
        Logs the endpoint and payload at debug level before sending the request.
    """
    logger.debug(f"Calling API {endpoint} with payload {payload}")
    return post(base_url + endpoint, payload)
