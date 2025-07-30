from __future__ import annotations
import numpy
import ostk.core.type
import ostk.physics.unit
import typing
__all__ = ['AER', 'LLA']
class AER:
    """
    
                Azimuth - Elevation - Range (AER).
            
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def from_position_to_position(from_position: typing.Any, to_position: typing.Any, is_z_negative: bool = True) -> AER:
        """
                        Construct AER from position to position.
        
                        Args:
                            from_position (Position): From position.
                            to_position (Position): To position.
                            is_z_negative (bool): True if Z is negative.
        
                        Returns:
                            AER: AER.
        """
    @staticmethod
    def undefined() -> AER:
        """
                        Undefined AER.
        
                        Returns:
                            AER: Undefined AER.
        """
    @staticmethod
    def vector(vector: numpy.ndarray[numpy.float64[3, 1]]) -> AER:
        """
                        Construct AER from vector.
        
                        Args:
                            vector (np.ndarray): Vector.
        
                        Returns:
                            AER: AER.
        """
    def __eq__(self, arg0: AER) -> bool:
        """
                        Equality operator.
        
                        Args:
                            other (AER): Other AER.
        
                        Returns:
                            bool: True if equal.
        """
    def __init__(self, azimuth: ostk.physics.unit.Angle, elevation: ostk.physics.unit.Angle, range: ostk.physics.unit.Length) -> None:
        """
                        Construct an AER instance.
        
                        Args:
                            azimuth (Angle): Azimuth.
                            elevation (Angle): Elevation.
                            range (Length): Range.
        """
    def __ne__(self, arg0: AER) -> bool:
        """
                        Inequality operator.
        
                        Args:
                            other (AER): Other AER.
        
                        Returns:
                            bool: True if not equal.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def get_azimuth(self) -> ostk.physics.unit.Angle:
        """
                        Get azimuth.
        
                        Returns:
                            Angle: Azimuth.
        """
    def get_elevation(self) -> ostk.physics.unit.Angle:
        """
                        Get elevation.
        
                        Returns:
                            Angle: Elevation.
        """
    def get_range(self) -> ostk.physics.unit.Length:
        """
                        Get range.
        
                        Returns:
                            Length: Range.
        """
    def is_defined(self) -> bool:
        """
                        Check if defined.
        
                        Returns:
                            bool: True if defined.
        """
    def to_string(self) -> ostk.core.type.String:
        """
                        Convert to string.
        
                        Returns:
                            String: String representation.
        """
    def to_vector(self) -> numpy.ndarray[numpy.float64[3, 1]]:
        """
                        Convert to vector.
        
                        Returns:
                            np.ndarray: Vector.
        """
