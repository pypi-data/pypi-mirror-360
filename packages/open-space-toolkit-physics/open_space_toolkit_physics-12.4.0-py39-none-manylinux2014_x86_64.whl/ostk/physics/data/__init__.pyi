from __future__ import annotations
import numpy
import ostk.core.filesystem
import ostk.core.type
import ostk.io
import ostk.physics
import ostk.physics.coordinate
import ostk.physics.time
import typing
from . import provider
__all__ = ['Direction', 'Manager', 'Manifest', 'Scalar', 'Vector', 'provider']
class Direction(Vector):
    """
    
                Direction.
    
                A unit vector, expressed in a given frame. 
    
            
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def undefined() -> Direction:
        """
                        Create an undefined direction.
        
                        Returns:
                            Direction: Undefined direction.
        """
    def __eq__(self, arg0: Direction) -> bool:
        """
                        Equality operator.
        
                        Args:
                            other (Direction): Other direction.
        
                        Returns:
                            bool: True if equal.
        """
    def __init__(self, value: numpy.ndarray[numpy.float64[3, 1]], frame: ostk.physics.coordinate.Frame) -> None:
        """
                        Construct a Direction.
        
                        Args:
                            np.ndarray: Value
                            Frame: Frame
        """
    def __ne__(self, arg0: Direction) -> bool:
        """
                        Inequality operator.
        
                        Args:
                            other (Direction): Other direction.
        
                        Returns:
                            bool: True if not equal.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
class Manager(ostk.physics.Manager):
    """
    
                OSTk Data manager base class (thread-safe).
    
                The base manager defines methods for tracking and checking the manifest file.
            
    """
    @staticmethod
    def default_remote_url() -> ostk.io.URL:
        """
                        Get the default remote URL for data fetching. 
        
                        Returns:
                            URL: Default remote URL.
        """
    @staticmethod
    def get() -> Manager:
        """
                        Get manager singleton.
        
                        Returns:
                            Manager: Manager instance.
        """
    def find_remote_data_urls(self, data_name_regex_pattern: ostk.core.type.String) -> list[ostk.io.URL]:
        """
                        Find remote URLs of data matching regular expression string. 
        
                        Args:
                            data_name_regex_pattern (String): A regular expression string
        
                        Returns:
                            List[URL]: List of URLs.
        """
    def get_last_update_timestamp_for(self, data_name: ostk.core.type.String) -> ostk.physics.time.Instant:
        """
                        Check if there are updates for data of a certain name. 
        
                        Args:
                            data_name (String): Name of the data to query. This is the key for the data entry in the manifest file.
        
                        Returns:
                            Instant: Instant indicating when the data was last updated on the remote, according to the manifest record. 
        """
    def get_manifest(self) -> ...:
        """
                        Get a copy of the current manifest file.
        
                        Returns:
                            Manifest: Manifest.
        """
    def get_remote_data_urls(self, data_name: ostk.core.type.String) -> list[ostk.io.URL]:
        """
                        Get the remote data URL for a given data name.
        
                        Args:
                            data_name (String): Name of the data. i.e. the key for the data entry in the manifest 
        
                        Returns:
                            List[URL]: List of URLs.
        """
    def get_remote_url(self) -> ostk.io.URL:
        """
                        Get the remote URL. This points to the base URL for the OSTk input data. 
        
                        Returns:
                            URL: Remote URL.
        """
    def load_manifest(self, manifest: typing.Any) -> None:
        """
                        Load a new manifest file.
        
                        Args:
                            manifest (Manifest): Manifest.
        """
    def manifest_file_exists(self) -> bool:
        """
                        Return true if a manifest file already exists in the directory. 
        
                        Returns:
                            bool: True if the manifest file exists.
        """
    def reset(self) -> None:
        """
                        Reset the manager.
        
                        Unload the manifest file and forget manifest age. 
        """
    def set_remote_url(self, remote_url: ostk.io.URL) -> None:
        """
                        Set the remote URL. 
        
                        Args:
                            remote_url (Directory): Remote URL.
        """
