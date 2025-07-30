from __future__ import annotations
import numpy
import ostk.core.type
import ostk.mathematics.geometry.d3.transformation.rotation
import ostk.physics.time
import ostk.physics.unit
import typing
from . import frame
from . import spherical
__all__ = ['Axes', 'Frame', 'Position', 'Transform', 'Velocity', 'frame', 'spherical']
class Axes:
    """
    
                Axes.
    
            
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def undefined() -> Axes:
        """
                        Get undefined axes.
        
                        Returns:
                            Axes: Undefined axes.
        """
    def __eq__(self, arg0: Axes) -> bool:
        """
                        Equality operator.
        
                        Args:
                            other (Axes): Other Axes.
        
                        Returns:
                            bool: True if equal.
        """
    def __init__(self, x_axis: numpy.ndarray[numpy.float64[3, 1]], y_axis: numpy.ndarray[numpy.float64[3, 1]], z_axis: numpy.ndarray[numpy.float64[3, 1]], frame: Frame) -> None:
        """
                        Constructor.
        
                    Args:
                        x_axis (np.ndarray): X-axis.
                        y_axis (np.ndarray): Y-axis.
                        z_axis (np.ndarray): Z-axis.
                        frame (Frame): Frame of reference.
        """
    def __ne__(self, arg0: Axes) -> bool:
        """
                        Inequality operator.
        
                        Args:
                            other (Axes): Other Axes.
        
                        Returns:
                            bool: True if not equal.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def get_frame(self) -> Frame:
        """
                        Get the frame of reference.
        
                        Returns:
                            Frame: Frame of reference.
        """
    def in_frame(self, frame: Frame, instant: ostk.physics.time.Instant) -> Axes:
        """
                        Get the axes in another frame of reference.
        
                        Args:
                            frame (Frame): Frame of reference.
                            instant (Instant): Instant.
        
                        Returns:
                            Axes: Axes in the other frame of reference.
        """
    def is_defined(self) -> bool:
        """
                        Check if defined.
        
                        Returns:
                            bool: True if defined.
        """
    def x(self) -> numpy.ndarray[numpy.float64[3, 1]]:
        """
                        Get the X-axis.
        
                    Returns:
                        np.ndarray: X-axis.
        """
    def y(self) -> numpy.ndarray[numpy.float64[3, 1]]:
        """
                        Get the Y-axis.
        
                    Returns:
                        np.ndarray: Y-axis.
        """
    def z(self) -> numpy.ndarray[numpy.float64[3, 1]]:
        """
                        Get the Z-axis.
        
                    Returns:
                        np.ndarray: Z-axis.
        """
