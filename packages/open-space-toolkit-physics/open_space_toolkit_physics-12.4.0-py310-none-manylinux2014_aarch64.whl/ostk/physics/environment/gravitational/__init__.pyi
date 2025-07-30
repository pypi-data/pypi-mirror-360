from __future__ import annotations
import numpy
import ostk.core.filesystem
import ostk.core.type
import ostk.physics.time
import ostk.physics.unit
import typing
from . import earth
__all__ = ['Earth', 'GravitationalParameters', 'Model', 'Moon', 'Spherical', 'Sun', 'earth']
class Earth(Model):
    """
    
                    Earth gravitational model.
    
                    The gravitational potential is expanded as sum of spherical harmonics.
    
                    :reference: https://en.wikipedia.org/wiki/Spherical_harmonics
                    :reference: https://geographiclib.sourceforge.io/html/gravity.html
                
    """
    class Type:
        """
        Members:
        
          Undefined : 
                            Undefined.
                        
        
          Spherical : 
                            The spherical gravity originating from a point source at the center of the Earth.
                        
        
          WGS84 : 
                            The normal gravitational field for the reference ellipsoid. This includes the zonal coefficients up to order 20.
                        
        
          EGM84 : 
                            The Earth Gravity Model 1984, which includes terms up to degree 180.
                        
        
          WGS84_EGM96 : 
                            The normal gravitational field for the reference ellipsoid plus the Earth Gravity Model 1996,
                            which includes terms up to degree 360.
                        
        
          EGM96 : 
                            The Earth Gravity Model 1996, which includes terms up to degree 360.
                        
        
          EGM2008 : 
                            The Earth Gravity Model 2008, which includes terms up to degree 2190.
                        
        """
        EGM2008: typing.ClassVar[Earth.Type]  # value = <Type.EGM2008: 6>
        EGM84: typing.ClassVar[Earth.Type]  # value = <Type.EGM84: 3>
        EGM96: typing.ClassVar[Earth.Type]  # value = <Type.EGM96: 5>
        Spherical: typing.ClassVar[Earth.Type]  # value = <Type.Spherical: 1>
        Undefined: typing.ClassVar[Earth.Type]  # value = <Type.Undefined: 0>
        WGS84: typing.ClassVar[Earth.Type]  # value = <Type.WGS84: 2>
        WGS84_EGM96: typing.ClassVar[Earth.Type]  # value = <Type.WGS84_EGM96: 4>
        __members__: typing.ClassVar[dict[str, Earth.Type]]  # value = {'Undefined': <Type.Undefined: 0>, 'Spherical': <Type.Spherical: 1>, 'WGS84': <Type.WGS84: 2>, 'EGM84': <Type.EGM84: 3>, 'WGS84_EGM96': <Type.WGS84_EGM96: 4>, 'EGM96': <Type.EGM96: 5>, 'EGM2008': <Type.EGM2008: 6>}
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
    EGM2008: typing.ClassVar[GravitationalParameters]  # value = -- Gravitational Model Parameters ------------------------------------------------------------------...
    EGM84: typing.ClassVar[GravitationalParameters]  # value = -- Gravitational Model Parameters ------------------------------------------------------------------...
    EGM96: typing.ClassVar[GravitationalParameters]  # value = -- Gravitational Model Parameters ------------------------------------------------------------------...
    WGS84: typing.ClassVar[GravitationalParameters]  # value = -- Gravitational Model Parameters ------------------------------------------------------------------...
    WGS84_EGM96: typing.ClassVar[GravitationalParameters]  # value = -- Gravitational Model Parameters ------------------------------------------------------------------...
    gravity_constant: typing.ClassVar[float] = 9.80665
    spherical: typing.ClassVar[GravitationalParameters]  # value = -- Gravitational Model Parameters ------------------------------------------------------------------...
    @typing.overload
    def __init__(self, type: typing.Any, directory: ostk.core.filesystem.Directory) -> None:
        """
                            Construct an Earth gravitational model.
        
                            Args:
                                type (Earth.Type): Earth model type.
                                directory (Directory): Directory containing the gravity model data files.
        """
    @typing.overload
    def __init__(self, type: typing.Any) -> None:
        """
                            Construct an Earth gravitational model.
        
                            Args:
                                type (Earth.Type): Earth model type.
        """
    @typing.overload
    def __init__(self, type: typing.Any, directory: ostk.core.filesystem.Directory, gravitational_model_degree: ostk.core.type.Integer, gravitational_model_order: ostk.core.type.Integer) -> None:
        """
                            Construct an Earth gravitational model.
        
                            Args:
                                type (Earth.Type): Earth model type.
                                directory (Directory): Directory containing the gravity model data files.
                                gravitational_model_degree (int): Degree of the gravitational model.
                                gravitational_model_order (int): Order of the gravitational model.
        """
    @typing.overload
    def __init__(self, type: typing.Any, gravitational_model_degree: ostk.core.type.Integer, gravitational_model_order: ostk.core.type.Integer) -> None:
        """
                            Construct an Earth gravitational model.
        
                            Args:
                                type (Earth.Type): Earth model type.
                                gravitational_model_degree (int): Degree of the gravitational model.
                                gravitational_model_order (int): Order of the gravitational model.
        """
    def get_degree(self) -> ostk.core.type.Integer:
        """
                            Get the Earth model degree.
        
                            Returns:
                                int: Earth model degree.
        """
    def get_field_value_at(self, position: numpy.ndarray[numpy.float64[3, 1]], instant: ostk.physics.time.Instant) -> numpy.ndarray[numpy.float64[3, 1]]:
        """
                            Get the gravitational field value at a given position and instant.
        
                            Args:
                                position (Position): A position.
                                instant (Instant): An instant.
        
                            Returns:
                                np.ndarray: Gravitational field value [m.s^-2].
        """
    def get_order(self) -> ostk.core.type.Integer:
        """
                            Get the Earth model order.
        
                            Returns:
                                int: Earth model order.
        """
    def get_type(self) -> ...:
        """
                            Get the Earth model type.
        
                            Returns:
                                Earth.Type: Earth model type.
        """
    def is_defined(self) -> bool:
        """
                            Check if the Earth model is defined.
        
                            Returns:
                                bool: True if the model is defined.
        """
