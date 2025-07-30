from __future__ import annotations
import ostk.core.type
import ostk.mathematics.geometry.d3
import ostk.mathematics.geometry.d3.object
import ostk.physics.coordinate
import ostk.physics.coordinate.spherical
import ostk.physics.environment
import ostk.physics.time
import ostk.physics.unit
import typing
from . import celestial
__all__ = ['Celestial', 'Geometry', 'celestial']
class Celestial(ostk.physics.environment.Object):
    """
    
                Celestial class
            
    """
    class CelestialType:
        """
        Members:
        
          Undefined : 
                        Undefined celestial object.
                    
        
          Sun : 
                        Sun.
                    
        
          Mercury : 
                        Mercury.
                    
        
          Venus : 
                        Venus.
                    
        
          Earth : 
                        Earth.
                    
        
          Moon : 
                        Moon.
                    
        
          Mars : 
                        Mars.
                    
        """
        Earth: typing.ClassVar[Celestial.CelestialType]  # value = <CelestialType.Earth: 4>
        Mars: typing.ClassVar[Celestial.CelestialType]  # value = <CelestialType.Mars: 6>
        Mercury: typing.ClassVar[Celestial.CelestialType]  # value = <CelestialType.Mercury: 2>
        Moon: typing.ClassVar[Celestial.CelestialType]  # value = <CelestialType.Moon: 5>
        Sun: typing.ClassVar[Celestial.CelestialType]  # value = <CelestialType.Sun: 1>
        Undefined: typing.ClassVar[Celestial.CelestialType]  # value = <CelestialType.Undefined: 0>
        Venus: typing.ClassVar[Celestial.CelestialType]  # value = <CelestialType.Venus: 3>
        __members__: typing.ClassVar[dict[str, Celestial.CelestialType]]  # value = {'Undefined': <CelestialType.Undefined: 0>, 'Sun': <CelestialType.Sun: 1>, 'Mercury': <CelestialType.Mercury: 2>, 'Venus': <CelestialType.Venus: 3>, 'Earth': <CelestialType.Earth: 4>, 'Moon': <CelestialType.Moon: 5>, 'Mars': <CelestialType.Mars: 6>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    class FrameType:
        """
        Members:
        
          Undefined : 
                        Undefined frame.
                    
        
          NED : 
                        North-East-Down (NED) frame.
                    
        """
        NED: typing.ClassVar[Celestial.FrameType]  # value = <FrameType.NED: 1>
        Undefined: typing.ClassVar[Celestial.FrameType]  # value = <FrameType.Undefined: 0>
        __members__: typing.ClassVar[dict[str, Celestial.FrameType]]  # value = {'Undefined': <FrameType.Undefined: 0>, 'NED': <FrameType.NED: 1>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    @staticmethod
    def string_from_frame_type(frame_type: typing.Any) -> ostk.core.type.String:
        """
                        Get the string representation of a frame type.
        
                        Args:
                            frame_type (Celestial.FrameType): Frame type.
        
                        Returns:
                            str: String representation.
        """
    @staticmethod
    def undefined() -> Celestial:
        """
                        Create an undefined celestial object.
        
                        Returns:
                            Celestial: Undefined celestial object.
        """
    @typing.overload
    def __init__(self, name: ostk.core.type.String, type: typing.Any, gravitational_parameter: ostk.physics.unit.Derived, equatorial_radius: ostk.physics.unit.Length, flattening: ostk.core.type.Real, J2_parameter_value: ostk.core.type.Real, J4_parameter_value: ostk.core.type.Real, ephemeris: typing.Any, gravitational_model: typing.Any, magnetic_model: typing.Any, atmospheric_model: typing.Any) -> None:
        """
                        Constructor
        
                        Args:
                            name (str): Name.
                            type (CelestialType): Type.
                            gravitational_parameter (Derived): Gravitational parameter [m³/s²].
                            equatorial_radius (Length): Equatorial radius [m].
                            flattening (Real): Flattening.
                            J2_parameter_value (Real): J2 parameter value.
                            J4_parameter_value (Real): J4 parameter value.
                            ephemeris (Ephemeris): Ephemeris.
                            gravitational_model (GravitationalModel): Gravitational model.
                            magnetic_model (MagneticModel): Magnetic model.
                            atmospheric_model (AtmosphericModel): Atmospheric model.
        """
    @typing.overload
    def __init__(self, name: ostk.core.type.String, type: typing.Any, gravitational_parameter: ostk.physics.unit.Derived, equatorial_radius: ostk.physics.unit.Length, flattening: ostk.core.type.Real, J2_parameter_value: ostk.core.type.Real, J4_parameter_value: ostk.core.type.Real, ephemeris: typing.Any, gravitational_model: typing.Any, magnetic_model: typing.Any, atmospheric_model: typing.Any, geometry: Geometry) -> None:
        """
                        Constructor
        
                        Args:
                            name (str): Name.
                            type (CelestialType): Type.
                            gravitational_parameter (Derived): Gravitational parameter [m³/s²].
                            equatorial_radius (Length): Equatorial radius [m].
                            flattening (Real): Flattening.
                            J2_parameter_value (Real): J2 parameter value.
                            J4_parameter_value (Real): J4 parameter value.
                            ephemeris (Ephemeris): Ephemeris
                            gravitational_model (GravitationalModel): Gravitational model.
                            magnetic_model (MagneticModel): Magnetic model.
                            atmospheric_model (AtmosphericModel): Atmospheric model.
                            geometry (Object.Geometry): Geometry.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def access_atmospheric_model(self) -> ...:
        """
                        Access the atmospheric model.
        
                        Returns:
                            Atmospheric: Atmospheric model.
        """
    def access_ephemeris(self) -> ...:
        """
                        Access the ephemeris.
        
                        Returns:
                            Ephemeris: Ephemeris.
        """
    def access_gravitational_model(self) -> ...:
        """
                        Access the gravitational model.
        
                        Returns:
                            Gravitational: Gravitational model.
        """
    def access_magnetic_model(self) -> ...:
        """
                        Access the magnetic model.
        
                        Returns:
                            Magnetic: Magnetic model.
        """
    def atmospheric_model_is_defined(self) -> bool:
        """
                        Check if the atmospheric model is defined.
        
                        Returns:
                            bool: True if the atmospheric model is defined, false otherwise.
        """
    def get_axes_in(self, frame: ostk.physics.coordinate.Frame, instant: ostk.physics.time.Instant) -> ostk.physics.coordinate.Axes:
        """
                        Get the axes of the celestial object in a given frame at a given instant.
        
                        Args:
                            frame (Frame): Frame.
                            instant (Instant): Instant.
        
                        Returns:
                            Axes: Axes.
        """
    def get_equatorial_radius(self) -> ostk.physics.unit.Length:
        """
                        Get the equatorial radius of the celestial object.
        
                        Returns:
                            Length: Equatorial radius [m].
        """
    def get_flattening(self) -> ostk.core.type.Real:
        """
                        Get the flattening of the celestial object.
        
                        Returns:
                            float: Flattening.
        """
    def get_frame_at(self, lla: ostk.physics.coordinate.spherical.LLA, frame_type: typing.Any) -> ostk.physics.coordinate.Frame:
        """
                        Get the frame at a given LLA and frame type.
        
                        Args:
                            lla (LLA): LLA
                            frame_type (Celestial.FrameType): Frame type
        
                        Returns:
                            Frame: Frame.
        """
    def get_gravitational_parameter(self) -> ostk.physics.unit.Derived:
        """
                        Get the gravitational parameter of the celestial object.
        
                        Returns:
                            Derived: Gravitational parameter [m³/s²].
        """
    def get_j2(self) -> ostk.core.type.Real:
        """
                        Get the J2 parameter value of the celestial object.
        
                        Returns:
                            float: J2 parameter value.
        """
    def get_j4(self) -> ostk.core.type.Real:
        """
                        Get the J4 parameter value of the celestial object.
        
                        Returns:
                            float: J4 parameter value.
        """
    def get_position_in(self, frame: ostk.physics.coordinate.Frame, instant: ostk.physics.time.Instant) -> ostk.physics.coordinate.Position:
        """
                        Get the position of the celestial object in a given frame at a given instant.
        
                        Args:
                            frame (Frame): Frame.
                            instant (Instant): Instant.
        
                        Returns:
                            Position: Position.
        """
    def get_transform_to(self, frame: ostk.physics.coordinate.Frame, instant: ostk.physics.time.Instant) -> ostk.physics.coordinate.Transform:
        """
                        Get the transform of the celestial object to a given frame at a given instant.
        
                        Args:
                            frame (Frame): Frame.
                            instant (Instant): Instant.
        
                        Returns:
                            Transform: Transform.
        """
    def get_type(self) -> ...:
        """
                        Get the type of the celestial object.
        
                        Returns:
                            Celestial.Type: Type.
        """
    def gravitational_model_is_defined(self) -> bool:
        """
                        Check if the gravitational model is defined.
        
                        Returns:
                            bool: True if the gravitational model is defined, false otherwise.
        """
    def is_defined(self) -> bool:
        """
                        Check if the celestial object is defined.
        
                        Returns:
                            bool: True if the celestial object is defined, false otherwise.
        """
    def magnetic_model_is_defined(self) -> bool:
        """
                        Check if the magnetic model is defined.
        
                        Returns:
                            bool: True if the magnetic model is defined, false otherwise.
        """
class Geometry:
    """
    
                Geometry.
            
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def undefined() -> Geometry:
        """
                        Constructs an undefined geometry.
        
                        Returns:
                            Geometry: Undefined geometry.
        """
    def __eq__(self, arg0: Geometry) -> bool:
        ...
    @typing.overload
    def __init__(self, arg0: ostk.mathematics.geometry.d3.object.Composite, arg1: ostk.physics.coordinate.Frame) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: ostk.mathematics.geometry.d3.Object, arg1: ostk.physics.coordinate.Frame) -> None:
        ...
    def __ne__(self, arg0: Geometry) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def access_composite(self) -> ostk.mathematics.geometry.d3.object.Composite:
        """
                        Access composite.
        
                        Returns:
                            Composite: Composite.
        """
    def access_frame(self) -> ostk.physics.coordinate.Frame:
        """
                        Access frame.
        
                        Returns:
                            Frame: Frame.
        """
    def contains(self, arg0: Geometry) -> bool:
        """
                        Check if the geometry contains a point.
        
                        Args:
                            aPoint (Point): A point.
        
                        Returns:
                            bool: True if geometry contains point.
        """
    def in_frame(self, arg0: ostk.physics.coordinate.Frame, arg1: ostk.physics.time.Instant) -> Geometry:
        """
                        Get geometry expressed in a given frame.
        
                        Args:
                            aFrame (Frame): Frame.
                            anInstant (Instant): An instant.
        
                        Returns:
                            Geometry: Geometry expressed in a given frame.
        """
    def intersection_with(self, arg0: Geometry) -> Geometry:
        """
                        Compute intersection of geometry with another geometry.
        
                        Args:
                            aGeometry (Geometry): Another geometry.
        
                        Returns:
                            Geometry: Intersection of geometry with another geometry.
        """
    def intersects(self, arg0: Geometry) -> bool:
        """
                        Check if the geometry intersects with another geometry.
        
                        Args:
                            aGeometry (Geometry): Another geometry.
        
                        Returns:
                            bool: True if geometries intersect.
        """
    def is_defined(self) -> bool:
        """
                        Check if the geometry is defined.
        
                        Returns:
                            bool: True if defined.
        """
