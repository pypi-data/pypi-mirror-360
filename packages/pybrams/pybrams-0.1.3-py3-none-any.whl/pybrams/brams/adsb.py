from dataclasses import dataclass
import datetime
import json

from pybrams.utils.coordinates import Coordinates
from pybrams.utils.interval import Interval
from pybrams.brams.fetch import api
from typing import Dict, Any, List, Literal
from pybrams.utils import Config
from pybrams.utils import Cache
from pybrams.utils.cache import generate_key

import logging

logger = logging.getLogger(__name__)

api_endpoint = Config.get(__name__, "api_endpoint")


@dataclass
class Position:
    """
    Represents the position of an aircraft at a given time.

    Attributes:
        mode_s (str): The Mode-S identifier of the aircraft.
        dt (datetime.datetime): The timestamp of the position report.
        coordinates (Coordinates): The geodetic coordinates of the aircraft.
    """

    mode_s: str
    dt: datetime.datetime
    coordinates: Coordinates

    def json(self) -> Dict[str, Any]:
        """
        Serializes the position data to a dictionary format.

        Returns:
            dict: A JSON-serializable dictionary containing position data.
        """
        return {
            "mode_s": self.mode_s,
            "dt": self.dt.strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "coordinates": self.coordinates,
        }


def get(interval: Interval) -> Dict[str, List[Position]]:
    """
    Retrieves aircraft position data from the API over a given time interval.

    Args:
        interval (Interval): The datetime interval to query.

    Returns:
        dict: A dictionary where keys are Mode-S identifiers and values are lists of Position objects.
    """
    positions = {}

    if isinstance(interval, Interval):
        current_page = 1
        while True:
            payload = {
                "from": interval.start,
                "to": interval.end,
                "page": str(current_page),
                "limit": 2500,
            }

            try:
                response = api.request(api_endpoint, payload)
                json_response = response.json()

                for entry in json_response["data"]:
                    mode_s = entry["mode_s"]
                    year = entry["year"]
                    month = entry["month"]
                    day = entry["month"]
                    hours = entry["hours"]
                    minutes = entry["minutes"]
                    seconds = entry["seconds"]
                    microseconds = entry["microseconds"]
                    latitude = entry["latitude"]
                    longitude = entry["longitude"]
                    altitude = entry["altitude"]

                    dt = datetime.datetime(
                        year=year,
                        month=month,
                        day=day,
                        hour=hours,
                        minute=minutes,
                        second=seconds,
                        microsecond=microseconds,
                    )
                    coordinates = Coordinates.fromGeodetic(
                        latitude, longitude, altitude
                    )

                    if mode_s not in positions:
                        positions[mode_s] = []

                    positions[mode_s].append(Position(mode_s, dt, coordinates))

                current_page = int(json_response["pagination"]["current_page"])
                total_pages = int(json_response["pagination"]["total_pages"])

                if current_page == total_pages:
                    break

                current_page += 1

            except Exception:
                # todo : log error
                pass

    return positions


def availability(interval: Interval, key_format: Literal["str", "datetime"] = "str"):
    """
    Returns the availability of ADS-B data for each day within a given interval.

    Uses caching to avoid redundant API calls and supports formatting keys
    as either datetime objects or strings.

    Args:
        interval (Interval): The time interval to query.
        key_format (Literal["str", "datetime"], optional): Output key format. Defaults to "str".

    Returns:
        dict: A dictionary mapping each day in the interval to a boolean indicating availability.
              Keys are strings ("YYYY-MM-DD") or datetime objects, depending on `key_format`.

    Raises:
        TypeError: If `interval` is not an instance of Interval.
        ValueError: If no availability data is returned by the API.
    """
    if isinstance(interval, Interval):
        interval.start.replace(minute=0, second=0, microsecond=0)
        interval.end.replace(minute=0, second=0, microsecond=0)
        payload = {
            "from": interval.start,
            "to": interval.end,
            "availability": True,
        }

    else:
        raise TypeError("Unsupported type for 'interval' parameter")

    key = generate_key({**payload, "api_endpoint": "adsb"})
    cached_response = Cache.get(key)

    if cached_response:
        json_response = json.loads(cached_response)
    else:
        response = api.request(api_endpoint, payload)

        if not response:
            logging.error("No response from API")
            return {}
        json_response = response.json()
        Cache.cache(key, json.dumps(json_response, indent=4))

    if not json_response:
        raise ValueError("No ADSB availability was found with this interval")

    data = [
        datetime.datetime.strptime(date, "%Y-%m-%d").replace(
            tzinfo=datetime.timezone.utc
        )
        for date in json_response
    ]
    days = []
    dt = interval.start
    while dt < interval.end:
        days.append(dt)
        dt += datetime.timedelta(days=1)

    filled = {day: day in data for day in days}

    if key_format == "str":
        result = {
            day.strftime("%Y-%m-%d"): availability
            for day, availability in filled.items()
        }
        return result
    return filled