class GravitationalParameters:
    """
    
                    Gravitational model parameters.
    
                
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def undefined() -> GravitationalParameters:
        """
                            Get undefined parameters.
        
                            Returns:
                                GravitationalParameters: Undefined parameters.
        """
    def __eq__(self, arg0: GravitationalParameters) -> bool:
        """
                            Equal to operator
                            
                            Args:
                                other (GravitationalParameters): Other parameters.
        
                            Returns:
                                bool: True if equal
        """
    @typing.overload
    def __init__(self, gravitational_parameter: ostk.physics.unit.Derived, equatorial_radius: ostk.physics.unit.Length, flattening: ostk.core.type.Real, C20: ostk.core.type.Real, C40: ostk.core.type.Real) -> None:
        """
                            Constructor.
        
                            Args:
                                gravitational_parameter (Derived): Gravitational parameter [m^3/s^2].
                                equatorial_radius (Length): Equatorial radius [m].
                                flattening (Real): Flattening.
                                C20 (Real): C20.
                                C40 (Real): C40.
        """
    @typing.overload
    def __init__(self, gravitational_parameter: ostk.physics.unit.Derived, equatorial_radius: ostk.physics.unit.Length, flattening: ostk.core.type.Real, C20: ostk.core.type.Real, C30: ostk.core.type.Real, C40: ostk.core.type.Real) -> None:
        """
                            Constructor.
        
                            Args:
                                gravitational_parameter (Derived): Gravitational parameter [m^3/s^2].
                                equatorial_radius (Length): Equatorial radius [m].
                                flattening (Real): Flattening.
                                C20 (Real): C20.
                                C30 (Real): C30.
                                C40 (Real): C40.
        """
    def __ne__(self, arg0: GravitationalParameters) -> bool:
        """
                            Not equal to operator
                            
                            Args:
                                other (GravitationalParameters): Other parameters.
        
                            Returns:
                                bool: True if not equal
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def compute_geocentric_radius_at(self, latitude: ostk.physics.unit.Angle) -> ostk.physics.unit.Length:
        """
                            Compute geocentric radius of ellipsoid at a given latitude.
        
                            Args:
                                latitude (Angle): A latitude.
        
                            Returns:
                                Length: Geocentric radius of ellipsoid at a given latitude.
        """
    def is_defined(self) -> bool:
        """
                            Check if the parameters are defined.
        
                            Returns:
                                bool: True if defined.
        """
    @property
    def C20(self) -> ostk.core.type.Real:
        """
                            C20.
        """
    @C20.setter
    def C20(self, arg0: ostk.core.type.Real) -> None:
        ...
    @property
    def C30(self) -> ostk.core.type.Real:
        """
                            C30.
        """
    @C30.setter
    def C30(self, arg0: ostk.core.type.Real) -> None:
        ...
    @property
    def C40(self) -> ostk.core.type.Real:
        """
                            C40.
        """
    @C40.setter
    def C40(self, arg0: ostk.core.type.Real) -> None:
        ...
    @property
    def J2(self) -> ostk.core.type.Real:
        """
                            J2.
        """
    @J2.setter
    def J2(self, arg0: ostk.core.type.Real) -> None:
        ...
    @property
    def J3(self) -> ostk.core.type.Real:
        """
                            J3.
        """
    @J3.setter
    def J3(self, arg0: ostk.core.type.Real) -> None:
        ...
    @property
    def J4(self) -> ostk.core.type.Real:
        """
                            J4.
        """
    @J4.setter
    def J4(self, arg0: ostk.core.type.Real) -> None:
        ...
    @property
    def equatorial_radius(self) -> ostk.physics.unit.Length:
        """
                            Equatorial radius [m].
        """
    @equatorial_radius.setter
    def equatorial_radius(self, arg0: ostk.physics.unit.Length) -> None:
        ...
    @property
    def flattening(self) -> ostk.core.type.Real:
        """
                            Flattening.
        """
    @flattening.setter
    def flattening(self, arg0: ostk.core.type.Real) -> None:
        ...
    @property
    def gravitational_parameter(self) -> ostk.physics.unit.Derived:
        """
                            Gravitational parameter [m^3/s^2].
        """
    @gravitational_parameter.setter
    def gravitational_parameter(self, arg0: ostk.physics.unit.Derived) -> None:
        ...