class Frame:
    """
    
                Reference frame
    
                :reference: https://en.wikipedia.org/wiki/Frame_of_reference
    
                :note: Implementation heavily inspired by (the great!) https://www.orekit.org/static/architecture/frames.html
    
                
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def CIRF() -> Frame:
        """
                        Get the Celestial Intermediate Reference Frame (CIRF).
        
                        Returns:
                            Frame: CIRF.
        """
    @staticmethod
    def GCRF() -> Frame:
        """
                        Get the Geocentric Celestial Reference Frame (GCRF).
        
                        Returns:
                            Frame: GCRF.
        """
    @staticmethod
    def ITRF() -> Frame:
        """
                        Get the International Terrestrial Reference Frame (ITRF).
        
                        Returns:
                            Frame: ITRF.
        """
    @staticmethod
    def J2000(theory: typing.Any) -> Frame:
        """
                        Get the J2000 frame.
        
                        Args:
                            theory (Theory): Theory.
        
                        Returns:
                            Frame: J2000.
        """
    @staticmethod
    def MOD(epoch: ostk.physics.time.Instant) -> Frame:
        """
                        Get the MOD frame.
        
                        Args:
                            epoch (Instant): Epoch.
        
                        Returns:
                            Frame: MOD.
        """
    @staticmethod
    def TEME() -> Frame:
        """
                        Get the True Equator Mean Equinox (TEME) frame.
        
                        Returns:
                            Frame: TEME.
        """
    @staticmethod
    def TEME_of_epoch(epoch: ostk.physics.time.Instant) -> Frame:
        """
                        Get the True Equator Mean Equinox (TEME) frame of epoch.
        
                        Args:
                            epoch (Instant): Epoch.
        
                        Returns:
                            Frame: TEME of epoch.
        """
    @staticmethod
    def TIRF() -> Frame:
        """
                        Get the Terrestrial Intermediate Reference Frame (TIRF).
        
                        Returns:
                            Frame: TIRF.
        """
    @staticmethod
    def TOD(epoch: ostk.physics.time.Instant, theory: typing.Any) -> Frame:
        """
                        Get the TOD frame.
        
                        Args:
                            epoch (Instant): Epoch.
                            theory (Theory): Theory.
        
                        Returns:
                            Frame: TOD.
        """
    @staticmethod
    def construct(name: ostk.core.type.String, is_quasi_inertial: bool, parent_frame: Frame, provider: typing.Any) -> Frame:
        """
                        Construct a frame.
        
                        Args:
                            name (String): Name.
                            is_quasi_inertial (bool): True if quasi-inertial.
                            parent_frame (Frame): Parent frame.
                            provider (Provider): Provider.
        
                        Returns:
                            Frame: Frame.
        """
    @staticmethod
    def destruct(name: ostk.core.type.String) -> None:
        """
                        Destruct a frame.
        
                        Args:
                            name (String): Name.
        """
    @staticmethod
    def exists(name: ostk.core.type.String) -> bool:
        """
                        Check if a frame exists.
        
                        Args:
                            name (String): Name.
        
                        Returns:
                            bool: True if exists.
        """
    @staticmethod
    def undefined() -> Frame:
        """
                        Get undefined frame.
        
                        Returns:
                            Frame: Undefined frame.
        """
    @staticmethod
    def with_name(name: ostk.core.type.String) -> Frame:
        """
                        Get the frame with a given name.
        
                        Args:
                            name (String): Name.
        
                        Returns:
                            Frame: Frame.
        """
    def __eq__(self, arg0: Frame) -> bool:
        """
                        Equality operator.
        
                        Args:
                            other (Frame): Other frame.
        
                        Returns:
                            bool: True if equal.
        """
    def __ne__(self, arg0: Frame) -> bool:
        """
                        Inequality operator.
        
                        Args:
                            other (Frame): Other frame.
        
                        Returns:
                            bool: True if not equal.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def access_ancestor(self, ancestor_degree: int) -> Frame:
        """
                        Access the ancestor frame.
        
                        Args:
                            ancestor_degree (int): Ancestor degree.
        
                        Returns:
                            Frame: Ancestor frame.
        """
    def access_parent(self) -> Frame:
        """
                        Access the parent frame.
        
                        Returns:
                            Frame: Parent frame.
        """
    def access_provider(self) -> ...:
        """
                        Access the provider.
        
                        Returns:
                            Provider: Provider.
        """
    def get_axes_in(self, frame: Frame, instant: ostk.physics.time.Instant) -> ...:
        """
                        Get the axes in another frame.
        
                        Args:
                            frame (Frame): Frame.
                            instant (Instant): Instant.
        
                        Returns:
                            Axes: Axes.
        """
    def get_name(self) -> ostk.core.type.String:
        """
                        Get the name.
        
                        Returns:
                            String: Name.
        """
    def get_origin_in(self, frame: Frame, instant: ostk.physics.time.Instant) -> Position:
        """
                        Get the origin in another frame.
        
                        Args:
                            frame (Frame): Frame.
                            instant (Instant): Instant.
        
                        Returns:
                            Position: Origin.
        """
    def get_transform_to(self, frame: Frame, instant: ostk.physics.time.Instant) -> ...:
        """
                        Get the transformation to another frame.
        
                        Args:
                            frame (Frame): Frame.
                            instant (Instant): Instant.
        
                        Returns:
                            Transform: Transformation.
        """
    def get_velocity_in(self, frame: Frame, instant: ostk.physics.time.Instant) -> Velocity:
        """
                        Get the velocity in another frame.
        
                        Args:
                            frame (Frame): Frame.
                            instant (Instant): Instant.
        
                        Returns:
                            Velocity: Velocity.
        """
    def has_parent(self) -> bool:
        """
                        Check if the frame has a parent.
        
                        Returns:
                            bool: True if the frame has a parent.
        """
    def is_defined(self) -> bool:
        """
                        Check if the instance is defined.
        
                        Returns:
                            bool: True if the instance is defined.
        """
    def is_quasi_inertial(self) -> bool:
        """
                        Check if the frame is quasi-inertial.
        
                        Returns:
                            bool: True if the frame is quasi-inertial.
        """
