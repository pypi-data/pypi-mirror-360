from __future__ import annotations
import numpy
import ostk.core.type
import ostk.mathematics.geometry
import ostk.mathematics.object
import typing
__all__ = ['Angle', 'Derived', 'ElectricCurrent', 'Interval', 'Length', 'Mass', 'Time']
class Angle:
    """
    
                Angle.
                
                :reference: https://en.wikipedia.org/wiki/Angle
                
    """
    class Unit:
        """
        Members:
        
          Undefined : 
                        Undefined unit.
                    
        
          Radian : 
                        Radian unit.
                    
        
          Degree : 
                        Degree unit.
                    
        
          Arcminute : 
                        Arcminute unit.
                    
        
          Arcsecond : 
                        Arcsecond unit.
                    
        
          Revolution : 
                        Revolution unit.
                    
        """
        Arcminute: typing.ClassVar[Angle.Unit]  # value = <Unit.Arcminute: 3>
        Arcsecond: typing.ClassVar[Angle.Unit]  # value = <Unit.Arcsecond: 4>
        Degree: typing.ClassVar[Angle.Unit]  # value = <Unit.Degree: 2>
        Radian: typing.ClassVar[Angle.Unit]  # value = <Unit.Radian: 1>
        Revolution: typing.ClassVar[Angle.Unit]  # value = <Unit.Revolution: 5>
        Undefined: typing.ClassVar[Angle.Unit]  # value = <Unit.Undefined: 0>
        __members__: typing.ClassVar[dict[str, Angle.Unit]]  # value = {'Undefined': <Unit.Undefined: 0>, 'Radian': <Unit.Radian: 1>, 'Degree': <Unit.Degree: 2>, 'Arcminute': <Unit.Arcminute: 3>, 'Arcsecond': <Unit.Arcsecond: 4>, 'Revolution': <Unit.Revolution: 5>}
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
    def arcminutes(value: ostk.core.type.Real) -> Angle:
        """
                        Create an angle in arcminutes.
        
                        Args:
                            value (Real): A value.
        
                        Returns:
                            Angle: An angle in arcminutes.
        """
    @staticmethod
    def arcseconds(value: ostk.core.type.Real) -> Angle:
        """
                        Create an angle in arcseconds.
        
                        Args:
                            value (Real): A value.
        
                        Returns:
                            Angle: An angle in arcseconds.
        """
    @staticmethod
    @typing.overload
    def between(first_vector: numpy.ndarray[numpy.float64[2, 1]], second_vector: numpy.ndarray[numpy.float64[2, 1]]) -> Angle:
        """
                        Create an angle between two vectors.
        
                        Args:
                            first_vector (Vector2d): A first vector.
                            second_vector (Vector2d): A second vector.
        
                        Returns:
                            Angle: An angle between two vectors.
        """
    @staticmethod
    @typing.overload
    def between(first_vector: numpy.ndarray[numpy.float64[3, 1]], second_vector: numpy.ndarray[numpy.float64[3, 1]]) -> Angle:
        """
                        Create an angle between two vectors.
        
                        Args:
                            first_vector (np.ndarray): A first vector.
                            second_vector (np.ndarray): A second vector.
        
                        Returns:
                            Angle: An angle between two vectors.
        """
    @staticmethod
    def degrees(value: ostk.core.type.Real) -> Angle:
        """
                        Create an angle in degrees.
        
                        Args:
                            value (Real): A value.
        
                        Returns:
                            Angle: An angle in degrees.
        """
    @staticmethod
    def half_pi() -> Angle:
        """
                        Create a half pi angle.
        
                        Returns:
                            Angle: A half pi angle.
        """
    @staticmethod
    def parse(string: ostk.core.type.String) -> Angle:
        """
                        Parse an angle from a string.
        
                        Args:
                            string (str): A string.
        
                        Returns:
                            Angle: An angle.
        """
    @staticmethod
    def pi() -> Angle:
        """
                        Create a pi angle.
        
                        Returns:
                            Angle: A pi angle.
        """
    @staticmethod
    def radians(value: ostk.core.type.Real) -> Angle:
        """
                        Create an angle in radians.
        
                        Args:
                            value (Real): A value.
        
                        Returns:
                            Angle: An angle in radians.
        """
    @staticmethod
    def revolutions(value: ostk.core.type.Real) -> Angle:
        """
                        Create an angle in revolutions.
        
                        Args:
                            value (Real): A value.
        
                        Returns:
                            Angle: An angle in revolutions.
        """
    @staticmethod
    def string_from_unit(unit: typing.Any) -> ostk.core.type.String:
        """
                        Get the string representation of an angle unit.
        
                        Args:
                            unit (Unit): An angle unit.
        
                        Returns:
                            str: The string representation of an angle unit.
        """
    @staticmethod
    def symbol_from_unit(unit: typing.Any) -> ostk.core.type.String:
        """
                        Get the symbol representation of an angle unit.
        
                        Args:
                            unit (Unit): An angle unit.
        
                        Returns:
                            str: The symbol representation of an angle unit.
        """
    @staticmethod
    def two_pi() -> Angle:
        """
                        Create a two pi angle.
        
                        Returns:
                            Angle: A two pi angle.
        """
    @staticmethod
    def undefined() -> Angle:
        """
                        Create an undefined angle.
        
                        Returns:
                            Angle: An undefined angle.
        """
    @staticmethod
    def zero() -> Angle:
        """
                        Create a zero angle.
        
                        Returns:
                            Angle: A zero angle.
        """
    def __add__(self, arg0: Angle) -> Angle:
        ...
    def __eq__(self, arg0: Angle) -> bool:
        ...
    def __iadd__(self, arg0: Angle) -> Angle:
        ...
    def __imul__(self, arg0: ostk.core.type.Real) -> Angle:
        ...
    @typing.overload
    def __init__(self, value: ostk.core.type.Real, unit: typing.Any) -> None:
        """
                        Constructor.
        
                        Args:
                            value (Real): A value.
                            unit (Unit): An angle unit.
        """
    @typing.overload
    def __init__(self, angle: ostk.mathematics.geometry.Angle) -> None:
        """
                        Constructor.
        
                        Args:
                            angle (Angle): An angle.
        """
    def __isub__(self, arg0: Angle) -> Angle:
        ...
    def __itruediv__(self, arg0: ostk.core.type.Real) -> Angle:
        ...
    def __mul__(self, arg0: ostk.core.type.Real) -> Angle:
        ...
    def __ne__(self, arg0: Angle) -> bool:
        ...
    def __neg__(self) -> Angle:
        ...
    def __pos__(self) -> Angle:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def __sub__(self, arg0: Angle) -> Angle:
        ...
    def __truediv__(self, arg0: ostk.core.type.Real) -> Angle:
        ...
    def get_unit(self) -> ...:
        """
                        Get the unit of the angle.
        
                        Returns:
                            Unit: The unit of the angle.
        """
    @typing.overload
    def in_arcminutes(self) -> ostk.core.type.Real:
        """
                        Get the angle in arcminutes.
        
                        Returns:
                            float: The angle in arcminutes.
        """
    @typing.overload
    def in_arcminutes(self, lower_bound: ostk.core.type.Real, upper_bound: ostk.core.type.Real) -> ostk.core.type.Real:
        """
                        Get the angle in arcminutes.
        
                        Args:
                            lower_bound (Real): A lower bound.
                            upper_bound (Real): An upper bound.
        
                        Returns:
                            float: The angle in arcminutes.
        """
    @typing.overload
    def in_arcseconds(self) -> ostk.core.type.Real:
        """
                        Get the angle in arcseconds.
        
                        Returns:
                            float: The angle in arcseconds.
        """
    @typing.overload
    def in_arcseconds(self, lower_bound: ostk.core.type.Real, upper_bound: ostk.core.type.Real) -> ostk.core.type.Real:
        """
                        Get the angle in arcseconds.
        
                        Args:
                            lower_bound (Real): A lower bound.
                            upper_bound (Real): An upper bound.
        
                        Returns:
                            float: The angle in arcseconds.
        """
    @typing.overload
    def in_degrees(self) -> ostk.core.type.Real:
        """
                        Get the angle in degrees.
        
                        Returns:
                            float: The angle in degrees.
        """
    @typing.overload
    def in_degrees(self, lower_bound: ostk.core.type.Real, upper_bound: ostk.core.type.Real) -> ostk.core.type.Real:
        """
                        Get the angle in degrees.
        
                        Args:
                            lower_bound (Real): A lower bound.
                            upper_bound (Real): An upper bound.
        
                        Returns:
                            float: The angle in degrees.
        """
    @typing.overload
    def in_radians(self) -> ostk.core.type.Real:
        """
                        Get the angle in radians.
        
                        Returns:
                            float: The angle in radians.
        """
    @typing.overload
    def in_radians(self, lower_bound: ostk.core.type.Real, upper_bound: ostk.core.type.Real) -> ostk.core.type.Real:
        """
                        Get the angle in radians.
        
                        Args:
                            lower_bound (Real): A lower bound.
                            upper_bound (Real): An upper bound.
        
                        Returns:
                            float: The angle in radians.
        """
    def in_revolutions(self) -> ostk.core.type.Real:
        """
                        Get the angle in revolutions.
        
                        Returns:
                            float: The angle in revolutions.
        """
    def in_unit(self, unit: typing.Any) -> ostk.core.type.Real:
        """
                        Get the angle in the specified unit.
        
                        Args:
                            unit (Unit): An angle unit.
        
                        Returns:
                            float: The angle in the specified unit.
        """
    def is_defined(self) -> bool:
        """
                        Check if the angle is defined.
        
                        Returns:
                            bool: True if defined.
        """
    def is_zero(self) -> bool:
        """
                        Check if the angle is zero.
        
                        Returns:
                            bool: True if zero.
        """
    def to_string(self, precision: ostk.core.type.Integer = ...) -> ostk.core.type.String:
        """
                        Get the string representation of the angle.
        
                        Args:
                            precision (int): A precision.
        
                        Returns:
                            str: The string representation of the angle.
        """
