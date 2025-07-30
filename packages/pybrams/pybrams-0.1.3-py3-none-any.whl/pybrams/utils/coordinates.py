from __future__ import annotations
from dataclasses import dataclass
from math import cos, radians, sin, sqrt
from typing import Any, Dict, Union, ClassVar
import autograd.numpy as np
from pybrams.utils import Config


@dataclass
class GeodeticCoordinates:
    """Represents geographic coordinates: latitude, longitude, and altitude."""

    latitude: float
    longitude: float
    altitude: float

    def __json__(self) -> Dict[str, Any]:
        """Returns a JSON-serializable dictionary representation.

        Returns:
            Dict[str, Any]: The object's attributes as a dictionary.
        """
        return self.__dict__

    def __add__(self, o: GeodeticCoordinates) -> GeodeticCoordinates:
        """Adds two GeodeticCoordinates component-wise.

        Args:
            o (GeodeticCoordinates): Another geodetic coordinate.

        Returns:
            GeodeticCoordinates: The sum of both coordinates.
        """
        return GeodeticCoordinates(
            self.latitude + o.latitude,
            self.longitude + o.longitude,
            self.altitude + o.altitude,
        )

    def __sub__(self, o: GeodeticCoordinates) -> GeodeticCoordinates:
        """Subtracts two GeodeticCoordinates component-wise.

        Args:
            o (GeodeticCoordinates): Another geodetic coordinate.

        Returns:
            GeodeticCoordinates: The difference of both coordinates.
        """
        return GeodeticCoordinates(
            self.latitude - o.latitude,
            self.longitude - o.longitude,
            self.altitude - o.altitude,
        )

    def __eq__(self, other: object) -> bool:
        """Checks equality with another GeodeticCoordinates object.

        Args:
            other (object): The object to compare.

        Returns:
            bool: True if equal, False otherwise.
        """
        if isinstance(other, GeodeticCoordinates):
            return (
                self.latitude == other.latitude
                and self.longitude == other.longitude
                and self.altitude == other.altitude
            )

        return False


@dataclass
class CartesianCoordinates:
    """Represents Cartesian coordinates: x, y, and z."""

    x: float
    y: float
    z: float

    def __json__(self) -> Dict[str, float]:
        """Returns a JSON-serializable dictionary representation.

        Returns:
            Dict[str, float]: The object's attributes as a dictionary.
        """
        return self.__dict__

    def __add__(self, o: CartesianCoordinates) -> CartesianCoordinates:
        """Adds two CartesianCoordinates component-wise.

        Args:
            o (CartesianCoordinates): Another cartesian coordinate.

        Returns:
            CartesianCoordinates: The sum of both coordinates.
        """
        return CartesianCoordinates(self.x + o.x, self.y + o.y, self.z + o.z)

    def __sub__(self, o: CartesianCoordinates) -> CartesianCoordinates:
        """Subtracts two CartesianCoordinates component-wise.

        Args:
            o (CartesianCoordinates): Another cartesian coordinate.

        Returns:
            CartesianCoordinates: The difference of both coordinates.
        """
        return CartesianCoordinates(self.x - o.x, self.y - o.y, self.z - o.z)

    def __eq__(self, other: object) -> bool:
        """Checks equality with another CartesianCoordinates object.

        Args:
            other (object): The object to compare.

        Returns:
            bool: True if equal, False otherwise.
        """
        if isinstance(other, CartesianCoordinates):
            return self.x == other.x and self.y == other.y and self.z == other.z

        return False


