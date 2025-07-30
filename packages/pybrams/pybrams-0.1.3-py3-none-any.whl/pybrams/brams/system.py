from dataclasses import dataclass
import json
import datetime
from typing import Union, Dict, Optional, List, TypedDict, Any

from .location import Location, get as get_location
from pybrams.brams.fetch import api
from pybrams.utils import Cache
from pybrams.utils import Config

api_endpoint = Config.get(__name__, "api_endpoint")


class SystemDict(TypedDict):
    """
    Typed dictionary representing the structure of a BRAMS system
    as returned by the API or from cache.
    """

    system_code: str
    name: str
    start: str
    end: str
    antenna: int
    location_url: str
    location_code: str


@dataclass
class System:
    """
    Represents a BRAMS system with its metadata.

    Attributes:
        system_code (str): Unique identifier for the system (e.g., "RSP02").
        name (str): Full name of the system.
        start (str): Start date of operation (ISO 8601 format).
        end (str): End date of operation (ISO 8601 format).
        antenna (int): Antenna ID associated with the system.
        location_url (str): URL pointing to location metadata.
        location_code (str): Code representing the associated location.
    """

    system_code: str
    name: str
    start: str
    end: str
    antenna: int
    location_url: str
    location_code: str

    def json(self) -> Dict[str, Any]:
        """
        Serialize the system into a JSON-compatible dictionary.

        Returns:
            dict: A dictionary of the system’s attributes.
        """
        return {
            "system_code": self.system_code,
            "name": self.name,
            "start": self.start,
            "end": self.end,
            "antenna": self.antenna,
            "location_url": self.location_url,
            "location_code": self.location_code,
        }

    @property
    def location(self) -> Location:
        """
        Retrieve the associated Location object.

        Returns:
            Location: The location corresponding to `location_code`.
        """
        return get_location(self.location_code)

    def __eq__(self, other: object) -> bool:
        """
        Compare this system to another based on their `system_code`.

        Returns:
            bool: True if both systems share the same code, else False.
        """
        return isinstance(other, System) and self.system_code == other.system_code


def get(
    system_code: Optional[str] = None, location: Optional[Union[str, Location]] = None
) -> Dict[str, System]:
    """
    Retrieve system(s) either by system code or location.

    You must provide either `system_code` or `location`, but not both.

    Args:
        system_code (str, optional): Unique code identifying a system.
        location (str or Location, optional): Location code or Location object.

    Returns:
        dict[str, System]: A dictionary of systems keyed by `system_code`.

    Raises:
        ValueError: If neither or both arguments are provided, or if the code is invalid.
    """
    if location:
        location_code = (
            location if isinstance(location, str) else location.location_code
        )
        cached_systems = Cache.get("systems")

        if cached_systems:
            all_systems = json.loads(cached_systems).get("data")
            matching_systems = {
                system_code: System(*system.values())
                for system_code, system in all_systems.items()
                if system["location_code"] == location_code
            }

        else:
            payload = {"location_code": location_code}
            response = api.request(api_endpoint, payload)
            api_response: Union[SystemDict, List[SystemDict]] = (
                response.json() if response else []
            )

            if isinstance(api_response, dict):
                matching_systems = {api_response["system_code"]: System(**api_response)}

            else:
                matching_systems = {
                    system["system_code"]: System(**system) for system in api_response
                }

            for system_code, system in matching_systems.items():
                json_content = {
                    "date": datetime.datetime.now(datetime.timezone.utc).strftime(
                        "%Y-%m-%dT%H:%M:%S"
                    ),
                    "data": {system_code: system.json()},
                }

                Cache.cache(system_code, json.dumps(json_content, indent=4))

        return matching_systems

    elif system_code:
        system = {}

        for key in [system_code, "systems"]:
            json_system = Cache.get(key)

            if json_system:
                system = json.loads(json_system).get("data").get(system_code)

                if system:
                    break

        if not system:
            payload = {"system_code": system_code}

            response = api.request(api_endpoint, payload)
            json_system = response.json()

            json_content = {
                "date": datetime.datetime.now(datetime.timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%S"
                ),
                "data": {system_code: json_system},
            }

            Cache.cache(system_code, json.dumps(json_content, indent=4))
            system = json_system

            if not system:
                raise ValueError(f"Invalid system code: {system_code}")

        s = System(*system.values())
        return {s.system_code: s}

    else:
        raise ValueError("No location or system code was provided")


def all() -> Dict[str, System]:
    """
    Retrieve all BRAMS systems from cache or the API.

    Returns:
        dict[str, System]: All known systems, keyed by system code.
    """
    json_systems = Cache.get("systems")

    if not json_systems:
        response = api.request(api_endpoint)
        json_systems = {system["system_code"]: system for system in response.json()}

        json_content = {
            "date": datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S"
            ),
            "data": json_systems,
        }

        Cache.cache("systems", json.dumps(json_content, indent=4))

    else:
        json_systems = json.loads(json_systems).get("data")

    systems: dict[str, System] = {}

    for code, json_system in json_systems.items():
        systems[code] = System(*json_system.values())

    return systems