class Derived:
    """
    
                Derived unit.
    
                :reference: https://en.wikipedia.org/wiki/SI_derived_unit
            
    """
    class Order:
        """
        
                    SI unit order.
        
                
        """
        __hash__: typing.ClassVar[None] = None
        @staticmethod
        def one() -> Derived.Order:
            """
                            Create a unity order.
            
                            Returns:
                                Order: Order.
            """
        @staticmethod
        def two() -> Derived.Order:
            """
                            Create a two order.
            
                            Returns:
                                Order: Order.
            """
        @staticmethod
        def zero() -> Derived.Order:
            """
                            Create a zero order.
            
                            Returns:
                                Order: Order.
            """
        def __eq__(self, arg0: Derived.Order) -> bool:
            ...
        @typing.overload
        def __init__(self, arg0: int) -> None:
            """
                            Constructor.
            
                            Args:
                                aValue (int): Value.
            """
        @typing.overload
        def __init__(self, arg0: int, arg1: int) -> None:
            """
                            Constructor.
            
                            Args:
                                aNumerator (int): Numerator.
                                aDenominator (int): Denominator.
            """
        def __ne__(self, arg0: Derived.Order) -> bool:
            ...
        def get_denominator(self) -> int:
            """
                            Get denominator.
            
                            Returns:
                                int: Denominator.
            """
        def get_numerator(self) -> int:
            """
                            Get numerator.
            
                            Returns:
                                int: Numerator.
            """
        def get_value(self) -> ostk.core.type.Real:
            """
                            Get value.
            
                            Returns:
                                float: Value.
            """
        def is_unity(self) -> bool:
            """
                            Check if the order is unity.
            
                            Returns:
                                bool: True if unity.
            """
        def is_zero(self) -> bool:
            """
                            Check if the order is zero.
            
                            Returns:
                                bool: True if zero.
            """
        def to_string(self) -> ostk.core.type.String:
            """
                            Convert to string.
            
                            Returns:
                                str: String representation.
            """
    class Unit:
        """
        
                    Unit
                
        """
        __hash__: typing.ClassVar[None] = None
        @staticmethod
        def acceleration(length: Length.Unit, time: Time.Unit) -> Derived.Unit:
            """
                            Create an acceleration unit.
            
                            Args:
                                length (Length::Unit): Length unit.
                                time (Time::Unit): Time unit.
            
                            Returns:
                                Unit: Unit.
            """
        @staticmethod
        def angular_velocity(angle: typing.Any, time: Time.Unit) -> Derived.Unit:
            """
                            Create an angular velocity unit.
            
                            Args:
                                angle (Angle::Unit): Angle unit.
                                time (Time::Unit): Time unit.
            
                            Returns:
                                Unit: Unit.
            """
        @staticmethod
        def cubic_meter() -> Derived.Unit:
            """
                            Create a cubic meter unit.
            
                            Returns:
                                Unit: Unit.
            """
        @staticmethod
        def force(mass: Mass.Unit, length: Length.Unit, time: Time.Unit) -> Derived.Unit:
            """
                            Create a force unit.
            
                            Args:
                                mass (Mass::Unit): Mass unit.
                                length (Length::Unit): Length unit.
                                time (Time::Unit): Time unit.
            
                            Returns:
                                Unit: Unit.
            """
        @staticmethod
        def gravitational_parameter(length: Length.Unit, time: Time.Unit) -> Derived.Unit:
            """
                            Create a gravitational parameter unit.
            
                            Args:
                                length (Length::Unit): Length unit.
                                time (Time::Unit): Time unit.
            
                            Returns:
                                Unit: Unit.
            """
        @staticmethod
        def hertz() -> Derived.Unit:
            """
                            Create a hertz unit.
            
                            Returns:
                                Unit: Unit.
            """
        @staticmethod
        def kilogram_per_second() -> Derived.Unit:
            """
                            Create a kilogram per second unit.
            
                            Returns:
                                Unit: Unit.
            """
        @staticmethod
        def mass_density(mass: Mass.Unit, length: Length.Unit) -> Derived.Unit:
            """
                            Create a mass density unit.
            
                            Args:
                                mass (Mass::Unit): Mass unit.
                                length (Length::Unit): Length unit.
            
                            Returns:
                                Unit: Unit.
            """
        @staticmethod
        def mass_flow_rate(mass: Mass.Unit, time: Time.Unit) -> Derived.Unit:
            """
                            Create a mass flow rate unit.
            
                            Args:
                                mass (Mass::Unit): Mass unit.
                                time (Time::Unit): Time unit.
            
                            Returns:
                                Unit: Unit.
            """
        @staticmethod
        def meter_cubed_per_second_squared() -> Derived.Unit:
            """
                            Create a meter cubed per second squared unit.
            
                            Returns:
                                Unit: Unit.
            """
        @staticmethod
        def meter_per_second() -> Derived.Unit:
            """
                            Create a meter per second unit.
            
                            Returns:
                                Unit: Unit.
            """
        @staticmethod
        def meter_per_second_squared() -> Derived.Unit:
            """
                            Create a meter per second squared unit.
            
                            Returns:
                                Unit: Unit.
            """
        @staticmethod
        def newton() -> Derived.Unit:
            """
                            Create a newton unit.
            
                            Returns:
                                Unit: Unit.
            """
        @staticmethod
        def radian_per_second() -> Derived.Unit:
            """
                            Create a radian per second unit.
            
                            Returns:
                                Unit: Unit.
            """
        @staticmethod
        def revolution_per_day() -> Derived.Unit:
            """
                            Create a revolution per day unit.
            
                            Returns:
                                Unit: Unit.
            """
        @staticmethod
        def square_meter() -> Derived.Unit:
            """
                            Create a square meter unit.
            
                            Returns:
                                Unit: Unit.
            """
        @staticmethod
        def tesla() -> Derived.Unit:
            """
                            Create a tesla unit.
            
                            Returns:
                                Unit: Unit.
            """
        @staticmethod
        def undefined() -> Derived.Unit:
            """
                            Create an undefined unit.
            
                            Returns:
                                Unit: Unit.
            """
        @staticmethod
        def velocity(length: Length.Unit, time: Time.Unit) -> Derived.Unit:
            """
                            Create a velocity unit.
            
                            Args:
                                length (Length::Unit): Length unit.
                                time (Time::Unit): Time unit.
            
                            Returns:
                                Unit: Unit.
            """
        @staticmethod
        def watt() -> Derived.Unit:
            """
                            Create a watt unit.
            
                            Returns:
                                Unit: Unit.
            """
        def __eq__(self, arg0: Derived.Unit) -> bool:
            ...
        def __init__(self, arg0: Length.Unit, arg1: Derived.Order, arg2: Mass.Unit, arg3: Derived.Order, arg4: Time.Unit, arg5: Derived.Order, arg6: ElectricCurrent.Unit, arg7: Derived.Order, arg8: typing.Any, arg9: Derived.Order) -> None:
            ...
        def __ne__(self, arg0: Derived.Unit) -> bool:
            ...
        def get_symbol(self) -> ostk.core.type.String:
            """
                            Get symbol.
            
                            Returns:
                                str: Symbol.
            """
        def is_compatible_with(self, arg0: Derived.Unit) -> bool:
            ...
        def is_defined(self) -> bool:
            ...
        def to_string(self) -> ostk.core.type.String:
            """
                            Convert to string.
            
                            Returns:
                                str: String representation.
            """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def string_from_unit(arg0: typing.Any) -> ostk.core.type.String:
        """
                        Get string from unit.
        
                        Args:
                            aUnit (Unit): Unit.
        
                        Returns:
                            str: String.
        """
    @staticmethod
    def symbol_from_unit(arg0: typing.Any) -> ostk.core.type.String:
        """
                        Get symbol from unit.
        
                        Args:
                            aUnit (Unit): Unit.
        
                        Returns:
                            str: Symbol.
        """
    @staticmethod
    def undefined() -> Derived:
        """
                        Create an undefined derived unit.
        
                        Returns:
                            Derived: Derived unit.
        """
    def __eq__(self, arg0: Derived) -> bool:
        ...
    def __init__(self, arg0: ostk.core.type.Real, arg1: typing.Any) -> None:
        """
                        Constructor.
        
                        Args:
                            aValue (Real): Value
                            aUnit (Unit): Unit
        """
    def __ne__(self, arg0: Derived) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def get_unit(self) -> ...:
        """
                        Get unit.
        
                        Returns:
                            Unit: Unit.
        """
    def in_unit(self, arg0: typing.Any) -> ostk.core.type.Real:
        """
                        Convert to unit.
        
                        Returns:
                            float: Value in unit.
        """
    def is_defined(self) -> bool:
        """
                        Check if the derived unit is defined.
        
                        Returns:
                            bool: True if defined.
        """
    def to_string(self, aPrecision: ostk.core.type.Integer = ...) -> ostk.core.type.String:
        """
                        Convert to string.
        
                        Args:
                            aPrecision (int): Precision
        
                        Returns:
                            str: String representation.
        """
