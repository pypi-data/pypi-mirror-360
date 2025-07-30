from __future__ import annotations
import ostk.core.type
import ostk.physics.coordinate
import ostk.physics.coordinate.spherical
import ostk.physics.environment.object
import ostk.physics.time
import ostk.physics.unit
import typing
from . import earth
__all__ = ['Earth', 'earth']
class Earth:
    """
    
                    Earth atmospheric model.
    
                
    """
    class InputDataType:
        """
        Members:
        
          Undefined : 
                            Undefined.
                        
        
          ConstantFluxAndGeoMag : 
                            Use constant values for F10.7, F10.7a and Kp NRLMSISE00 input parameters.
                        
        
          CSSISpaceWeatherFile : 
                            Use historical and predicted values for F10.7, F10.7a and Kp NRLMSISE00 input parameters from CSSI.
                        
        """
        CSSISpaceWeatherFile: typing.ClassVar[Earth.InputDataType]  # value = <InputDataType.CSSISpaceWeatherFile: 2>
        ConstantFluxAndGeoMag: typing.ClassVar[Earth.InputDataType]  # value = <InputDataType.ConstantFluxAndGeoMag: 1>
        Undefined: typing.ClassVar[Earth.InputDataType]  # value = <InputDataType.Undefined: 0>
        __members__: typing.ClassVar[dict[str, Earth.InputDataType]]  # value = {'Undefined': <InputDataType.Undefined: 0>, 'ConstantFluxAndGeoMag': <InputDataType.ConstantFluxAndGeoMag: 1>, 'CSSISpaceWeatherFile': <InputDataType.CSSISpaceWeatherFile: 2>}
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
    class Type:
        """
        Members:
        
          Undefined : 
                            Undefined.
                        
        
          Exponential : 
                            Exponential atmospheric density model, valid up to 1000 km.
                        
        
          NRLMSISE00 : 
                            Navy Research Lab Mass Spectrometer and Incoherent Scatter Radar Exosphere 2000.
                        
        """
        Exponential: typing.ClassVar[Earth.Type]  # value = <Type.Exponential: 1>
        NRLMSISE00: typing.ClassVar[Earth.Type]  # value = <Type.NRLMSISE00: 2>
        Undefined: typing.ClassVar[Earth.Type]  # value = <Type.Undefined: 0>
        __members__: typing.ClassVar[dict[str, Earth.Type]]  # value = {'Undefined': <Type.Undefined: 0>, 'Exponential': <Type.Exponential: 1>, 'NRLMSISE00': <Type.NRLMSISE00: 2>}
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
    def __init__(self, type: Earth.Type, input_data_type: Earth.InputDataType = ..., f107_constant_value: ostk.core.type.Real = 150.0, f107_average_constant_value: ostk.core.type.Real = 150.0, kp_constant_value: ostk.core.type.Real = 3.0, earth_frame: ostk.physics.coordinate.Frame = ..., earth_radius: ostk.physics.unit.Length = ..., earth_flattening: ostk.core.type.Real = ..., sun_celestial: ostk.physics.environment.object.Celestial = None) -> None:
        """
                            Constructor.
        
                        Args:
                            type (Earth.Type): Earth atmospheric model type.
                            input_data_type (Earth.InputDataType): Earth atmospheric model input data type.
                            f107_constant_value (Real): F10.7 constant value.
                            f107_average_constant_value (Real): F10.7a constant value.
                            kp_constant_value (Real): Kp constant value.
                            earth_frame (Frame): Earth frame.
                            earth_radius (Length): Earth radius [m].
                            earth_flattening (Real): Earth flattening.
                            sun_celestial (Celestial): Sun celestial object.
        
                        Returns:
                            Earth: Earth atmospheric model.
        """
    @typing.overload
    def get_density_at(self, position: ostk.physics.coordinate.Position, instant: ostk.physics.time.Instant) -> ostk.core.type.Real:
        """
                            Get the atmospheric density value at a given position and instant.
        
                            Args:
                                position (Position): A position.
                                instant (Instant): An instant.
        
                            Returns:
                                float: Atmospheric density value [kg.m^-3].
        """
    @typing.overload
    def get_density_at(self, lla: ostk.physics.coordinate.spherical.LLA, instant: ostk.physics.time.Instant) -> ostk.core.type.Real:
        """
                            Get the atmospheric density value at a given position and instant.
        
                            Args:
                                lla (LLA): A position, expressed as latitude, longitude, altitude [deg, deg, m].
                                instant (Instant): An instant.
        
                            Returns:
                                float: Atmospheric density value [kg.m^-3].
        """
    def get_input_data_type(self) -> Earth.InputDataType:
        """
                            Get the Earth atmospheric model input data type.
        
                            Returns:
                                Earth.InputDataType: Earth atmospheric model input data type.
        """
    def get_type(self) -> Earth.Type:
        """
                            Get the Earth atmospheric model type.
        
                            Returns:
                                Earth.Type: Earth atmospheric model type.
        """
    def is_defined(self) -> bool:
        """
                            Check if the Earth atmospheric model is defined.
        
                            Returns:
                                bool: True if defined.
        """
