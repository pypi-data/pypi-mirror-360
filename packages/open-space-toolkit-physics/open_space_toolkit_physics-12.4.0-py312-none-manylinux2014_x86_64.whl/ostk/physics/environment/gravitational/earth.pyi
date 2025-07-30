from __future__ import annotations
import ostk.core.filesystem
import ostk.physics
import ostk.physics.environment.gravitational
__all__ = ['Manager']
class Manager(ostk.physics.Manager):
    """
    
                Earth gravitational model data manager.
    
                Fetches and manages necessary gravity model data files.
    
                The following environment variables can be defined:
    
                - "OSTK_PHYSICS_ENVIRONMENT_GRAVITATIONAL_EARTH_MANAGER_MODE" will override "DefaultMode"
                - "OSTK_PHYSICS_ENVIRONMENT_GRAVITATIONAL_EARTH_MANAGER_LOCAL_REPOSITORY" will override "DefaultLocalRepository"
            
    """
    @staticmethod
    def get() -> Manager:
        """
                        Get manager singleton.
        
                        Returns:
                            Manager: Reference to manager.
        """
    def fetch_data_files_for_type(self, model_type: ostk.physics.environment.gravitational.Earth.Type) -> None:
        """
                        Fetch data file from remote.
        
                        Args:
                            model_type (EarthGravitationalModel::Type): A model type.
        """
    def has_data_files_for_type(self, model_type: ostk.physics.environment.gravitational.Earth.Type) -> bool:
        """
                        Returns true if manager has data file for the given model type.
        
                        Args:
                            model_type (EarthGravitationalModel::Type): A model type.
        
                        Returns:
                            bool: True if manager has data file for the given model type.
        """
    def local_data_files_for_type(self, model_type: ostk.physics.environment.gravitational.Earth.Type) -> list[ostk.core.filesystem.File]:
        """
                        Returns list of file objects for the given type.
        
                        Args:
                            model_type (EarthGravitationalModel::Type): A model type.
        
                        Returns:
                            list[File]: list of Files.
        """