class ElectricCurrent:
    """
    
                Electric current.
    
                https://en.wikipedia.org/wiki/Electric_current
            
    """
    class Unit:
        """
        Members:
        
          Undefined : 
                        Undefined.
                    
        
          Ampere : 
                        Ampere (SI).
                    
        """
        Ampere: typing.ClassVar[ElectricCurrent.Unit]  # value = <Unit.Ampere: 1>
        Undefined: typing.ClassVar[ElectricCurrent.Unit]  # value = <Unit.Undefined: 0>
        __members__: typing.ClassVar[dict[str, ElectricCurrent.Unit]]  # value = {'Undefined': <Unit.Undefined: 0>, 'Ampere': <Unit.Ampere: 1>}
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
    def amperes(arg0: ostk.core.type.Real) -> ElectricCurrent:
        """
                        Construct an electric current in amperes.
        
                        Returns:
                            ElectricCurrent: An electric current in amperes.
        """
    @staticmethod
    def string_from_unit(arg0: typing.Any) -> ostk.core.type.String:
        """
                        Get the string representation of an electric current unit.
        
                        Returns:
                            str: The string representation.
        """
    @staticmethod
    def symbol_from_unit(arg0: typing.Any) -> ostk.core.type.String:
        """
                        Get the symbol of an electric current unit.
        
                        Returns:
                            str: The symbol.
        """
    @staticmethod
    def undefined() -> ElectricCurrent:
        """
                        Get an undefined electric current.
        
                        Returns:
                            ElectricCurrent: An undefined electric current.
        """
    def __eq__(self, arg0: ElectricCurrent) -> bool:
        ...
    def __init__(self, arg0: ostk.core.type.Real, arg1: typing.Any) -> None:
        """
                        Constructor.
        
                        Args:
                            aReal (Real): A real number.
                            aUnit (ElectricCurrent.Unit): An electric current unit.
        """
    def __ne__(self, arg0: ElectricCurrent) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def get_unit(self) -> ...:
        """
                        Get the electric current unit.
        
                        Returns:
                            ElectricCurrent.Unit: The electric current unit.
        """
    def in_amperes(self) -> ostk.core.type.Real:
        """
                        Get the electric current in amperes.
        
                        Returns:
                            float: The electric current in amperes.
        """
    def in_unit(self, arg0: typing.Any) -> ostk.core.type.Real:
        """
                        Get the electric current in a given unit.
        
                        Returns:
                            float: The electric current in the given unit.
        """
    def is_defined(self) -> bool:
        """
                        Check if the electric current is defined.
        
                        Returns:
                            bool: True if defined.
        """
    def to_string(self, aPrecision: ostk.core.type.Integer = ...) -> ostk.core.type.String:
        """
                        Get the string representation of the electric current.
        
                        Args:
                            aPrecision (int): A precision.
        
                        Returns:
                            str: The string representation.
        """
