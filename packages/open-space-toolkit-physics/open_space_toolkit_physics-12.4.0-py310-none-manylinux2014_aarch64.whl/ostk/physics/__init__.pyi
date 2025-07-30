from __future__ import annotations
from ostk import core as OpenSpaceToolkitCorePy
from ostk.core import container
import ostk.core.filesystem
from ostk.core import filesystem
from ostk.core import type
import ostk.core.type
from ostk import io as OpenSpaceToolkitIOPy
from ostk.io import URL
from ostk.io import ip
from ostk import mathematics as OpenSpaceToolkitMathematicsPy
from ostk.mathematics import curve_fitting
from ostk.mathematics import geometry
from ostk.mathematics import object
from ostk.mathematics import solver
from ostk import physics as OpenSpaceToolkitPhysicsPy
import typing
from . import coordinate
from . import data
from . import environment
from . import time
from . import unit
__all__ = ['Environment', 'Manager', 'OpenSpaceToolkitCorePy', 'OpenSpaceToolkitIOPy', 'OpenSpaceToolkitMathematicsPy', 'OpenSpaceToolkitPhysicsPy', 'URL', 'Unit', 'container', 'coordinate', 'curve_fitting', 'data', 'environment', 'filesystem', 'geometry', 'ip', 'object', 'solver', 'time', 'type', 'unit']
class Environment:
    """
    
                Environment modelling
            
    """
    @staticmethod
    def access_global_instance() -> Environment:
        """
                        Access the global environment instance.
        
                        Returns:
                            Environment: The global environment instance.
        """
    @staticmethod
    def default(set_global_instance: bool = False) -> Environment:
        """
                        Get the default Environment object.
        
                        Args:
                            (set_global_instance): True if the global environment instance should be set.
        
                        Returns:
                            Environment: The default Environment object.
        """
    @staticmethod
    def has_global_instance() -> bool:
        """
                        Check if the global environment instance is set.
        
                        Returns:
                            bool: True if the global environment instance is set, False otherwise.
        """
    @staticmethod
    def reset_global_instance() -> None:
        """
                        Reset the global environment instance.
        """
    @staticmethod
    def undefined() -> Environment:
        """
                        Get an undefined Environment object.
        
                        Returns:
                            Environment: An undefined Environment object.
        """
    @typing.overload
    def __init__(self, instant: time.Instant, objects: list[...], set_global_instance: bool = False) -> None:
        """
                        Constructor
        
                        Args:
                            instant (Instant): An Instant.
                            objects (list[Object]): List of objects.
                            set_global_instance (bool, optional): True if the global environment instance should be set. Defaults to False.
        """
    @typing.overload
    def __init__(self, central_celestial_object: typing.Any, objects: list[...], instant: time.Instant = ..., set_global_instance: bool = False) -> None:
        """
                        Constructor
        
                        Args:
                            central_celestial_object (Object): A central celestial object.
                            objects (list[Object]): List of objects.
                            instant (Instant, optional): An Instant. Default is J2000 epoch.
                            set_global_instance (bool, optional): True if the global environment instance should be set. Defaults to False.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def access_celestial_object_with_name(self, name: ostk.core.type.String) -> ...:
        """
                        Access celestial object with a given name.
        
                        Args:
                            name (str): The name of the celestial object.
        
                        Returns:
                            Celestial: The celestial object with the given name.
        """
    def access_central_celestial_object(self) -> ...:
        """
                        Access the central celestial object.
        
                        Returns:
                            Celestial: The central celestial object.
        """
    def access_object_with_name(self, name: ostk.core.type.String) -> ...:
        """
                        Access an object with a given name.
        
                        Args:
                            name (str): An object name.
        
                        Returns:
                            Object: The object with the given name.
        """
    def access_objects(self) -> list[...]:
        """
                        Access the objects in the environment.
        
                        Returns:
                            list(Object): The list of objects.
        """
    def get_instant(self) -> time.Instant:
        """
                        Get instant.
        
                        Returns:
                            Instant: The instant.
        """
    def get_object_names(self) -> list[ostk.core.type.String]:
        """
                        Get names of objects.
        
                        Returns:
                            list(str): List of objects names.
        """
    def has_central_celestial_object(self) -> bool:
        """
                        Returns true if the environment has a central celestial object.
        
                        Returns:
                            bool: True if the environment has a central celestial object, False otherwise.
        """
    def has_object_with_name(self, name: ostk.core.type.String) -> bool:
        """
                        Returns true if environment contains objects with a given name.
        
                        Args:
                            name (str): The name of the object.
        
                        Returns:
                            bool: True if environment contains objects with a given name, False otherwise.
        """
    def intersects(self, geometry: typing.Any, objects_to_ignore: list[...] = []) -> bool:
        """
                        Returns true if a given geometry intersects any of the environment objects.
        
                        Args:
                            geometry (Geometry): The geometry to check for intersection.
                            objects_to_ignore (list[Object], optional): List of objects to ignore during intersection check.
        
                        Returns:
                            bool: True if the geometry intersects with any objects, False otherwise.
        """
    def is_defined(self) -> bool:
        """
                        Check if the environment is defined,
        
                        Returns:
                            bool: True if the environment is defined, False otherwise,
        """
    def is_position_in_eclipse(self, position: coordinate.Position) -> bool:
        """
                        Is position in eclipse.
        
                        Args:
                            position (Position): A position.
        
                        Returns:
                            bool: True if the position is in eclipse, False otherwise.
        """
    def set_instant(self, instant: time.Instant) -> None:
        """
                        Set the instant of the environment.
        
                        Args:
                            instant (Instant): The new instant of the environment.
        """
class Manager:
    """
    
                Manager
    
                Abstract base class for managing physics-related resources.
    
                This class serves as the foundation for specialized managers like
                IERS, Data, Atmospheric, Gravitational, and Magnetic managers.
                It provides common functionality for mode management and local
                repository handling.
            
    """
    class Mode:
        """
        Members:
        
          Manual
        
          Automatic
        """
        Automatic: typing.ClassVar[Manager.Mode]  # value = <Mode.Automatic: 1>
        Manual: typing.ClassVar[Manager.Mode]  # value = <Mode.Manual: 0>
        __members__: typing.ClassVar[dict[str, Manager.Mode]]  # value = {'Manual': <Mode.Manual: 0>, 'Automatic': <Mode.Automatic: 1>}
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
    def clear_local_repository(self) -> None:
        """
                        Clear the local repository.
        """
    def get_local_repository(self) -> ostk.core.filesystem.Directory:
        """
                        Get the local repository.
        
                        Returns:
                            Directory: Local repository.
        """
    def get_local_repository_lock_timeout(self) -> ...:
        """
                        Get the local repository lock timeout.
        
                        Returns:
                            Duration: Local repository lock timeout.
        """
    def get_mode(self) -> Manager.Mode:
        """
                        Get the manager mode.
        
                        Returns:
                            Mode: Manager mode.
        """
    def reset(self) -> None:
        """
                        Reset the manager.
        """
    def set_local_repository(self, directory: ostk.core.filesystem.Directory) -> None:
        """
                        Set the local repository.
        
                        Args:
                            directory (Directory): Local repository.
        """
    def set_mode(self, mode: Manager.Mode) -> None:
        """
                        Set the manager mode.
        
                        Args:
                            mode (Mode): Manager mode.
        """
class Unit:
    """
    
                Unit
    
                A unit of measurement is a definite magnitude of a quantity, defined and adopted by
                convention or by law, that is used as a standard for measurement of the same kind of
                quantity. Any other quantity of that kind can be expressed as a multiple of the unit of
                measurement.
    
                :see: https://en.wikipedia.org/wiki/Unit_of_measurement
    
            
    """
    class Type:
        """
        Members:
        
          Undefined : 
                        Undefined unit type.
                    
        
          None_ : 
                        None unit type.
                    
        
          Length : 
                        Length unit type.
                    
        
          Mass : 
                        Mass unit type.
                    
        
          Time : 
                        Time unit type.
                    
        
          Temperature : 
                        Temperature unit type.
                    
        
          ElectricCurrent : 
                        Electric current unit type.
                    
        
          LuminousIntensity : 
                        Luminous intensity unit type.
                    
        
          Derived : 
                        Derived unit type.
                    
        """
        Derived: typing.ClassVar[Unit.Type]  # value = <Type.Derived: 8>
        ElectricCurrent: typing.ClassVar[Unit.Type]  # value = <Type.ElectricCurrent: 6>
        Length: typing.ClassVar[Unit.Type]  # value = <Type.Length: 2>
        LuminousIntensity: typing.ClassVar[Unit.Type]  # value = <Type.LuminousIntensity: 7>
        Mass: typing.ClassVar[Unit.Type]  # value = <Type.Mass: 3>
        None_: typing.ClassVar[Unit.Type]  # value = <Type.None_: 1>
        Temperature: typing.ClassVar[Unit.Type]  # value = <Type.Temperature: 5>
        Time: typing.ClassVar[Unit.Type]  # value = <Type.Time: 4>
        Undefined: typing.ClassVar[Unit.Type]  # value = <Type.Undefined: 0>
        __members__: typing.ClassVar[dict[str, Unit.Type]]  # value = {'Undefined': <Type.Undefined: 0>, 'None_': <Type.None_: 1>, 'Length': <Type.Length: 2>, 'Mass': <Type.Mass: 3>, 'Time': <Type.Time: 4>, 'Temperature': <Type.Temperature: 5>, 'ElectricCurrent': <Type.ElectricCurrent: 6>, 'LuminousIntensity': <Type.LuminousIntensity: 7>, 'Derived': <Type.Derived: 8>}
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
    def derived(derived_unit: typing.Any) -> Unit:
        """
                        Create a derived unit.
        
                        Args:
                            derived_unit (unit.Derived.Unit): A derived unit.
        
                        Returns:
                            Unit: Derived unit.
        """
    @staticmethod
    def length(length_unit: typing.Any) -> Unit:
        """
                        Create a length unit.
        
                        Args:
                            length_unit (unit.Length.Unit): A length unit.
        
                        Returns:
                            Unit: Length unit.
        """
    @staticmethod
    def none() -> Unit:
        """
                        Create a none unit.
        
                        Returns:
                            Unit: None unit.
        """
    @staticmethod
    def string_from_type(type: Unit.Type) -> ostk.core.type.String:
        """
                        Get the string representation of a unit type.
        
                        Args:
                            type (Type): Unit type.
        
                        Returns:
                            str: String representation.
        """
    @staticmethod
    def undefined() -> Unit:
        """
                        Create an undefined unit.
        
                        Returns:
                            Unit: Undefined unit.
        """
    def __eq__(self, arg0: Unit) -> bool:
        ...
    def __ne__(self, arg0: Unit) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def get_type(self) -> Unit.Type:
        """
                        Get the unit type.
        
                        Returns:
                            Type: Unit type.
        """
    def is_defined(self) -> bool:
        """
                        Check if the unit is defined.
        
                        Returns:
                            bool: True if defined.
        """
    def is_none(self) -> bool:
        """
                        Check if the unit is none.
        
                        Returns:
                            bool: True if none.
        """
    def ratio_to(self, unit: Unit) -> ostk.core.type.Real:
        """
                        Get the ratio to another unit.
        
                        Args:
                            unit (Unit): Another unit.
        
                        Returns:
                            float:Ratio to another unit.
        """
    def to_string(self) -> ostk.core.type.String:
        """
                        Get the string representation of the unit.
        
                        Returns:
                            str: String representation.
        """
