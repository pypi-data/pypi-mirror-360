from __future__ import annotations
import numpy
import ostk.core.filesystem
import ostk.physics.time
import typing
from . import earth
__all__ = ['Dipole', 'Earth', 'earth']
class Dipole:
    """
    
                Magnetic dipole model.
    
                :reference: https://en.wikipedia.org/wiki/Magnetic_dipole
                :reference: https://en.wikipedia.org/wiki/Magnetic_moment
                :reference: https://en.wikipedia.org/wiki/Vacuum_permeability
                :reference: https://en.wikipedia.org/wiki/Dipole_model_of_the_Earth%27s_magnetic_field
            
    """
    def __init__(self, arg0: numpy.ndarray[numpy.float64[3, 1]]) -> None:
        """
                        Construct a dipole magnetic model.
        
                        Args:
                            magnetic_moment (np.ndarray): Magnetic moment [A⋅m2].
        """
    def get_field_value_at(self, arg0: numpy.ndarray[numpy.float64[3, 1]], arg1: ostk.physics.time.Instant) -> numpy.ndarray[numpy.float64[3, 1]]:
        """
                        Get the magnetic field value at a given position and instant.
        
                        Args:
                            position (np.ndarray): Position, expressed in the magnetic object frame [m].
                            instant (Instant): Instant.
        
                        Returns:
                            np.ndarray: Magnetic field value, expressed in the magnetic object frame [T].
        """
class Earth:
    """
    
                Earth magnetic model.
    
                :reference: https://geographiclib.sourceforge.io/html/magnetic.html
            
    """
    class Type:
        """
        Members:
        
          Undefined : 
                        Undefined Earth model type.
                    
        
          Dipole : 
                        Dipole Earth model type.
                    
        
          EMM2010 : 
                        Enhanced Magnetic Model 2010: approximates the main and crustal magnetic fields for the period 2010–2015.
                    
        
          EMM2015 : 
                        Enhanced Magnetic Model 2015: approximates the main and crustal magnetic fields for the period 2000–2020.
                    
        
          EMM2017 : 
                        Enhanced Magnetic Model 2017: approximates the main and crustal magnetic fields for the period 2000–2022.
                    
        
          IGRF11 : 
                        International Geomagnetic Reference Field (11th generation): approximates the main magnetic field for the period 1900–2015.
                    
        
          IGRF12 : 
                        International Geomagnetic Reference Field (12th generation): approximates the main magnetic field for the period 1900–2020.
                    
        
          WMM2010 : 
                        World Magnetic Model 2010: approximates the main magnetic field for the period 2010–2015.
                    
        
          WMM2015 : 
                        World Magnetic Model 2015: approximates the main magnetic field for the period 2015–2020.
                    
        """
        Dipole: typing.ClassVar[Earth.Type]  # value = <Type.Dipole: 1>
        EMM2010: typing.ClassVar[Earth.Type]  # value = <Type.EMM2010: 2>
        EMM2015: typing.ClassVar[Earth.Type]  # value = <Type.EMM2015: 3>
        EMM2017: typing.ClassVar[Earth.Type]  # value = <Type.EMM2017: 4>
        IGRF11: typing.ClassVar[Earth.Type]  # value = <Type.IGRF11: 5>
        IGRF12: typing.ClassVar[Earth.Type]  # value = <Type.IGRF12: 6>
        Undefined: typing.ClassVar[Earth.Type]  # value = <Type.Undefined: 0>
        WMM2010: typing.ClassVar[Earth.Type]  # value = <Type.WMM2010: 7>
        WMM2015: typing.ClassVar[Earth.Type]  # value = <Type.WMM2015: 8>
        __members__: typing.ClassVar[dict[str, Earth.Type]]  # value = {'Undefined': <Type.Undefined: 0>, 'Dipole': <Type.Dipole: 1>, 'EMM2010': <Type.EMM2010: 2>, 'EMM2015': <Type.EMM2015: 3>, 'EMM2017': <Type.EMM2017: 4>, 'IGRF11': <Type.IGRF11: 5>, 'IGRF12': <Type.IGRF12: 6>, 'WMM2010': <Type.WMM2010: 7>, 'WMM2015': <Type.WMM2015: 8>}
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
    @typing.overload
    def __init__(self, type: typing.Any, directory: ostk.core.filesystem.Directory) -> None:
        """
                        Construct an Earth magnetic model.
        
                        Args:
                            type (Earth.Type): Earth model type.
                            directory (Directory): Directory containing the magnetic model data files.
        """
    @typing.overload
    def __init__(self, type: typing.Any) -> None:
        """
                        Construct an Earth magnetic model.
        
                        Args:
                            type (Earth.Type): Earth model type.
        """
    def get_field_value_at(self, arg0: numpy.ndarray[numpy.float64[3, 1]], arg1: ostk.physics.time.Instant) -> numpy.ndarray[numpy.float64[3, 1]]:
        """
                        Get the magnetic field value at a given position and instant.
        
                        Args:
                            position (np.ndarray): Position, expressed in the magnetic object frame [m].
                            instant (Instant): Instant.
        
                        Returns:
                            np.ndarray: Magnetic field value, expressed in the magnetic object frame [T].
        """
    def get_type(self) -> ...:
        """
                        Get Earth model type.
        
                        Returns:
                            Earth.Type: Earth model type.
        """
    def is_defined(self) -> bool:
        """
                        Check if the magnetic model is defined.
        
                        Returns:
                            bool: True if defined.
        """