class Interval:
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def closed(arg0: Length, arg1: Length) -> Interval:
        """
                        Construct a closed interval.
        
                        Returns:
                            Interval: A closed interval.
        """
    @staticmethod
    def undefined() -> Interval:
        """
                        Get an undefined interval.
        
                        Returns:
                            Interval: An undefined interval.
        """
    def __eq__(self, arg0: Interval) -> bool:
        ...
    def __init__(self, arg0: Length, arg1: Length, arg2: ostk.mathematics.object.RealInterval.Type) -> None:
        """
                        Constructor.
        
                        Args:
                            aLowerBound (Length): The lower bound.
                            anUpperBound (Length): The upper bound.
                            aType (Interval.Type): The type.
        """
    def __ne__(self, arg0: Interval) -> bool:
        ...
    def contains_interval(self, arg0: Interval) -> bool:
        """
                        Check if the interval contains another interval.
        
                        Args:
                            anOtherInterval (Interval): Another interval.
        
                        Returns:
                            bool: True if contains.
        """
    def contains_length(self, arg0: Length) -> bool:
        """
                        Check if the interval contains a length.
        
                        Args:
                            aLength (Length): A length.
        
                        Returns:
                            bool: True if contains.
        """
    def get_lower_bound(self) -> Length:
        """
                        Get the lower bound.
        
                        Returns:
                            Length: The lower bound.
        """
    def get_upper_bound(self) -> Length:
        """
                        Get the upper bound.
        
                        Returns:
                            Length: The upper bound.
        """
    def intersects(self, arg0: Interval) -> bool:
        """
                        Check if the interval intersects another interval.
        
                        Returns:
                            bool: True if intersects.
        """
    def is_defined(self) -> bool:
        """
                        Check if the interval is defined.
        
                        Returns:
                            bool: True if defined.
        """
    def is_degenerate(self) -> bool:
        """
                        Check if the interval is degenerate.
        
                        Returns:
                            bool: True if degenerate.
        """
