from __future__ import annotations
import ostk.physics
import ostk.physics.coordinate
import ostk.physics.data
import ostk.physics.environment.object
__all__ = ['nadir']
def nadir(position: ostk.physics.coordinate.Position, celestial: ostk.physics.environment.object.Celestial, environment: ostk.physics.Environment) -> ostk.physics.data.Direction:
    """
                Nadir.
    
                Compute the nadir direction from a given position.
                The instant of the position is inferred from the environment.
    
                Args:
                    position (Position): Position.
                    celestial (Celestial): Celestial object.
                    environment (Environment): Environment.
    
                Returns:
                    Direction: Nadir direction.
    """
