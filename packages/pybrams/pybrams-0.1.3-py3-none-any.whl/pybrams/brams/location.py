"""
location.py

Defines classes and functions to retrieve BRAMS location metadata from cache or API.
Provides a data model with geospatial coordinates, and access to associated systems.
"""

from typing import Any, Dict, TypedDict, Optional
from dataclasses import dataclass
import json
import datetime

from pybrams.utils.coordinates import Coordinates
from pybrams.utils import Cache
from pybrams.brams.fetch import api
from pybrams.utils import Config

api_endpoint = Config.get(__name__, "api_endpoint")


class LocationDict(TypedDict):
    """
    Dictionary-like structure representing the metadata of a BRAMS location.

    :key str location_code: Unique identifier for the location.
    :key str name: Human-readable name of the location.
    :key str status: Operational status of the location.
    :key float longitude: Longitude coordinate in degrees.
    :key float latitude: Latitude coordinate in degrees.
    :key int altitude: Altitude of the location in meters.
    :key str systems_url: URL to the systems endpoint for this location.
    """

    location_code: str
    name: str
    status: str
    longitude: float
    latitude: float
    altitude: int
    systems_url: str


@dataclass
class Location:
    """
    Represents a BRAMS location with geospatial attributes and system metadata.

    :param location_code: Unique identifier for the location.
    :param name: Display name of the location.
    :param status: Operational status (e.g., active, inactive).
    :param longitude: Longitude in degrees.
    :param latitude: Latitude in degrees.
    :param altitude: Altitude in meters above sea level.
    :param systems_url: URL for accessing associated systems for this location.
    """

    location_code: str
    name: str
    status: str
    longitude: float
    latitude: float
    altitude: int
    systems_url: str

    def __post_init__(self):
        """
        Compute the cartesian coordinates from geodetic latitude, longitude, and altitude
        after the Location instance is initialized.
        """

        self.coordinates = Coordinates.fromGeodetic(
            self.latitude, self.longitude, self.altitude
        )

    def json(self) -> Dict[str, Any]:
        """
        Convert the location object to a JSON-serializable dictionary.

        :return: Dictionary containing all public attributes of the location.
        """

        return {
            "location_code": self.location_code,
            "name": self.name,
            "status": self.status,
            "longitude": self.longitude,
            "latitude": self.latitude,
            "altitude": self.altitude,
            "systems_url": self.systems_url,
        }

    @property
    def systems(self):
        """
        Retrieve systems associated with this location.

        Systems are resolved dynamically through the BRAMS API.

        :return: Parsed system data for this location.
        """

        from pybrams.brams.system import get as get_system

        return get_system(location=self)


def get(location_code: str) -> Location:
    """
    Retrieve a location by its code.

    Tries cache first, then queries the BRAMS API if not cached.
    If the location is found, returns a `Location` instance.

    :param location_code: The location’s unique identifier.
    :return: Corresponding `Location` instance.
    :raises ValueError: If the location code is invalid or not found.
    """

    location: Optional[LocationDict] = None

    for key in [location_code, "locations"]:
        json_location = Cache.get(key)

        if json_location:
            location = json.loads(json_location).get("data").get(location_code)

            if location:
                break

    if not location:
        payload = {"location_code": location_code}

        response = api.request(api_endpoint, payload)
        json_location = response.json()

        if any(json_location.keys()):
            json_content = {
                "date": datetime.datetime.now(datetime.timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%S"
                ),
                "data": {location_code: json_location},
            }

            Cache.cache(location_code, json.dumps(json_content, indent=4))
            location = json_location

    if location:
        return Location(**location)

    else:
        raise ValueError(f"Invalid location code: {location_code}")


def all() -> Dict[str, Location]:
    """
    Retrieve all known locations from cache or the BRAMS API.

    Loads cached location data if available; otherwise, performs an API request.
    Returns a dictionary mapping location codes to `Location` instances.

    :return: Dictionary of all available locations.
    """

    json_locations = Cache.get("locations")

    if not json_locations:
        response = api.request(api_endpoint)
        json_locations = response.json() if response else []
        json_locations = {
            location["location_code"]: location for location in json_locations
        }

        json_content = {
            "date": datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S"
            ),
            "data": json_locations,
        }

        Cache.cache("locations", json.dumps(json_content, indent=4))

    else:
        json_locations = json.loads(json_locations).get("data")

    locations: Dict[str, Location] = {}

    for code, json_location in json_locations.items():
        locations[code] = Location(*json_location.values())

    return locations
