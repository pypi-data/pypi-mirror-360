from __future__ import annotations
import ostk.core.filesystem
import ostk.physics
import ostk.physics.environment.magnetic
__all__ = ['Manager']
class Manager(ostk.physics.Manager):
    """
    
                Earth magnetic model data manager
    
                Fetches and manages necessary magnetic model data files.
    
                The following environment variables can be defined:
    
                - "OSTK_PHYSICS_ENVIRONMENT_MAGNETIC_EARTH_MANAGER_MODE" will override "DefaultMode"
                - "OSTK_PHYSICS_ENVIRONMENT_MAGNETIC_EARTH_MANAGER_LOCAL_REPOSITORY" will override "DefaultLocalRepository"
            
    """
    @staticmethod
    def get() -> Manager:
        """
                        Get manager singleton
        
                        Returns:
                            Manager: Reference to manager
        """
    def fetch_data_files_for_type(self, model_type: ostk.physics.environment.magnetic.Earth.Type) -> None:
        """
                        Fetch data file from remote
        
                        Args:
                            model_type (EarthMagneticModel.Type): Model type
        """
    def has_data_files_for_type(self, model_type: ostk.physics.environment.magnetic.Earth.Type) -> bool:
        """
                        Check if data files are available for the given type
        
                        Args:
                            model_type (EarthMagneticModel.Type): Model type
        
                        Returns:
                            bool: True if data files are available for the given type
        """
    def local_data_files_for_type(self, model_type: ostk.physics.environment.magnetic.Earth.Type) -> list[ostk.core.filesystem.File]:
        """
                        Get local data files for the given type
        
                        Args:
                            model_type (EarthMagneticModel.Type): Model type
        
                        Returns:
                            list[File]: Local data files
        """