class Model:
    """
    
                    Earth Gravitational model.
                
    """
    def get_parameters(self) -> ...:
        ...
class Moon(Model):
    """
    
                    Moon gravitational model.
    
                    The gravitational potential of the Moon for now is kept as a simple spherical model.
                
    """
    class Type:
        """
        Members:
        
          Undefined : 
                            Undefined Moon model type.
                        
        
          Spherical : 
                            Spherical Moon model type.
                        
        """
        Spherical: typing.ClassVar[Moon.Type]  # value = <Type.Spherical: 1>
        Undefined: typing.ClassVar[Moon.Type]  # value = <Type.Undefined: 0>
        __members__: typing.ClassVar[dict[str, Moon.Type]]  # value = {'Undefined': <Type.Undefined: 0>, 'Spherical': <Type.Spherical: 1>}
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
    spherical: typing.ClassVar[GravitationalParameters]  # value = -- Gravitational Model Parameters ------------------------------------------------------------------...
    @typing.overload
    def __init__(self, type: typing.Any, directory: ostk.core.filesystem.Directory) -> None:
        """
                            Construct a Moon gravitational model.
        
                            Args:
                                type (Moon.Type): Moon model type.
                                directory (Directory): Directory containing the gravity model data files.
        """
    @typing.overload
    def __init__(self, type: typing.Any) -> None:
        """
                            Construct a Moon gravitational model.
        
                            Args:
                                type (Moon.Type): Moon model type.
        """
    def get_field_value_at(self, position: numpy.ndarray[numpy.float64[3, 1]], instant: ostk.physics.time.Instant) -> numpy.ndarray[numpy.float64[3, 1]]:
        """
                            Get the gravitational field value at a position.
        
                            Args:
                                position (np.ndarray): A position.
                                instant (Instant): An instant.
        
                            Returns:
                                np.ndarray: Gravitational field value.
        """
    def get_type(self) -> ...:
        """
                            Get the Moon model type.
        
                            Returns:
                                Moon.Type: Moon model type.
        """
    def is_defined(self) -> bool:
        """
                            Check if the Moon model is defined.
        
                            Returns:
                                bool: True if defined.
        """
