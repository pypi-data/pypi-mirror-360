from __future__ import annotations
import ostk.core.type
import ostk.physics.environment.object
import ostk.physics.unit
import typing
from . import moon
from . import sun
__all__ = ['Earth', 'Moon', 'Sun', 'moon', 'sun']
class Earth(ostk.physics.environment.object.Celestial):
    """
    
                    Earth
                
    """
    @staticmethod
    def EGM2008(degree: ostk.core.type.Integer = ..., order: ostk.core.type.Integer = ...) -> Earth:
        """
                            Earth Gravity Model 2008 model (EGM2008).
        
                            Args:
                                degree (int): Degree.
                                order (int): Order.
        
                            Returns:
                                Earth: Earth.
        """
    @staticmethod
    def EGM84(degree: ostk.core.type.Integer = ..., order: ostk.core.type.Integer = ...) -> Earth:
        """
                            Earth Gravity Model 1984 (EGM84).
        
                            Args:
                                degree (int): Degree.
                                order (int): Order.
        
                            Returns:
                                Earth: Earth.
        """
    @staticmethod
    def EGM96(degree: ostk.core.type.Integer = ..., order: ostk.core.type.Integer = ...) -> Earth:
        """
                            Earth Gravity Model 1996 (EGM96).
        
                            Args:
                                degree (int): Degree.
                                order (int): Order.
        
                            Returns:
                                Earth: Earth.
        """
    @staticmethod
    def WGS84(degree: ostk.core.type.Integer = ..., order: ostk.core.type.Integer = ...) -> Earth:
        """
                            World Geodetic System 1984 (WGS84).
        
                            Args:
                                degree (int): Degree.
                                order (int): Order.
        
                            Returns:
                                Earth: Earth.
        """
    @staticmethod
    def WGS84_EGM96(degree: ostk.core.type.Integer = ..., order: ostk.core.type.Integer = ...) -> Earth:
        """
                            World Geodetic System 1984 (WGS84) + Earth Gravity Model 1996 (EGM96).
        
                            EGM96 coefficients and WGS84 shape.
                            Gravitational parameter: 398600441800000 [m^3/s^2].
                            Equatorial radius: 6378137.0 [m].
        
                            Args:
                                degree (int): Degree.
                                order (int): Order.
        
                            Returns:
                                Earth: Earth.
        """
    @staticmethod
    def atmospheric_only(atmospheric_model: typing.Any) -> Earth:
        """
                            Just atmospheric model.
        
                            Args:
                                atmospheric_model (EarthAtmosphericModel): Atmospheric model.
        
                            Returns:
                                Earth: Earth.
        """
    @staticmethod
    def default() -> Earth:
        """
                            Default Earth model (EGM2008).
        
                            Returns:
                                Earth: Earth
        """
    @staticmethod
    def from_models(gravity_model: typing.Any, magnetic_model: typing.Any, atmospheric_model: typing.Any) -> Earth:
        """
                            Create earth from specified models.
        
                            Args:
                                gravity_model (EarthGravitationalModel): Gravitational model.
                                magnetic_model (EarthMagneticModel): Magnetic model.
                                atmospheric_model (EarthAtmosphericModel): Atmospheric model.
        
                            Returns:
                                Earth: Earth.
        """
    @staticmethod
    def gravitational_only(gravity_model: typing.Any) -> Earth:
        """
                            Just gravity model.
        
                            Args:
                                gravity_model (EarthGravitationalModel): Gravitational model.
        
                            Returns:
                                Earth: Earth.
        """
    @staticmethod
    def magnetic_only(magnetic_model: typing.Any) -> Earth:
        """
                            Just magnetic model.
        
                            Args:
                                magnetic_model (EarthMagneticModel): Magnetic model.
        
                            Returns:
                                Earth: Earth.
        """
    @staticmethod
    def spherical() -> Earth:
        """
                            Spherical model.
        
                            Returns:
                                Earth: Earth.
        """
    @typing.overload
    def __init__(self, gravitational_parameter: ostk.physics.unit.Derived, equatorial_radius: ostk.physics.unit.Length, flattening: ostk.core.type.Real, J2_parameter_value: ostk.core.type.Real, J4_parameter_value: ostk.core.type.Real, ephemeris: typing.Any, gravitational_model: typing.Any, magnetic_model: typing.Any, atmospheric_model: typing.Any) -> None:
        """
                            Constructor
        
                            Args:
                                gravitational_parameter (Derived): Gravitational parameter [m³/s²].
                                equatorial_radius (Length): Equatorial radius [m].
                                flattening (Real): Flattening.
                                J2_parameter_value (Real): J2 parameter value.
                                J4_parameter_value (Real): J4 parameter value.
                                ephemeris (Ephemeris): Ephemeris.
                                gravitational_model (EarthGravitationalModel): Gravitational model.
                                magnetic_model (EarthMagneticModel): Magnetic model.
                                atmospheric_model (EarthAtmosphericModel): Atmospheric model.
        """
    @typing.overload
    def __init__(self, ephemeris: typing.Any, gravitational_model: typing.Any = None, magnetic_model: typing.Any = None, atmospheric_model: typing.Any = None) -> None:
        """
                            Constructor
        
                            Args:
                                ephemeris (Ephemeris): Ephemeris.
                                gravitational_model (EarthGravitationalModel): Gravitational model. Defaults to None.
                                magnetic_model (EarthMagneticModel): Magnetic model. Defaults to None.
                                atmospheric_model (EarthAtmosphericModel): Atmospheric model. Defaults to None.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
class Moon(ostk.physics.environment.object.Celestial):
    """
    
                    Moon.
                
    """
    @staticmethod
    def default() -> Moon:
        """
                            Create a default Moon.
        
                            Returns:
                                Moon: Default Moon.
        """
    @staticmethod
    def spherical() -> Moon:
        """
                            Spherical model.
        
                            Returns:
                                Moon: Moon.
        """
    def __init__(self, ephemeris: typing.Any, gravitational_model: typing.Any) -> None:
        """
                            Constructor.
        
                            Args:
                                ephemeris (Ephemeris): Ephemeris.
                                gravitational_model (MoonGravitationalModel): Gravitational model.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
class Sun(ostk.physics.environment.object.Celestial):
    """
    
                    Sun.
                
    """
    @staticmethod
    def default() -> Sun:
        """
                            Create a default Sun.
        
                            Returns:
                                Sun: Default Sun.
        """
    @staticmethod
    def spherical() -> Sun:
        """
                            Spherical model.
        
                            Returns:
                                Sun: Sun.
        """
    def __init__(self, ephemeris: typing.Any, gravitational_model: typing.Any) -> None:
        """
                            Constructor.
        
                            Args:
                                ephemeris (Ephemeris): Ephemeris.
                                gravitational_model (SunGravitationalModel): Gravitational model.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