class Length:
    """
    
                Length.
    
                https://en.wikipedia.org/wiki/Length
            
    """
    class Unit:
        """
        Members:
        
          Undefined : 
                        Undefined length unit.
                    
        
          Meter : 
                        Meter (SI).
                    
        
          Foot : 
                        Foot.
                    
        
          TerrestrialMile : 
                        Terrestrial mile.
                    
        
          NauticalMile : 
                        Nautical mile.
                    
        
          AstronomicalUnit : 
                        Astronomical Unit.
                    
        """
        AstronomicalUnit: typing.ClassVar[Length.Unit]  # value = <Unit.AstronomicalUnit: 5>
        Foot: typing.ClassVar[Length.Unit]  # value = <Unit.Foot: 2>
        Meter: typing.ClassVar[Length.Unit]  # value = <Unit.Meter: 1>
        NauticalMile: typing.ClassVar[Length.Unit]  # value = <Unit.NauticalMile: 4>
        TerrestrialMile: typing.ClassVar[Length.Unit]  # value = <Unit.TerrestrialMile: 3>
        Undefined: typing.ClassVar[Length.Unit]  # value = <Unit.Undefined: 0>
        __members__: typing.ClassVar[dict[str, Length.Unit]]  # value = {'Undefined': <Unit.Undefined: 0>, 'Meter': <Unit.Meter: 1>, 'Foot': <Unit.Foot: 2>, 'TerrestrialMile': <Unit.TerrestrialMile: 3>, 'NauticalMile': <Unit.NauticalMile: 4>, 'AstronomicalUnit': <Unit.AstronomicalUnit: 5>}
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
    def kilometers(arg0: ostk.core.type.Real) -> Length:
        """
                        Construct a length in kilometers.
        
                        Returns:
                            Length: A length in kilometers.
        """
    @staticmethod
    def meters(arg0: ostk.core.type.Real) -> Length:
        """
                        Construct a length in meters.
        
                        Returns:
                            Length: A length in meters.
        """
    @staticmethod
    def millimeters(arg0: ostk.core.type.Real) -> Length:
        """
                        Construct a length in millimeters.
        
                        Returns:
                            Length: A length in millimeters.
        """
    @staticmethod
    def parse(arg0: ostk.core.type.String) -> Length:
        """
                        Parse a string and construct a length.
        
                        Args:
                            aString (str): A string.
        
                        Returns:
                            Length: A length.
        """
    @staticmethod
    def string_from_unit(arg0: typing.Any) -> ostk.core.type.String:
        """
                        Get the string representation of a length unit.
        
                        Returns:
                            str: The string representation.
        """
    @staticmethod
    def symbol_from_unit(arg0: typing.Any) -> ostk.core.type.String:
        """
                        Get the symbol of a length unit.
        
                        Returns:
                            str: The symbol.
        """
    @staticmethod
    def undefined() -> Length:
        """
                        Get an undefined length.
        
                        Returns:
                            Length: An undefined length.
        """
    def __add__(self, arg0: Length) -> Length:
        ...
    def __eq__(self, arg0: Length) -> bool:
        ...
    def __ge__(self, arg0: Length) -> bool:
        ...
    def __gt__(self, arg0: Length) -> bool:
        ...
    def __iadd__(self, arg0: Length) -> Length:
        ...
    def __imul__(self, arg0: float) -> Length:
        ...
    def __init__(self, arg0: ostk.core.type.Real, arg1: typing.Any) -> None:
        """
                        Constructor.
        
                        Args:
                            aReal (Real): A real number.
                            aUnit (Length.Unit): A length unit.
        """
    def __isub__(self, arg0: Length) -> Length:
        ...
    def __itruediv__(self, arg0: float) -> Length:
        ...
    def __le__(self, arg0: Length) -> bool:
        ...
    def __lt__(self, arg0: Length) -> bool:
        ...
    def __mul__(self, arg0: float) -> Length:
        ...
    def __ne__(self, arg0: Length) -> bool:
        ...
    def __neg__(self) -> Length:
        ...
    def __pos__(self) -> Length:
        ...
    def __repr__(self) -> str:
        ...
    def __rmul__(self, arg0: float) -> Length:
        ...
    def __str__(self) -> str:
        ...
    def __sub__(self, arg0: Length) -> Length:
        ...
    def __truediv__(self, arg0: float) -> Length:
        ...
    def get_unit(self) -> ...:
        """
                        Get the length unit.
        
                        Returns:
                            Length.Unit: The length unit.
        """
    def in_kilometers(self) -> ostk.core.type.Real:
        """
                        Get the length in kilometers.
        
                        Returns:
                            float: The length in kilometers.
        """
    def in_meters(self) -> ostk.core.type.Real:
        """
                        Get the length in meters.
        
                        Returns:
                            float: The length in meters.
        """
    def in_unit(self, arg0: typing.Any) -> ostk.core.type.Real:
        """
                        Get the length in a given unit.
        
                        Returns:
                            float: The length in the given unit.
        """
    def is_defined(self) -> bool:
        """
                        Check if the length is defined.
        
                        Returns:
                            bool: True if defined.
        """
    def is_zero(self) -> bool:
        """
                        Check if the length is zero.
        
                        Returns:
                            bool: True if zero.
        """
    def to_string(self, aPrecision: ostk.core.type.Integer = ...) -> ostk.core.type.String:
        """
                        Get the string representation of the length.
        
                        Args:
                            aPrecision (int): A precision.
        
                        Returns:
                            str: The string representation.
        """