class Spherical(Model):
    """
    
                Spherical gravitational model.
    
            
    """
    def __init__(self, gravitational_parameters: GravitationalParameters) -> None:
        """
                        Construct a Spherical gravitational model.
        
                        Args:
                            gravitational_parameters (GravitationalParameters): Gravitational model parameters.
        """
    def get_field_value_at(self, position: numpy.ndarray[numpy.float64[3, 1]], instant: ostk.physics.time.Instant) -> numpy.ndarray[numpy.float64[3, 1]]:
        """
                        Get the gravitational field value at a given position and instant.
        
                        Args:
                            position (np.ndarray): Position, expressed in the gravitational object frame [m].
                            instant (Instant): Instant.
        
                        Returns:
                            np.ndarray: Gravitational field value, expressed in the gravitational object frame [m.s-2].
        """
    def is_defined(self) -> bool:
        """
                        Check if the Spherical gravitational model is defined.
        
                        Returns:
                            bool: True if the Spherical gravitational model is defined.
        """
class Sun(Model):
    """
    
                    Sun gravitational model.
    
                    The gravitational potential of the Sun for now is kept as a simple spherical model.
                
    """
    class Type:
        """
        Members:
        
          Undefined : 
                            Undefined.
                        
        
          Spherical : 
                            The spherical gravity originating from a point source at the center of the Sun.
                        
        """
        Spherical: typing.ClassVar[Sun.Type]  # value = <Type.Spherical: 1>
        Undefined: typing.ClassVar[Sun.Type]  # value = <Type.Undefined: 0>
        __members__: typing.ClassVar[dict[str, Sun.Type]]  # value = {'Undefined': <Type.Undefined: 0>, 'Spherical': <Type.Spherical: 1>}
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
    spherical: typing.ClassVar[GravitationalParameters]  # value = -- Gravitational Model Parameters ------------------------------------------------------------------...
    @typing.overload
    def __init__(self, type: typing.Any, directory: ostk.core.filesystem.Directory) -> None:
        """
                            Construct a Sun gravitational model.
        
                            Args:
                                type (Sun.Type): Sun model type.
                                directory (Directory): Directory containing the gravity model data files.
        """
    @typing.overload
    def __init__(self, type: typing.Any) -> None:
        """
                            Construct a Sun gravitational model.
        
                            Args:
                                type (Sun.Type): Sun model type.
        """
    def get_field_value_at(self, position: numpy.ndarray[numpy.float64[3, 1]], instant: ostk.physics.time.Instant) -> numpy.ndarray[numpy.float64[3, 1]]:
        """
                            Get the gravitational field value at a given position and instant.
        """
    def get_type(self) -> ...:
        """
                            Get the Sun model type.
        
                            Returns:
                                Sun.Type: Sun model type.
        """
    def is_defined(self) -> bool:
        """
                            Check if the Sun model is defined.
        
                            Returns:
                                bool: True if defined.
        """