class LLA:
    """
    
                Geodetic Latitude - Longitude - Altitude (LLA).
    
                :reference: https://en.wikipedia.org/wiki/Latitude
                :reference: https://en.wikipedia.org/wiki/Longitude
            
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def azimuth_between(lla_1: LLA, lla_2: LLA, ellipsoid_equatorial_radius: ostk.physics.unit.Length = ..., ellipsoid_flattening: ostk.core.type.Real = ...) -> tuple[ostk.physics.unit.Angle, ostk.physics.unit.Angle]:
        """
                        Calculate the azimuth angles between two LLA coordinates.
                        If ellipsoid parameters are not provided, values from the global Environment central celestial are used. 
        
                        Args:
                            lla_1 (LLA): First LLA coordinate.
                            lla_2 (LLA): Second LLA coordinate.
                            ellipsoid_equatorial_radius (Length): Equatorial radius of the ellipsoid.
                            ellipsoid_flattening (float): Flattening of the ellipsoid.
        
                        Returns:
                            Angle: Azimuth.
        """
    @staticmethod
    def cartesian(cartesian_coordinates: numpy.ndarray[numpy.float64[3, 1]], ellipsoid_equatorial_radius: ostk.physics.unit.Length = ..., ellipsoid_flattening: ostk.core.type.Real = ...) -> LLA:
        """
                        Construct LLA from Cartesian.
                        If ellipsoid parameters are not provided, values from the global Environment central celestial are used. 
        
                        Args:
                            cartesian_coordinates (np.ndarray): Cartesian coordinates.
                            ellipsoid_equatorial_radius (Length): Equatorial radius of the ellipsoid.
                            ellipsoid_flattening (float): Flattening of the ellipsoid.
        
                        Returns:
                            LLA: LLA.
        """
    @staticmethod
    def distance_between(lla_1: LLA, lla_2: LLA, ellipsoid_equatorial_radius: ostk.physics.unit.Length = ..., ellipsoid_flattening: ostk.core.type.Real = ...) -> ostk.physics.unit.Length:
        """
                        Calculate the distance between two LLA coordinates.
                        If ellipsoid parameters are not provided, values from the global Environment central celestial are used. 
        
                        Args:
                            lla_1 (LLA): First LLA coordinate.
                            lla_2 (LLA): Second LLA coordinate.
                            ellipsoid_equatorial_radius (Length): Equatorial radius of the ellipsoid.
                            ellipsoid_flattening (float): Flattening of the ellipsoid.
        
                        Returns:
                            Length: Distance.
        """
    @staticmethod
    def forward(lla: LLA, azimuth: ostk.physics.unit.Angle, distance: ostk.physics.unit.Length, ellipsoid_equatorial_radius: ostk.physics.unit.Length = ..., ellipsoid_flattening: ostk.core.type.Real = ...) -> LLA:
        """
                        Propagate an LLA coordinate in provided direction and distance.
                        If ellipsoid parameters are not provided, values from the global Environment central celestial are used. 
        
                        Args:
                            lla (LLA): LLA coordinate.
                            azimuth (Angle): Azimuth.
                            distance (Length): Distance.
                            ellipsoid_equatorial_radius (Length): Equatorial radius of the ellipsoid.
                            ellipsoid_flattening (float): Flattening of the ellipsoid.
        
                        Returns:
                            LLA: Propagated LLA coordinate.
        """
    @staticmethod
    def from_position(position: typing.Any, celestial: typing.Any = None) -> LLA:
        """
                        Construct LLA from position.
        
                        Args:
                            position (Position): Position.
                            celestial (Celestial): Celestial object. Defaults to None, in which case, values from the global Environment central celestial are used. 
        
                        Returns:
                            LLA: LLA.
        """
    @staticmethod
    def intermediate_between(lla_1: LLA, lla_2: LLA, ratio: ostk.core.type.Real, ellipsoid_equatorial_radius: ostk.physics.unit.Length = ..., ellipsoid_flattening: ostk.core.type.Real = ...) -> LLA:
        """
                        Calculate a point between two LLA coordinates.
                        If ellipsoid parameters are not provided, values from the global Environment central celestial are used. 
        
                        Args:
                            lla_1 (LLA): First LLA coordinate.
                            lla_2 (LLA): Second LLA coordinate.
                            ratio (Real): Ratio.
                            ellipsoid_equatorial_radius (Length): Equatorial radius of the ellipsoid.
                            ellipsoid_flattening (float): Flattening of the ellipsoid.
        
                        Returns:
                            LLA: A point between the two LLA coordinates.
        """
    @staticmethod
    def linspace(lla_1: LLA, lla_2: LLA, number_of_points: int, ellipsoid_equatorial_radius: ostk.physics.unit.Length = ..., ellipsoid_flattening: ostk.core.type.Real = ...) -> list[LLA]:
        """
                        Generate LLAs between two LLA coordinates at a given interval.
                        If ellipsoid parameters are not provided, values from the global Environment central celestial are used. 
        
                        Args:
                            lla_1 (LLA): First LLA coordinate.
                            lla_2 (LLA): Second LLA coordinate.
                            number_of_points (Size): Number of points.
                            ellipsoid_equatorial_radius (Length): Equatorial radius of the ellipsoid.
                            ellipsoid_flattening (float): Flattening of the ellipsoid.
        
                        Returns:
                            list[LLA]: List of LLA coordinates.
        """
    @staticmethod
    def undefined() -> LLA:
        """
                        Undefined LLA.
        
                        Returns:
                            LLA: Undefined LLA.
        """
    @staticmethod
    def vector(vector: numpy.ndarray[numpy.float64[3, 1]]) -> LLA:
        """
                        Construct LLA from vector.
        
                        Args:
                            vector (np.ndarray): Vector.
        
                        Returns:
                            LLA: LLA.
        """
    def __eq__(self, arg0: LLA) -> bool:
        """
                        Equality operator.
        
                        Args:
                            other (LLA): Other LLA.
        
                        Returns:
                            bool: True if equal.
        """
    def __init__(self, latitude: ostk.physics.unit.Angle, longitude: ostk.physics.unit.Angle, altitude: ostk.physics.unit.Length) -> None:
        """
                        Construct an LLA instance.
        
                        Args:
                            latitude (Angle): Latitude.
                            longitude (Angle): Longitude.
                            altitude (Length): Altitude.
        """
    def __ne__(self, arg0: LLA) -> bool:
        """
                        Inequality operator.
        
                        Args:
                            other (LLA): Other LLA.
        
                        Returns:
                            bool: True if not equal.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def calculate_azimuth_to(self, lla: LLA, ellipsoid_equatorial_radius: ostk.physics.unit.Length = ..., ellipsoid_flattening: ostk.core.type.Real = ...) -> tuple[ostk.physics.unit.Angle, ostk.physics.unit.Angle]:
        """
                        Calculate the azimuth angles between this LLA coordinate and another LLA coordinate.
                        If ellipsoid parameters are not provided, values from the global Environment central celestial are used. 
        
                        Args:
                            lla (LLA): Another LLA coordinate.
                            ellipsoid_equatorial_radius (Length): Equatorial radius of the ellipsoid.
                            ellipsoid_flattening (float): Flattening of the ellipsoid.
        
                        Returns:
                            Angle: Azimuth.
        """
    def calculate_distance_to(self, lla: LLA, ellipsoid_equatorial_radius: ostk.physics.unit.Length = ..., ellipsoid_flattening: ostk.core.type.Real = ...) -> ostk.physics.unit.Length:
        """
                        Calculate the distance between this LLA coordinate and another LLA coordinate.
                        If ellipsoid parameters are not provided, values from the global Environment central celestial are used. 
        
                        Args:
                            lla (LLA): Another LLA coordinate.
                            ellipsoid_equatorial_radius (Length): Equatorial radius of the ellipsoid.
                            ellipsoid_flattening (float): Flattening of the ellipsoid.
        
                        Returns:
                            Length: Distance.
        """
    def calculate_forward(self, azimuth: ostk.physics.unit.Angle, distance: ostk.physics.unit.Length, ellipsoid_equatorial_radius: ostk.physics.unit.Length = ..., ellipsoid_flattening: ostk.core.type.Real = ...) -> LLA:
        """
                        Propagate this LLA coordinate in provided direction and distance.
                        If ellipsoid parameters are not provided, values from the global Environment central celestial are used. 
        
                        Args:
                            azimuth (Angle): Azimuth.
                            distance (Length): Distance.
                            ellipsoid_equatorial_radius (Length): Equatorial radius of the ellipsoid.
                            ellipsoid_flattening (float): Flattening of the ellipsoid.
        
                        Returns:
                            LLA: Propagated LLA coordinate.
        """
    def calculate_intermediate_to(self, lla: LLA, ratio: ostk.core.type.Real, ellipsoid_equatorial_radius: ostk.physics.unit.Length = ..., ellipsoid_flattening: ostk.core.type.Real = ...) -> LLA:
        """
                        Calculate a point between this LLA coordinate and another LLA coordinate.
                        If ellipsoid parameters are not provided, values from the global Environment central celestial are used. 
        
                        Args:
                            lla (LLA): Another LLA coordinate.
                            ratio (Real): Ratio.
                            ellipsoid_equatorial_radius (Length): Equatorial radius of the ellipsoid.
                            ellipsoid_flattening (float): Flattening of the ellipsoid.
        
                        Returns:
                            LLA: A point between the two LLA coordinates.
        """
    def calculate_linspace_to(self, lla: LLA, number_of_points: int, ellipsoid_equatorial_radius: ostk.physics.unit.Length = ..., ellipsoid_flattening: ostk.core.type.Real = ...) -> list[LLA]:
        """
                        Generate LLAs between this LLA coordinate and another LLA coordinate at a given interval.
                        If ellipsoid parameters are not provided, values from the global Environment central celestial are used. 
        
                        Args:
                            lla (LLA): Another LLA coordinate.
                            number_of_points (Size): Number of points.
                            ellipsoid_equatorial_radius (Length): Equatorial radius of the ellipsoid.
                            ellipsoid_flattening (float): Flattening of the ellipsoid.
        
                        Returns:
                            list[LLA]: List of LLA coordinates.
        """
    def get_altitude(self) -> ostk.physics.unit.Length:
        """
                        Get altitude.
        
                        Returns:
                            Length: Altitude.
        """
    def get_latitude(self) -> ostk.physics.unit.Angle:
        """
                        Get latitude.
        
                        Returns:
                            Angle: Latitude.
        """
    def get_longitude(self) -> ostk.physics.unit.Angle:
        """
                        Get longitude.
        
                        Returns:
                            Angle: Longitude.
        """
    def is_defined(self) -> bool:
        """
                        Check if defined.
        
                        Returns:
                            bool: True if defined.
        """
    def on_surface(self) -> LLA:
        """
                        Get LLA on surface (Altitude is 0.0).
        
                        Returns:
                            LLA: LLA on surface.
        """
    def to_cartesian(self, ellipsoid_equatorial_radius: ostk.physics.unit.Length = ..., ellipsoid_flattening: ostk.core.type.Real = ...) -> numpy.ndarray[numpy.float64[3, 1]]:
        """
                        Convert to Cartesian.
                        If ellipsoid parameters are not provided, values from the global Environment central celestial are used. 
        
                        Args:
                            ellipsoid_equatorial_radius (Length): Equatorial radius of the ellipsoid.
                            ellipsoid_flattening (float): Flattening of the ellipsoid.
        
                        Returns:
                            np.ndarray: Cartesian.
        """
    def to_string(self) -> ostk.core.type.String:
        """
                        Convert to string.
        
                        Returns:
                            String: String representation.
        """
    def to_vector(self) -> numpy.ndarray[numpy.float64[3, 1]]:
        """
                        Convert to vector.
        
                        Returns:
                            np.ndarray: Vector.
        """