class Mass:
    """
    
                Mass.
    
                https://en.wikipedia.org/wiki/Mass
            
    """
    class Unit:
        """
        Members:
        
          Undefined : 
                        Undefined.
                    
        
          Kilogram : 
                        Kilogram (SI).
                    
        
          Pound : 
                        Pound.
                    
        
          Tonne : 
                        Tonne.
                    
        """
        Kilogram: typing.ClassVar[Mass.Unit]  # value = <Unit.Kilogram: 1>
        Pound: typing.ClassVar[Mass.Unit]  # value = <Unit.Pound: 3>
        Tonne: typing.ClassVar[Mass.Unit]  # value = <Unit.Tonne: 2>
        Undefined: typing.ClassVar[Mass.Unit]  # value = <Unit.Undefined: 0>
        __members__: typing.ClassVar[dict[str, Mass.Unit]]  # value = {'Undefined': <Unit.Undefined: 0>, 'Kilogram': <Unit.Kilogram: 1>, 'Pound': <Unit.Pound: 3>, 'Tonne': <Unit.Tonne: 2>}
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
    def kilograms(arg0: ostk.core.type.Real) -> Mass:
        """
                        Create a mass in kilograms.
        
                        Returns:
                            Mass: A mass in kilograms.
        """
    @staticmethod
    def parse(arg0: ostk.core.type.String) -> Mass:
        """
                        Parse a mass.
        
                        Returns:
                            Mass: A mass.
        """
    @staticmethod
    def string_from_unit(arg0: typing.Any) -> ostk.core.type.String:
        """
                        Get string from unit.
        
                        Returns:
                            str: A string.
        """
    @staticmethod
    def symbol_from_unit(arg0: typing.Any) -> ostk.core.type.String:
        """
                        Get symbol from unit.
        
                        Returns:
                            str: A symbol.
        """
    @staticmethod
    def undefined() -> Mass:
        """
                        Get an undefined mass.
        
                        Returns:
                            Mass: An undefined mass.
        """
    def __eq__(self, arg0: Mass) -> bool:
        ...
    def __init__(self, arg0: ostk.core.type.Real, arg1: typing.Any) -> None:
        """
                    Constructor.
        
                    Args:
                        aReal (Real): A real number.
                        aUnit (Mass.Unit): A mass unit.
        """
    def __ne__(self, arg0: Mass) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def get_unit(self) -> ...:
        """
                        Get the mass unit.
        
                        Returns:
                            Mass.Unit: Mass unit.
        """
    def in_kilograms(self) -> ostk.core.type.Real:
        """
                        Convert mass to kilograms.
        
                        Returns:
                            float: Mass in kilograms.
        """
    def in_unit(self, arg0: typing.Any) -> ostk.core.type.Real:
        """
                        Convert mass to unit.
        
                        Returns:
                            float: Mass in unit.
        """
    def is_defined(self) -> bool:
        """
                        Check if the mass is defined.
        
                        Returns:
                            bool: True if defined.
        """
    def to_string(self, aPrecision: ostk.core.type.Integer = ...) -> ostk.core.type.String:
        """
                        Convert mass to string.
        
                        Args:
                            aPrecision (int): Precision.
        
                        Returns:
                            str: Mass as string.
        """
