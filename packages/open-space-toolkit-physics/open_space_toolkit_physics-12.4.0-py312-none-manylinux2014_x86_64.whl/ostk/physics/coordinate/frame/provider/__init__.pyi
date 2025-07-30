from __future__ import annotations
import ostk.physics.coordinate.frame
import ostk.physics.time
import typing
from . import iau
from . import iers
__all__ = ['Dynamic', 'Static', 'iau', 'iers']
class Dynamic(ostk.physics.coordinate.frame.Provider):
    """
    
                Dynamic provider.
    
            
    """
    @staticmethod
    def undefined() -> Dynamic:
        """
                        Get an undefined dynamic provider. 
        """
    def __init__(self, generator: typing.Any) -> None:
        """
                        Constructor.
        
                        Args:
                            generator: Generator function.
        """
    def get_transform_at(self, instant: ostk.physics.time.Instant) -> ...:
        """
                        Get the transform at a given instant.
        
                        Args:
                            instant (Instant): An instant
        
                        Returns:
                            Transform: Transform
        """
    def is_defined(self) -> bool:
        """
                        Check if the Dynamic provider is defined
        
                        Returns:
                            bool: True if defined
        """
class Static(ostk.physics.coordinate.frame.Provider):
    """
    
                Static provider.
    
            
    """
    def __init__(self, arg0: typing.Any) -> None:
        """
                        Constructor.
        """
    def get_transform_at(self, instant: ostk.physics.time.Instant) -> ...:
        """
                        Get the transform at a given instant.
        
                        Args:
                            instant (Instant): An instant
        
                        Returns:
                            Transform: Transform
        """
    def is_defined(self) -> bool:
        """
                        Check if the Static provider is defined
        
                        Returns:
                            bool: True if defined
        """
