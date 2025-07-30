from __future__ import annotations
import ostk.physics.time
from . import provider
__all__ = ['Provider', 'provider']
class Provider:
    """
    
                Frame provider.
            
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
