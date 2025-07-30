from __future__ import annotations
import ostk.core.type
import ostk.physics.coordinate
import ostk.physics.time
from . import atmospheric
from . import gravitational
from . import magnetic
from . import object
__all__ = ['Object', 'atmospheric', 'gravitational', 'magnetic', 'object']
class Object:
    """
    
                This class represents a physical object in the environment.
                It can be subclassed to represent specific types of objects, like celestial bodies.
            
    """
    def __repr__(self) -> str:
        """
                    Returns:
                        str: a string representation of the Object. Similar to __str__.
        """
    def __str__(self) -> str:
        """
                    Returns:
                        str: a string representation of the Object.
        """
    def access_frame(self) -> ostk.physics.coordinate.Frame:
        """
                        Accesses the frame of the Object.
        
                        Returns:
                            Frame: The frame of the Object.
        """
    def access_name(self) -> ostk.core.type.String:
        """
                        Accesses the name of the Object.
        
                        Returns:
                            str: The name of the Object.
        """
    def get_axes_in(self, frame: ostk.physics.coordinate.Frame, instant: ostk.physics.time.Instant) -> ostk.physics.coordinate.Axes:
        """
                        Gets the axes of the Object in a given frame.
        
                        Args:
                            frame (Frame): The frame in which the axes are expressed.
                            instant (Instant): The instant at which the axes are computed.
        
                        Returns:
                            Axes: the axes of the Object.
        """
    def get_geometry(self) -> ...:
        """
                        Gets the geometry of the Object.
        
                        Returns:
                            Geometry: The geometry of the Object.
        """
    def get_geometry_in(self, frame: ostk.physics.coordinate.Frame, instant: ostk.physics.time.Instant) -> ...:
        """
                        Gets the geometry of the Object in a given frame.
        
                        Args:
                            frame (Frame): The frame in which the geometry is expressed.
                            instant (Instant): The instant at which the geometry is computed.
        
                        Returns:
                            Geometry: the geometry of the Object.
        """
    def get_name(self) -> ostk.core.type.String:
        """
                        Gets the name of the Object.
        
                        Returns:
                            str: The name of the Object.
        """
    def get_position_in(self, frame: ostk.physics.coordinate.Frame, instant: ostk.physics.time.Instant) -> ostk.physics.coordinate.Position:
        """
                        Gets the position of the Object in a given frame.
        
                        Args:
                            frame (Frame): The frame in which the position is expressed.
                            instant (Instant): The instant at which the position is computed.
        
                        Returns:
                            Position: The position of the Object.
        """
    def get_transform_to(self, frame: ostk.physics.coordinate.Frame, instant: ostk.physics.time.Instant) -> ostk.physics.coordinate.Transform:
        """
                        Gets the transformation from the Object to a given frame.
        
                        Args:
                            frame (Frame): The frame to which the transformation is expressed.
                            instant (Instant): The instant at which the transformation is computed.
        
                        Returns:
                            Transformation: the transformation.
        """
    def is_defined(self) -> bool:
        """
                        Checks if the Object is defined.
        
                        Returns:
                            bool: True if the Object is defined, False otherwise.
        """