class Manifest:
    """
    
                Data class for the OSTk Data Manifest.
    
            
    """
    @staticmethod
    def load(file: ostk.core.filesystem.File) -> Manifest:
        """
                        Load a manifest from a file.
        
                        Args:
                            file (File): A manifest file.
        
                        Returns:
                            Manifest: Manifest.
        """
    @staticmethod
    def undefined() -> Manifest:
        """
                        Create an undefined manifest.
        
                        Returns:
                            Manifest: Undefined manifest.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def find_remote_data_urls(self, base_url: ostk.io.URL, data_name_regex_pattern: ostk.core.type.String) -> list[ostk.io.URL]:
        """
                        Return remote data URLs the for data items matching the given name regex string. 
        
                        Args:
                            base_url (URL): A base URL for remote data.
                            data_name_regex_pattern (String): A data name regex string.
        
                        Returns:
                            list[URL]: List of remote data URLs.
        """
    def get_last_modified_timestamp(self) -> ostk.physics.time.Instant:
        """
                        Get last update timestamp.
        
                        Returns:
                            Instant: Instant indicating when the manifest was last updated based on file modification time.
        """
    def get_last_update_timestamp_for(self, data_name: ostk.core.type.String) -> ostk.physics.time.Instant:
        """
                        Get last update timestamp for data. 
        
                        Args:
                            data_name (String): A data name.
        
                        Returns:
                            Instant: Last update instant for data.
        """
    def get_next_update_check_timestamp_for(self, data_name: ostk.core.type.String) -> ostk.physics.time.Instant:
        """
                        Get next update check timestamp for data. 
        
                        Args:
                            data_name (String): A data name.
        
                        Returns:
                            Instant: Next update check instant for data.
        """
    def get_remote_data_urls(self, base_url: ostk.io.URL, data_name: ostk.core.type.String) -> list[ostk.io.URL]:
        """
                        Get the remote data URL for a given data name.
        
                        Args:
                            base_url (URL): A base URL for remote data.
                            data_name (String): Name of the data. i.e. the key for the data entry in the manifest.
        
                        Returns:
                            list[URL]: List of remote data URLs.
        """
    def is_defined(self) -> bool:
        """
                        Check if the manifest is defined.
        
                        Returns:
                            bool: True if defined.
        """
class Scalar:
    """
    
                Scalar quantity.
    
                A scalar quantity is a physical quantity that can be described by a single element of a
                number field such as a real number, often accompanied by units of measurement.
    
                :reference: https://en.wikipedia.org/wiki/Scalar_(physics)
                
            
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def undefined() -> Scalar:
        """
                        Create an undefined scalar.
        
                        Returns:
                            Scalar: Undefined scalar.
        """
    def __eq__(self, arg0: Scalar) -> bool:
        """
                        Equality operator.
        
                        Args:
                            other (Scalar): Other scalar.
        
                        Returns:
                            bool: True if equal.
        """
    def __init__(self, value: ostk.core.type.Real, unit: ostk.physics.Unit) -> None:
        """
                        Construct a Scalar.
        
                        Args:
                            value (Real): Value.
                            unit (Unit): Unit.
        """
    def __ne__(self, arg0: Scalar) -> bool:
        """
                        Inequality operator.
        
                        Args:
                            other (Scalar): Other scalar.
        
                            Returns:
                                bool: True if not equal.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def get_unit(self) -> ostk.physics.Unit:
        """
                        Get unit.
        
                        Returns:
                            Unit: Unit.
        """
    def get_value(self) -> ostk.core.type.Real:
        """
                        Get value.
        
                        Returns:
                            float: Value.
        """
    def in_unit(self, unit: ostk.physics.Unit) -> Scalar:
        """
                        Convert to unit.
        
                        Args:
                            unit (Unit): Unit.
        
                        Returns:
                            Scalar: Scalar in the specified unit.
        """
    def is_defined(self) -> bool:
        """
                        Check if the scalar is defined.
        
                        Returns:
                            bool: True if defined.
        """
    def to_string(self, precision: ostk.core.type.Integer = ...) -> ostk.core.type.String:
        """
                        Convert to string.
        
                        Args:
                            precision (int): Precision.
        
                        Returns:
                            str: String representation.
        """
class Vector:
    """
    
                Vector quantity
    
            
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def undefined() -> Vector:
        """
                        Create an undefined vector.
        
                        Returns:
                            Vector: Undefined vector.
        """
    def __eq__(self, arg0: Vector) -> bool:
        """
                        Equality operator.
        
                        Args:
                            other (Vector): Other vector.
        
                        Returns:
                            bool: True if equal.
        """
    def __init__(self, value: numpy.ndarray[numpy.float64[3, 1]], unit: ostk.physics.Unit, frame: ostk.physics.coordinate.Frame) -> None:
        """
                        Construct a Vector.
        
                        Args:
                            value (np.ndarray): Value.
                            unit (Unit): Unit.
                            frame (Frame): Frame.
        """
    def __ne__(self, arg0: Vector) -> bool:
        """
                        Inequality operator.
        
                        Args:
                            other (Vector): Other vector.
        
                        Returns:
                            bool: True if not equal.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def get_frame(self) -> ostk.physics.coordinate.Frame:
        """
                        Get frame.
        
                        Returns:
                            Frame: Frame.
        """
    def get_unit(self) -> ostk.physics.Unit:
        """
                        Get unit.
        
                        Returns:
                            Unit: Unit.
        """
    def get_value(self) -> numpy.ndarray[numpy.float64[3, 1]]:
        """
                        Get value.
        
                        Returns:
                            np.ndarray: Value.
        """
    def in_frame(self, frame: ostk.physics.coordinate.Frame, instant: ostk.physics.time.Instant) -> Vector:
        """
                        Convert to frame.
        
                        Args:
                            frame (Frame): Frame.
                            instant (Instant): Instant.
        
                        Returns:
                            Vector: Vector in frame.
        """
    def in_unit(self, unit: ostk.physics.Unit) -> Vector:
        """
                        Convert to unit.
        
                        Args:
                            unit (Unit): Unit.
        
                        Returns:
                            Vector: Vector in unit.
        """
    def is_defined(self) -> bool:
        """
                        Check if the vector is defined.
        
                        Returns:
                            bool: True if defined.
        """
    def to_string(self, precision: ostk.core.type.Integer = 6) -> ostk.core.type.String:
        """
                        Convert to (formatted) string.
        
                        Args:
                            precision (Integer): Precision.
        
                        Returns:
                            str: String representation.
        """