class Time:
    """
    
                Time.
    
                https://en.wikipedia.org/wiki/Unit_of_time
            
    """
    class Unit:
        """
        Members:
        
          Undefined : 
                        Undefined time unit.
                    
        
          Nanosecond : 
                        Nanosecond.
                    
        
          Microsecond : 
                        Microsecond.
                    
        
          Millisecond : 
                        Millisecond.
                    
        
          Second : 
                        Second (SI).
                    
        
          Minute : 
                        Minute.
                    
        
          Hour : 
                        Hour.
                    
        
          Day : 
                        Day.
                    
        
          Week : 
                        Week.
                    
        """
        Day: typing.ClassVar[Time.Unit]  # value = <Unit.Day: 7>
        Hour: typing.ClassVar[Time.Unit]  # value = <Unit.Hour: 6>
        Microsecond: typing.ClassVar[Time.Unit]  # value = <Unit.Microsecond: 2>
        Millisecond: typing.ClassVar[Time.Unit]  # value = <Unit.Millisecond: 3>
        Minute: typing.ClassVar[Time.Unit]  # value = <Unit.Minute: 5>
        Nanosecond: typing.ClassVar[Time.Unit]  # value = <Unit.Nanosecond: 1>
        Second: typing.ClassVar[Time.Unit]  # value = <Unit.Second: 4>
        Undefined: typing.ClassVar[Time.Unit]  # value = <Unit.Undefined: 0>
        Week: typing.ClassVar[Time.Unit]  # value = <Unit.Week: 8>
        __members__: typing.ClassVar[dict[str, Time.Unit]]  # value = {'Undefined': <Unit.Undefined: 0>, 'Nanosecond': <Unit.Nanosecond: 1>, 'Microsecond': <Unit.Microsecond: 2>, 'Millisecond': <Unit.Millisecond: 3>, 'Second': <Unit.Second: 4>, 'Minute': <Unit.Minute: 5>, 'Hour': <Unit.Hour: 6>, 'Day': <Unit.Day: 7>, 'Week': <Unit.Week: 8>}
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
    def string_from_unit(arg0: typing.Any) -> ostk.core.type.String:
        """
                        Get the string representation from a time unit.
        
                        Args:
                            aUnit (Time.Unit): A time unit.
        
                        Returns:
                            str: String representation.
        """
    @staticmethod
    def symbol_from_unit(arg0: typing.Any) -> ostk.core.type.String:
        """
                        Get the symbol representation from a time unit.
        
                        Args:
                            aUnit (Time.Unit): A time unit.
        
                        Returns:
                            str: Symbol representation.
        """
    @staticmethod
    def undefined() -> Time:
        """
                        Create an undefined time.
        
                        Returns:
                            Time: An undefined time.
        """
    def __eq__(self, arg0: Time) -> bool:
        ...
    def __init__(self, arg0: ostk.core.type.Real, arg1: typing.Any) -> None:
        """
                    Constructor.
        
                    Args:
                        aReal (Real): A real number.
                        aUnit (Time.Unit): A time unit.
        """
    def __ne__(self, arg0: Time) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def is_defined(self) -> bool:
        """
                        Check if the time is defined.
        
                        Returns:
                            bool: True if defined.
        """
    def to_string(self, aPrecision: ostk.core.type.Integer = ...) -> ostk.core.type.String:
        """
                        Convert time to string.
        
                        Args:
                            aPrecision (int): A precision.
        
                        Returns:
                            str: String representation.
        """