@dataclass
class Coordinates:
    """Wrapper for geodetic, geocentric, and Dourbocentric coordinates."""

    dourbes_geodetic_coordinates: ClassVar[GeodeticCoordinates] = GeodeticCoordinates(
        50.097569, 4.588487, 0.167
    )

    geodetic: GeodeticCoordinates
    geocentric: CartesianCoordinates
    dourbocentric: CartesianCoordinates

    def __json__(self) -> Dict[str, Union[GeodeticCoordinates, CartesianCoordinates]]:
        """Returns a JSON-serializable dictionary representation.

        Returns:
            Dict[str, Union[GeodeticCoordinates, CartesianCoordinates]]: Attributes dictionary.
        """
        return self.__dict__

    def __eq__(self, other: object) -> bool:
        """Checks equality with another Coordinates object.

        Args:
            other (object): The object to compare.

        Returns:
            bool: True if equal, False otherwise.
        """
        if isinstance(other, Coordinates):
            return (
                self.geodetic == other.geodetic
                and self.geocentric == other.geocentric
                and self.dourbocentric == other.dourbocentric
            )

        return False

    @classmethod
    def dourbes_dourbocentric_coordinates(cls):
        """Computes the Dourbocentric coordinates of Dourbes itself.

        Returns:
            CartesianCoordinates: The zeroed local coordinate at Dourbes.
        """
        return cls.geodetic2Dourbocentric(cls.dourbes_geodetic_coordinates)

    @staticmethod
    def geodetic2Geocentric(coordinates: GeodeticCoordinates) -> CartesianCoordinates:
        """Converts geodetic coordinates to geocentric Cartesian coordinates.

        Args:
            coordinates (GeodeticCoordinates): Input latitude, longitude, and altitude.

        Returns:
            CartesianCoordinates: Converted Cartesian coordinates (ECEF).
        """
        φ = radians(coordinates.latitude)
        λ = radians(coordinates.longitude)
        sin_φ = sin(φ)
        a, rf = Config.get(__name__, "wgs84")  # semi-major axis, reciprocal flattening
        e2 = 1 - (1 - 1 / rf) ** 2  # eccentricity squared
        n = a / sqrt(1 - e2 * sin_φ**2)  # prime vertical radius
        # perpendicular distance from z axis
        r = (n + coordinates.altitude) * cos(φ)
        x = r * cos(λ)
        y = r * sin(λ)
        z = (n * (1 - e2) + coordinates.altitude) * sin_φ

        return CartesianCoordinates(x, y, z)

    @classmethod
    def geodetic2Dourbocentric(
        cls, geodetic: GeodeticCoordinates
    ) -> CartesianCoordinates:
        """Converts geodetic coordinates to local Dourbocentric coordinates.

        Args:
            geodetic (GeodeticCoordinates): Input geodetic coordinates.

        Returns:
            CartesianCoordinates: Dourbocentric coordinates relative to Dourbes.
        """
        DOURBES_GEOCENTRIC_COORDINATES = Coordinates.geodetic2Geocentric(
            cls.dourbes_geodetic_coordinates
        )

        φ = radians(geodetic.latitude)
        λ = radians(geodetic.longitude)

        translated = cls.geodetic2Geocentric(geodetic) - DOURBES_GEOCENTRIC_COORDINATES

        C1 = np.array([translated.x, translated.y, translated.z])

        # Rotation around Dzd with an angle lon
        RotMatPhi = np.array([[cos(λ), sin(λ), 0], [-sin(λ), cos(λ), 0], [0, 0, 1]])

        C2 = RotMatPhi @ C1

        # Rotation around Dyd with an angle lat
        RotMatPhi = np.array([[cos(φ), 0, sin(φ)], [0, 1, 0], [-sin(φ), 0, cos(φ)]])

        C3 = RotMatPhi @ C2

        return CartesianCoordinates(C3[1], C3[2], C3[0])

    @classmethod
    def fromGeodetic(
        cls, latitude: float, longitude: float, altitude: float
    ) -> Coordinates:
        geodeticCoordinates = GeodeticCoordinates(latitude, longitude, altitude)
        geocentricCoordinates = cls.geodetic2Geocentric(geodeticCoordinates)
        dourbocentricCoordinates = cls.geodetic2Dourbocentric(geodeticCoordinates)
        """Constructs a Coordinates instance from geodetic values.

        Args:
            latitude (float): Latitude in degrees.
            longitude (float): Longitude in degrees.
            altitude (float): Altitude in meters.

        Returns:
            Coordinates: A Coordinates object with all three coordinate systems populated.
        """
        return cls(geodeticCoordinates, geocentricCoordinates, dourbocentricCoordinates)

    def get_dourbocentric_array(self) -> np.ndarray:
        """Returns the Dourbocentric coordinates as a NumPy array.

        Returns:
            np.ndarray: Array [x, y, z] in Dourbocentric space.
        """
        return np.array(
            [self.dourbocentric.x, self.dourbocentric.y, self.dourbocentric.z]
        )