class Position:
    """
    
                Position.
            
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def from_lla(lla: spherical.LLA, celestial: typing.Any = None) -> Position:
        """
                        Create a Position from LLA.
        
                        Args:
                            lla (LLA): LLA.
                            celestial_object (Celestial): Celestial object. Defaults to None. If None, the central body from the global environment instance will be used if it's available.
        
                        Returns:
                            Position: Position.
        """
    @staticmethod
    def meters(coordinates: numpy.ndarray[numpy.float64[3, 1]], frame: typing.Any) -> Position:
        """
                        Create a Position in meters.
        
                        Args:
                            coordinates (np.ndarray): Coordinates.
                            frame (Frame): Frame of reference.
        
                        Returns:
                            Position: Position in meters.
        """
    @staticmethod
    def undefined() -> Position:
        """
                        Get undefined Position.
        
                        Returns:
                            Position: Undefined Position.
        """
    def __eq__(self, arg0: Position) -> bool:
        """
                        Equality operator.
        
                        Args:
                            other (Position): Other Position.
        
                        Returns:
                            bool: True if equal.
        """
    def __init__(self, coordinates: numpy.ndarray[numpy.float64[3, 1]], unit: ostk.physics.unit.Length.Unit, frame: typing.Any) -> None:
        """
                        Constructs a Position.
        
                        Args:
                            coordinates (np.ndarray): Coordinates.
                            unit (Unit): Unit.
                            frame (Frame): Frame of reference.
        """
    def __ne__(self, arg0: Position) -> bool:
        """
                        Inequality operator.
        
                        Args:
                            other (Position): Other Position.
        
                        Returns:
                            bool: True if not equal.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def access_frame(self) -> ...:
        """
                        Access the frame of reference.
        
                        Returns:
                            Frame: Frame of reference.
        """
    def get_coordinates(self) -> numpy.ndarray[numpy.float64[3, 1]]:
        """
                        Get the coordinates.
        
                        Returns:
                            np.ndarray: Coordinates.
        """
    def get_unit(self) -> ostk.physics.unit.Length.Unit:
        """
                        Get the unit.
        
                        Returns:
                            Unit: Unit.
        """
    def in_frame(self, frame: typing.Any, instant: ostk.physics.time.Instant) -> Position:
        """
                        Get the Position in another frame of reference.
        
                        Args:
                            frame (Frame): Frame of reference.
                            instant (Instant): Instant.
        
                        Returns:
                            Position: Position in another frame of reference.
        """
    def in_meters(self) -> Position:
        """
                        Get the Position in meters.
        
                        Returns:
                            Position: Position in meters.
        """
    def in_unit(self, arg0: ostk.physics.unit.Length.Unit) -> Position:
        """
                        Get the Position in the unit.
        
                        Returns:
                            Position: Position in the unit.
        """
    def is_defined(self) -> bool:
        """
                        Check if the Position is defined.
        
                        Returns:
                            bool: True if the Position is defined.
        """
    def is_near(self, position: Position, tolerance: ostk.physics.unit.Length) -> bool:
        """
                        Check if the Position is near another Position.
        
                        Args:
                            position (Position): Position to compare with.
                            tolerance (Length): Tolerance.
        
                        Returns:
                            bool: True if the Position is near another Position.
        """
    def to_string(self, precision: ostk.core.type.Integer = ...) -> ostk.core.type.String:
        """
                        Create a string representation.
        
                        Args:
                            precision (Integer): Precision.
        
                        Returns:
                            String: String representation.
        """
