from __future__ import annotations
import typing
__all__ = ['Theory']
class Theory:
    """
    
                IAU theory.
    
                The IAU 2000A precession-nutation theory relates the International Celestial Reference
                Frame to the International Terrestrial Reference Frame and has been effective since
                January 2003. In 2006, the IAU moved to adopt a more dynamically consistent precession
                model to complement the IAU 2000A nutation theory.
    
                :reference: https://www.researchgate.net/publication/289753602_The_IAU_2000A_and_IAU_2006_precession-nutation_theories_and_their_implementation
    
            
    
    Members:
    
      IAU_2000A : 
                    The IAU 2000A theory.
                
    
      IAU_2000B : 
                    The IAU 2000B theory.
                
    
      IAU_2006 : 
                    The IAU 2006 theory.
                
    """
    IAU_2000A: typing.ClassVar[Theory]  # value = <Theory.IAU_2000A: 0>
    IAU_2000B: typing.ClassVar[Theory]  # value = <Theory.IAU_2000B: 1>
    IAU_2006: typing.ClassVar[Theory]  # value = <Theory.IAU_2006: 2>
    __members__: typing.ClassVar[dict[str, Theory]]  # value = {'IAU_2000A': <Theory.IAU_2000A: 0>, 'IAU_2000B': <Theory.IAU_2000B: 1>, 'IAU_2006': <Theory.IAU_2006: 2>}
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