class Transform:
    """
    
                Transform.
    
                :reference: https://en.wikipedia.org/wiki/Active_and_passive_transformation
                :reference: https://core.ac.uk/download/pdf/77055186.pdf
            
    """
    class Type:
        """
        
                    Transform type.
                
        
        Members:
        
          Undefined : 
                        Undefined type.
                    
        
          Active : 
                        Active type.
                    
        
          Passive : 
                        Passive type.
                    
        """
        Active: typing.ClassVar[Transform.Type]  # value = <Type.Active: 1>
        Passive: typing.ClassVar[Transform.Type]  # value = <Type.Passive: 2>
        Undefined: typing.ClassVar[Transform.Type]  # value = <Type.Undefined: 0>
        __members__: typing.ClassVar[dict[str, Transform.Type]]  # value = {'Undefined': <Type.Undefined: 0>, 'Active': <Type.Active: 1>, 'Passive': <Type.Passive: 2>}
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
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def active(instant: ostk.physics.time.Instant, translation: numpy.ndarray[numpy.float64[3, 1]], velocity: numpy.ndarray[numpy.float64[3, 1]], orientation: ostk.mathematics.geometry.d3.transformation.rotation.Quaternion, angular_velocity: numpy.ndarray[numpy.float64[3, 1]]) -> Transform:
        """
                        Create an active transform.
        
                        Args:
                            instant (Instant): Instant.
                            translation (np.ndarray): Translation.
                            velocity (np.ndarray): Velocity.
                            orientation (Quaternion): Orientation.
                            angular_velocity (np.ndarray): Angular velocity.
        
                        Returns:
                            Transform: Active transform.
        """
    @staticmethod
    def identity(arg0: ostk.physics.time.Instant) -> Transform:
        """
                        Get identity transform.
        
                        Returns:
                            Transform: Identity transform.
        """
    @staticmethod
    def passive(instant: ostk.physics.time.Instant, translation: numpy.ndarray[numpy.float64[3, 1]], velocity: numpy.ndarray[numpy.float64[3, 1]], orientation: ostk.mathematics.geometry.d3.transformation.rotation.Quaternion, angular_velocity: numpy.ndarray[numpy.float64[3, 1]]) -> Transform:
        """
                        Create a passive transform.
        
                        Args:
                            instant (Instant): Instant.
                            translation (np.ndarray): Translation.
                            velocity (np.ndarray): Velocity.
                            orientation (Quaternion): Orientation.
                            angular_velocity (np.ndarray): Angular velocity.
        
                        Returns:
                            Transform: Passive transform.
        """
    @staticmethod
    def undefined() -> Transform:
        """
                        Get undefined transform.
        
                        Returns:
                            Transform: Undefined transform.
        """
    def __eq__(self, arg0: Transform) -> bool:
        """
                        Equality operator.
        
                        Args:
                            other (Transform): Other transform.
        
                        Returns:
                            bool: True if equal.
        """
    def __imul__(self, arg0: Transform) -> Transform:
        """
                        Multiplication assignment operator.
        
                        Args:
                            other (Transform): Other transform.
        
                        Returns:
                            Transform: Composition.
        """
    def __init__(self, instant: ostk.physics.time.Instant, translation: numpy.ndarray[numpy.float64[3, 1]], velocity: numpy.ndarray[numpy.float64[3, 1]], orientation: ostk.mathematics.geometry.d3.transformation.rotation.Quaternion, angular_velocity: numpy.ndarray[numpy.float64[3, 1]], type: typing.Any) -> None:
        """
                        Constructs a transform.
        
                        Args:
                            instant (Instant): Instant.
                            translation (np.ndarray): Translation.
                            velocity (np.ndarray): Velocity.
                            orientation (Quaternion): Orientation.
                            angular_velocity (np.ndarray): Angular velocity.
                            type (Type): Type.
        """
    def __mul__(self, arg0: Transform) -> Transform:
        """
                        Multiplication operator.
        
                        Args:
                            other (Transform): Other transform.
        
                        Returns:
                            Transform: Composition.
        """
    def __ne__(self, arg0: Transform) -> bool:
        """
                        Inequality operator.
        
                        Args:
                            other (Transform): Other transform.
        
                        Returns:
                            bool: True if not equal.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def access_angular_velocity(self) -> numpy.ndarray[numpy.float64[3, 1]]:
        """
                        Access the angular velocity.
        
                        Returns:
                            np.ndarray: Angular velocity.
        """
    def access_instant(self) -> ostk.physics.time.Instant:
        """
                        Access the instant.
        
                        Returns:
                            Instant: Instant.
        """
    def access_orientation(self) -> ostk.mathematics.geometry.d3.transformation.rotation.Quaternion:
        """
                        Access the orientation.
        
                        Returns:
                            Quaternion: Orientation.
        """
    def access_translation(self) -> numpy.ndarray[numpy.float64[3, 1]]:
        """
                        Access the translation.
        
                        Returns:
                            np.ndarray: Translation.
        """
    def access_velocity(self) -> numpy.ndarray[numpy.float64[3, 1]]:
        """
                        Access the velocity.
        
                        Returns:
                            np.ndarray: Velocity.
        """
    def apply_to_position(self, position: numpy.ndarray[numpy.float64[3, 1]]) -> numpy.ndarray[numpy.float64[3, 1]]:
        """
                        Apply the transform to a position.
        
                        Args:
                            position (Position): Position.
        
                        Returns:
                            np.ndarray: Transformed position.
        """
    def apply_to_vector(self, vector: numpy.ndarray[numpy.float64[3, 1]]) -> numpy.ndarray[numpy.float64[3, 1]]:
        """
                        Apply the transform to a vector.
        
                        Args:
                            vector (np.ndarray): Vector.
        
                        Returns:
                            np.ndarray: Transformed vector.
        """
    def apply_to_velocity(self, position: numpy.ndarray[numpy.float64[3, 1]], velocity: numpy.ndarray[numpy.float64[3, 1]]) -> numpy.ndarray[numpy.float64[3, 1]]:
        """
                        Apply the transform to a velocity.
        
                        Args:
                            position (Position): Position.
                            velocity (Velocity): Velocity.
        
                        Returns:
                            np.ndarray: Transformed velocity.
        """
    def get_angular_velocity(self) -> numpy.ndarray[numpy.float64[3, 1]]:
        """
                        Get the angular velocity.
        
                        Returns:
                            np.ndarray: Angular velocity.
        """
    def get_instant(self) -> ostk.physics.time.Instant:
        """
                        Get the instant.
        
                        Returns:
                            Instant: Instant.
        """
    def get_inverse(self) -> Transform:
        """
                        Get the inverse.
        
                        Returns:
                            Transform: Inverse.
        """
    def get_orientation(self) -> ostk.mathematics.geometry.d3.transformation.rotation.Quaternion:
        """
                        Get the orientation.
        
                        Returns:
                            Quaternion: Orientation.
        """
    def get_translation(self) -> numpy.ndarray[numpy.float64[3, 1]]:
        """
                        Get the translation.
        
                        Returns:
                            np.ndarray: Translation.
        """
    def get_velocity(self) -> numpy.ndarray[numpy.float64[3, 1]]:
        """
                        Get the velocity.
        
                        Returns:
                            np.ndarray: Velocity.
        """
    def is_defined(self) -> bool:
        """
                        Check if the transform is defined.
        
                        Returns:
                            bool: True if the transform is defined.
        """
    def is_identity(self) -> bool:
        """
                        Check if the transform is the identity.
        
                        Returns:
                            bool: True if the transform is the identity.
        """
class Velocity:
    """
    
                Velocity.
            
    """
    class Unit:
        """
        
                    Velocity unit.
                
        
        Members:
        
          Undefined : 
                        Undefined.
                    
        
          MeterPerSecond : 
                        Meter per second.
                    
        """
        MeterPerSecond: typing.ClassVar[Velocity.Unit]  # value = <Unit.MeterPerSecond: 1>
        Undefined: typing.ClassVar[Velocity.Unit]  # value = <Unit.Undefined: 0>
        __members__: typing.ClassVar[dict[str, Velocity.Unit]]  # value = {'Undefined': <Unit.Undefined: 0>, 'MeterPerSecond': <Unit.MeterPerSecond: 1>}
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
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def meters_per_second(coordinates: numpy.ndarray[numpy.float64[3, 1]], frame: typing.Any) -> Velocity:
        """
                        Create a velocity in meters per second.
        
                        Args:
                            coordinates (np.ndarray): Coordinates.
                            frame (Frame): Frame of reference.
        
                        Returns:
                            Velocity: Velocity in meters per second.
        """
    @staticmethod
    def string_from_unit(unit: typing.Any) -> ostk.core.type.String:
        """
                        Create a string from unit.
        
                        Args:
                            unit (Unit): Unit.
        
                        Returns:
                            String: String.
        """
    @staticmethod
    def undefined() -> Velocity:
        """
                        Get undefined velocity.
        
                        Returns:
                            Velocity: Undefined velocity.
        """
    def __eq__(self, arg0: Velocity) -> bool:
        """
                        Equality operator.
        
                        Args:
                            other (Velocity): Other velocity.
        
                        Returns:
                            bool: True if equal.
        """
    def __init__(self, coordinates: numpy.ndarray[numpy.float64[3, 1]], unit: typing.Any, frame: typing.Any) -> None:
        """
                        Constructs a velocity.
        
                        Args:
                            coordinates (np.ndarray): Coordinates.
                            unit (Unit): Unit.
                            frame (Frame): Frame of reference.
        """
    def __ne__(self, arg0: Velocity) -> bool:
        """
                        Inequality operator.
        
                        Args:
                            other (Velocity): Other velocity.
        
                        Returns:
                            bool: True if not equal.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def access_frame(self) -> ...:
        """
                        Access the frame of reference.
        
                        Returns:
                            Frame: Frame of reference.
        """
    def get_coordinates(self) -> numpy.ndarray[numpy.float64[3, 1]]:
        """
                        Get the coordinates.
        
                        Returns:
                            np.ndarray: Coordinates.
        """
    def get_unit(self) -> ...:
        """
                        Get the unit.
        
                        Returns:
                            Unit: Unit.
        """
    def in_frame(self, position: Position, frame: typing.Any, instant: ostk.physics.time.Instant) -> Velocity:
        """
                        Convert to frame.
        
                        Args:
                            position (Position): Position.
                            frame (Frame): Frame.
                            instant (Instant): Instant.
        
                        Returns:
                            Velocity: Velocity.
        """
    def in_unit(self, unit: typing.Any) -> Velocity:
        """
                        Convert to unit.
        
                        Args:
                            unit (Unit): Unit.
        
                        Returns:
                            Velocity: Velocity.
        """
    def is_defined(self) -> bool:
        """
                        Check if the instance is defined.
        
                        Returns:
                            bool: True if the instance is defined.
        """
    def to_string(self, precision: ostk.core.type.Integer = ...) -> ostk.core.type.String:
        """
                        Convert to string.
        
                        Args:
                            precision (int): Precision.
        
                        Returns:
                            String: String.
        """
