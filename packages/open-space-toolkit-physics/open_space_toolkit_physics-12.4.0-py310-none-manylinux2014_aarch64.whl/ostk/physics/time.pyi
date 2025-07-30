from __future__ import annotations
import datetime
import ostk.core.type
import ostk.mathematics.object
import ostk.physics.unit
import typing
__all__ = ['Date', 'DateTime', 'Duration', 'Instant', 'Interval', 'Scale', 'Time']
class Date:
    """
    
                Date as year, month and day.
            
    """
    class Format:
        """
        Members:
        
          Undefined : 
                        Undefined date format.
                    
        
          Standard : 
                        Standard date format (YYYY-MM-DD).
                    
        
          STK : 
                        STK date format (d Mon YYYY).
                    
        """
        STK: typing.ClassVar[Date.Format]  # value = <Format.STK: 2>
        Standard: typing.ClassVar[Date.Format]  # value = <Format.Standard: 1>
        Undefined: typing.ClassVar[Date.Format]  # value = <Format.Undefined: 0>
        __members__: typing.ClassVar[dict[str, Date.Format]]  # value = {'Undefined': <Format.Undefined: 0>, 'Standard': <Format.Standard: 1>, 'STK': <Format.STK: 2>}
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
    def GPS_epoch() -> Date:
        """
                        GPS epoch (1980-01-06).
        
                        .. reference:: http://tycho.usno.navy.mil/gpstt.html
        
                        Returns:
                            Date: GPS epoch.
        """
    @staticmethod
    def J2000() -> Date:
        """
                        J2000 epoch (2000-01-01).
        
                        .. reference:: https://en.wikipedia.org/wiki/Epoch_(astronomy)#Julian_years_and_J2000
        
                        Returns:
                            Date: J2000 epoch.
        """
    @staticmethod
    def modified_julian_date_epoch() -> Date:
        """
                        Modified julian dates epoch (1858-11-17).
        
                        .. reference:: https://en.wikipedia.org/wiki/Julian_day
        
                        Returns:
                            Date: Modified Julian epoch.
        """
    @staticmethod
    def parse(aString: ostk.core.type.String, aFormat: Date.Format = ...) -> Date:
        ...
    @staticmethod
    def undefined() -> Date:
        """
                        Create an undefined date.
        
                        Returns:
                            Date: Undefined date.
        """
    @staticmethod
    def unix_epoch() -> Date:
        """
                        Unix epoch (1970-01-01).
        
                        .. reference:: https://en.wikipedia.org/wiki/Unix_time
        
                        Returns:
                            Date: Unix epoch.
        """
    def __eq__(self, arg0: Date) -> bool:
        ...
    def __init__(self, arg0: int, arg1: int, arg2: int) -> None:
        ...
    def __ne__(self, arg0: Date) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def get_day(self) -> int:
        """
                        Get day (1 - 31).
        
                        Returns:
                            int: Day.
        """
    def get_month(self) -> int:
        """
                        Get month (1 - 12).
        
                        Returns:
                            int: Month.
        """
    def get_year(self) -> int:
        """
                        Get year (1400 - 9999).
        
                        Returns:
                            int: Year.
        """
    def is_defined(self) -> bool:
        """
                        Check if the date is defined.
        
                        Returns:
                            bool: True if defined.
        """
    def set_day(self, arg0: int) -> None:
        """
                        Set day.
        
                        Args:
                            day (int): Day (1 - 31).
        """
    def set_month(self, arg0: int) -> None:
        """
                        Set month.
        
                        Args:
                            month (int): Month (1 - 12).
        """
    def set_year(self, arg0: int) -> None:
        """
                        Set year.
        
                        Args:
                            year (int): Year (1400 - 9999).
        """
    @typing.overload
    def to_string(self, arg0: typing.Any) -> ostk.core.type.String:
        """
                        Get string representation of date.
        
                        Args:
                            format (Date.Format): Date format.
        
                        Returns:
                            str: String representation of date.
        """
    @typing.overload
    def to_string(self) -> ostk.core.type.String:
        ...
    @typing.overload
    def to_string(self, arg0: typing.Any) -> ostk.core.type.String:
        ...
class DateTime:
    """
    
                Date-time.
            
    """
    class Format:
        """
        Members:
        
          Undefined : 
                        Undefined format.
                    
        
          Standard : 
                        Standard format (YYYY-MM-DD hh:mm:ss.sss.sss.sss).
                    
        
          ISO8601 : 
                        ISO 8601 format (YYYY-MM-DDThh:mm:ss.ssssss).
                    
        
          STK : 
                        STK format (d Mon YYYY hh:mm:ss.ssssss).
                    
        """
        ISO8601: typing.ClassVar[DateTime.Format]  # value = <Format.ISO8601: 2>
        STK: typing.ClassVar[DateTime.Format]  # value = <Format.STK: 3>
        Standard: typing.ClassVar[DateTime.Format]  # value = <Format.Standard: 1>
        Undefined: typing.ClassVar[DateTime.Format]  # value = <Format.Undefined: 0>
        __members__: typing.ClassVar[dict[str, DateTime.Format]]  # value = {'Undefined': <Format.Undefined: 0>, 'Standard': <Format.Standard: 1>, 'ISO8601': <Format.ISO8601: 2>, 'STK': <Format.STK: 3>}
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
    def GPS_epoch() -> DateTime:
        """
                        GPS epoch (1980-01-06 00:00:00.000.000.000).
        
                        Returns:
                            DateTime: Date-time at GPS epoch.
        """
    @staticmethod
    def J2000() -> DateTime:
        """
                        J2000 epoch (2000-01-01 12:00:00.000.000.00).
        
                        Returns:
                            DateTime: J2000 date-time.
        """
    @staticmethod
    def julian_date(julian_date: ostk.core.type.Real) -> DateTime:
        """
                        Date-time from Julian Date.
        
                        Args:
                            julian_date (float): A Julian Date.
        
                        Returns:
                            DateTime: Date-time.
        """
    @staticmethod
    def modified_julian_date(modified_julian_date: ostk.core.type.Real) -> DateTime:
        """
                        Date-time from Modified Julian Date.
        
                        Args:
                            modified_julian_date (float): A Modified Julian Date.
        
                        Returns:
                            DateTime: Date-time.
        """
    @staticmethod
    def modified_julian_date_epoch() -> DateTime:
        """
                        Modified Julian Date epoch (1858-11-17 00:00:00.000.000.000).
        
                        Returns:
                            Date-time: Date-time at Modified Julian Date epoch.
        """
    @staticmethod
    def parse(string: ostk.core.type.String, format: DateTime.Format = ...) -> DateTime:
        ...
    @staticmethod
    def undefined() -> DateTime:
        """
                        Create an undefined date-time.
        
                        Returns:
                            DateTime: Undefined date-time.
        """
    @staticmethod
    def unix_epoch() -> DateTime:
        """
                        Unix epoch (1970-01-01 00:00:00.000.000.000).
                        
                        Returns:
                            DateTime: Date-time at Unix epoch.
        """
    def __eq__(self, arg0: DateTime) -> bool:
        ...
    @typing.overload
    def __init__(self, date: typing.Any, time: typing.Any) -> None:
        """
                        Constructor.
        
                        Args:
                            date (Date): A date
                            time (Time): A time
        """
    @typing.overload
    def __init__(self, year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0, millisecond: int = 0, microsecond: int = 0, nanosecond: int = 0) -> None:
        """
                        Constructor.
        
                        Args:
                            year (int): Year
                            month (int): Month
                            day (int): Day
                            hour (int): Hour
                            minute (int): Minute
                            second (int): Second
                            millisecond (int): Millisecond
                            microsecond (int): Microsecond
                            nanosecond (int): Nanosecond
        """
    def __ne__(self, arg0: DateTime) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def get_date(self) -> ...:
        """
                        Get date.
        
                        Returns:
                            Date: Date.
        """
    def get_julian_date(self) -> ostk.core.type.Real:
        """
                        Get Julian date.
        
                        Returns:
                            float: Julian date.
        """
    def get_modified_julian_date(self) -> ostk.core.type.Real:
        """
                        Get Modified Julian date.
        
                        Returns:
                            float: Modified Julian date.
        """
    def get_time(self) -> ...:
        """
                        Get time.
        
                        Returns:
                            Time: Time.
        """
    def is_defined(self) -> bool:
        """
                        Check if the date-time is defined.
        
                        Returns:
                            bool: True if defined.
        """
    @typing.overload
    def to_string(self) -> ostk.core.type.String:
        ...
    @typing.overload
    def to_string(self, arg0: typing.Any) -> ostk.core.type.String:
        ...
class Duration:
    """
    
                Duration format.
            
    """
    class Format:
        """
        Members:
        
          Undefined : 
                        Undefined format.
                    
        
          Standard : 
                        Standard format (d hh:mm:ss.mmm.uuu.nnn)
                    
        
          ISO8601 : 
                        ISO 8601 format (PnDTnHnMnS)
                    
        """
        ISO8601: typing.ClassVar[Duration.Format]  # value = <Format.ISO8601: 2>
        Standard: typing.ClassVar[Duration.Format]  # value = <Format.Standard: 1>
        Undefined: typing.ClassVar[Duration.Format]  # value = <Format.Undefined: 0>
        __members__: typing.ClassVar[dict[str, Duration.Format]]  # value = {'Undefined': <Format.Undefined: 0>, 'Standard': <Format.Standard: 1>, 'ISO8601': <Format.ISO8601: 2>}
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
    def between(arg0: typing.Any, arg1: typing.Any) -> Duration:
        """
                        Constructs a duration between two instants
        
                        Returns:
                            Duration: Duration between two instants.
        """
    @staticmethod
    def days(arg0: ostk.core.type.Real) -> Duration:
        """
                        Create a duration in days.
        
                        Returns:
                            Duration: Duration in days.
        """
    @staticmethod
    def hours(arg0: ostk.core.type.Real) -> Duration:
        """
                        Create a duration in hours.
        
                        Returns:
                            Duration: Duration in hours.
        """
    @staticmethod
    def microseconds(arg0: ostk.core.type.Real) -> Duration:
        """
                        Create a duration in microseconds.
        
                        Returns:
                            Duration: Duration in microseconds.
        """
    @staticmethod
    def milliseconds(arg0: ostk.core.type.Real) -> Duration:
        """
                        Create a duration in milliseconds.
        
                        Returns:
                            Duration: Duration in milliseconds.
        """
    @staticmethod
    def minutes(arg0: ostk.core.type.Real) -> Duration:
        """
                        Create a duration in minutes.
        
                        Returns:
                            Duration: Duration in minutes.
        """
    @staticmethod
    def nanoseconds(arg0: ostk.core.type.Real) -> Duration:
        """
                        Create a duration in nanoseconds.
        
                        Returns:
                            Duration: Duration in nanoseconds.
        """
    @staticmethod
    def parse(string: ostk.core.type.String, format: Duration.Format = ...) -> Duration:
        ...
    @staticmethod
    def seconds(arg0: ostk.core.type.Real) -> Duration:
        """
                        Create a duration in seconds.
        
                        Returns:
                            Duration: Duration in seconds.
        """
    @staticmethod
    def undefined() -> Duration:
        """
                        Create an undefined duration.
        
                        Returns:
                            Duration: Undefined duration.
        """
    @staticmethod
    def weeks(arg0: ostk.core.type.Real) -> Duration:
        """
                        Create a duration in weeks.
        
                        Returns:
                            Duration: Duration in weeks.
        """
    @staticmethod
    def zero() -> Duration:
        """
                        Create a zero duration.
        
                        Returns:
                            Duration: Zero duration.
        """
    def __add__(self, arg0: Duration) -> Duration:
        ...
    def __eq__(self, arg0: Duration) -> bool:
        ...
    def __ge__(self, arg0: Duration) -> bool:
        ...
    def __gt__(self, arg0: Duration) -> bool:
        ...
    def __iadd__(self, arg0: Duration) -> Duration:
        ...
    def __imul__(self, arg0: float) -> Duration:
        ...
    @typing.overload
    def __init__(self, arg0: datetime.timedelta) -> None:
        """
                        Constructor.
                        Args:
                            count (int): A nanosecond count.
        """
    @typing.overload
    def __init__(self, duration: Duration) -> None:
        """
                        Copy constructor.
        
                        Args:
                            duration (Duration): The Duration.
        """
    def __isub__(self, arg0: Duration) -> Duration:
        ...
    def __itruediv__(self, arg0: float) -> Duration:
        ...
    def __le__(self, arg0: Duration) -> bool:
        ...
    def __lt__(self, arg0: Duration) -> bool:
        ...
    def __mul__(self, arg0: float) -> Duration:
        ...
    def __ne__(self, arg0: Duration) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __rmul__(self, arg0: float) -> Duration:
        ...
    def __str__(self) -> str:
        ...
    def __sub__(self, arg0: Duration) -> Duration:
        ...
    def __truediv__(self, arg0: float) -> Duration:
        ...
    def get_absolute(self) -> Duration:
        """
                        Get the absolute duration.
        
                        Returns:
                            Duration: Absolute duration.
        """
    def get_days(self) -> ostk.core.type.Integer:
        """
                        Get the day count.
        
                        Returns:
                            int: Day count.
        """
    def get_hours(self) -> ostk.core.type.Integer:
        """
                        Get the hour count.
        
                        Returns:
                            int: Hour count.
        """
    def get_microseconds(self) -> ostk.core.type.Integer:
        """
                        Get the microsecond count.
        
                        Returns:
                            int: Microsecond count.
        """
    def get_milliseconds(self) -> ostk.core.type.Integer:
        """
                        Get the millisecond count.
        
                        Returns:
                            int: Millisecond count.
        """
    def get_minutes(self) -> ostk.core.type.Integer:
        """
                        Get the minute count.
        
                        Returns:
                            int: Minute count.
        """
    def get_nanoseconds(self) -> ostk.core.type.Integer:
        """
                        Get the nanosecond count.
        
                        Returns:
                            int: Nanosecond count.
        """
    def get_seconds(self) -> ostk.core.type.Integer:
        """
                        Get the second count.
        
                        Returns:
                            int: Second count.
        """
    def get_weeks(self) -> ostk.core.type.Integer:
        """
                        Get the week count.
        
                        Returns:
                            int: Week count.
        """
    def in_days(self) -> ostk.core.type.Real:
        """
                        Get the duration in days.
        
                        Returns:
                            float: Duration in days.
        """
    def in_hours(self) -> ostk.core.type.Real:
        """
                        Get the duration in hours.
        
                        Returns:
                            float: Duration in hours.
        """
    def in_microseconds(self) -> ostk.core.type.Real:
        """
                        Get the duration in microseconds.
        
                        Returns:
                            float: Duration in microseconds.
        """
    def in_milliseconds(self) -> ostk.core.type.Real:
        """
                        Get the duration in milliseconds.
        
                        Returns:
                            float: Duration in milliseconds.
        """
    def in_minutes(self) -> ostk.core.type.Real:
        """
                        Get the duration in minutes.
        
                        Returns:
                            float: Duration in minutes.
        """
    def in_nanoseconds(self) -> ostk.core.type.Real:
        """
                        Get the duration in nanoseconds.
        
                        Returns:
                            float: Duration in nanoseconds.
        """
    def in_seconds(self) -> ostk.core.type.Real:
        """
                        Get the duration in seconds.
        
                        Returns:
                            float: Duration in seconds.
        """
    def in_unit(self, arg0: ostk.physics.unit.Time.Unit) -> ostk.core.type.Real:
        """
                        Get the duration in a unit.
        
                        Returns:
                            float: Duration in unit.
        """
    def in_weeks(self) -> ostk.core.type.Real:
        """
                        Get the duration in weeks.
        
                        Returns:
                            float: Duration in weeks.
        """
    def is_defined(self) -> bool:
        """
                        Check if the duration is defined.
        
                        Returns:
                            bool: True if defined.
        """
    def is_near(self, duration: Duration, tolerance: Duration) -> bool:
        """
                        Check if the duration is near another duration.
        
                        Args:
                            duration (Duration): Duration to compare with.
                            tolerance (Duration): Tolerance.
        
                        Returns:
                            bool: True if near.
        """
    def is_positive(self) -> bool:
        """
                        Check if the duration is positive.
        
                        Returns:
                            bool: True if positive.
        """
    def is_strictly_positive(self) -> bool:
        """
                        Check if the duration is strictly positive.
        
                        Returns:
                            bool: True if strictly positive.
        """
    def is_zero(self) -> bool:
        """
                        Check if the duration is zero.
        
                        Returns:
                            bool: True if zero.
        """
    @typing.overload
    def to_string(self) -> ostk.core.type.String:
        ...
    @typing.overload
    def to_string(self, arg0: typing.Any) -> ostk.core.type.String:
        ...
    def to_timedelta(self) -> datetime.timedelta:
        ...
class Instant:
    """
    
                Point in time.
            
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def GPS_epoch() -> Instant:
        """
                        Get the GPS epoch instant.
        
                        Returns:
                            Instant: GPS epoch instant.
        """
    @staticmethod
    def J2000() -> Instant:
        """
                        Get J2000 instant.
        
                        Returns:
                            Instant: J2000 instant.
        """
    @staticmethod
    def date_time(arg0: DateTime, arg1: Scale) -> Instant:
        """
                        Create an instant from a date-time.
        
                        Args:
                            date_time (DateTime): Date-time.
        
                        Returns:
                            Instant: Instant.
        """
    @staticmethod
    def julian_date(arg0: ostk.core.type.Real, arg1: Scale) -> Instant:
        """
                        Create an instant from a Julian date.
        
                        Args:
                            julian_date (float): Julian date.
        
                        Returns:
                            Instant: Instant.
        """
    @staticmethod
    def modified_julian_date(arg0: ostk.core.type.Real, arg1: Scale) -> Instant:
        """
                        Create an instant from a Modified Julian date.
        
                        Args:
                            modified_julian_date (float): Modified Julian date.
        
                        Returns:
                            Instant: Instant.
        """
    @staticmethod
    def now() -> Instant:
        """
                        Get current instant.
        
                        Returns:
                            Instant: Current instant.
        """
    @staticmethod
    def parse(string: ostk.core.type.String, scale: Scale, date_time_format: DateTime.Format = ...) -> Instant:
        """
                        Create an instant from a string representation.
        
                        Args:
                            string (str): String representation.
                            scale (Time.Scale): Time scale.
                            date_time_format (DateTime.Format): Date-time format.
        
        
                        Returns:
                            Instant: Instant.
        """
    @staticmethod
    def undefined() -> Instant:
        """
                        Create an undefined instant.
        
                        Returns:
                            Instant: Undefined instant.
        """
    def __add__(self, arg0: Duration) -> Instant:
        ...
    def __eq__(self, arg0: Instant) -> bool:
        ...
    def __ge__(self, arg0: Instant) -> bool:
        ...
    def __gt__(self, arg0: Instant) -> bool:
        ...
    def __iadd__(self, arg0: Duration) -> Instant:
        ...
    def __isub__(self, arg0: Duration) -> Instant:
        ...
    def __le__(self, arg0: Instant) -> bool:
        ...
    def __lt__(self, arg0: Instant) -> bool:
        ...
    def __ne__(self, arg0: Instant) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    @typing.overload
    def __sub__(self, arg0: Instant) -> Duration:
        ...
    @typing.overload
    def __sub__(self, arg0: Duration) -> Instant:
        ...
    def get_date_time(self, arg0: Scale) -> DateTime:
        """
                        Get date-time.
        
                        Returns:
                            DateTime: Date-time.
        """
    def get_julian_date(self, arg0: Scale) -> ostk.core.type.Real:
        """
                        Get Julian date.
        
                        Returns:
                            float: Julian date.
        """
    def get_leap_second_count(self) -> int:
        """
                        Get leap second count.
        
                        Returns:
                            int: Leap second count.
        """
    def get_modified_julian_date(self, arg0: Scale) -> ostk.core.type.Real:
        """
                        Get Modified Julian date.
        
                        Returns:
                            float: Modified Julian date.
        """
    def is_defined(self) -> bool:
        """
                        Check if the instant is defined.
        
                        Returns:
                            bool: True if defined.
        """
    def is_near(self, arg0: Instant, arg1: Duration) -> bool:
        """
                        Check if instant is near another instant
        
                        Return:
                            bool: True if near
        """
    def is_post_epoch(self) -> bool:
        """
                        Check if the instant is post-epoch (J2000).
        
                        Returns:
                            bool: True if post-epoch.
        """
    def to_string(self, scale: Scale = ..., date_time_format: DateTime.Format = ...) -> ostk.core.type.String:
        """
                        Convert to string.
        
                        Args:
                            scale (Time.Scale): Time scale.
                            date_time_format (DateTime.Format): Date-time format.
        
                        Returns:
                            str: String representation.
        """
class Interval:
    """
    
                Time interval.
            
    """
    class Type:
        """
        Members:
        
          Undefined : 
                        Undefined interval type.
                    
        
          Closed : 
                        Closed interval type.
                    
        
          Open : 
                        Open interval type.
                    
        
          HalfOpenLeft : 
                        Half-open left interval type.
                    
        
          HalfOpenRight : 
                        Half-open right interval type.
                    
        """
        Closed: typing.ClassVar[Interval.Type]  # value = <Type.Closed: 1>
        HalfOpenLeft: typing.ClassVar[Interval.Type]  # value = <Type.HalfOpenLeft: 3>
        HalfOpenRight: typing.ClassVar[Interval.Type]  # value = <Type.HalfOpenRight: 4>
        Open: typing.ClassVar[Interval.Type]  # value = <Type.Open: 2>
        Undefined: typing.ClassVar[Interval.Type]  # value = <Type.Undefined: 0>
        __members__: typing.ClassVar[dict[str, Interval.Type]]  # value = {'Undefined': <Type.Undefined: 0>, 'Closed': <Type.Closed: 1>, 'Open': <Type.Open: 2>, 'HalfOpenLeft': <Type.HalfOpenLeft: 3>, 'HalfOpenRight': <Type.HalfOpenRight: 4>}
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
    def centered(instant: typing.Any, duration: Duration, type: ostk.mathematics.object.RealInterval.Type) -> Interval:
        """
                        Create a centered interval.
        
                        Args:
                            instant (Instant): Central instant.
                            duration (Duration): Duration.
                            type (Interval.Type): Interval type.
        
                        Returns:
                            Interval: Centered interval.
        """
    @staticmethod
    def clip(intervals: list[Interval], interval: Interval) -> list[Interval]:
        """
                        Creates a clipped list of intervals.
        
                        ```
                        intervals = [[1, 3], [5, 7], [9, 11]]
                        interval = [4, 10]
                        output = [[5, 7], [9, 10]]
                        ```
        
                        Args:
                            intervals (list[Interval]): A list of intervals.
                            interval (Interval): The clipping interval.
        
                        Returns:
                            list[Interval]: Clipped intervals.
        """
    @staticmethod
    def closed(start_instant: typing.Any, end_instant: typing.Any) -> Interval:
        """
                        Create a closed interval.
        
                        Args:
                            start_instant (Instant): Start instant.
                            end_instant (Instant): End instant.
        
                        Returns:
                            Interval: Closed interval.
        """
    @staticmethod
    def get_gaps(intervals: list[Interval], interval: Interval = ...) -> list[Interval]:
        """
                        Creates a list of intervals gaps.
        
                        ```
                        intervals = [[1, 3], [5, 7], [9, 11]]
                        interval = [0, 12]
                        output = [[0, 1], [3, 5], [7, 9], [11, 12]]
                        ```
        
                        Args:
                            intervals (list[Interval]): A list of intervals.
                            interval (Interval): The analysis interval. Used to compute gaps for the first and last interval. Defaults to Undefined.
        
                        Returns:
                            list[Interval]: Intervals gaps.
        """
    @staticmethod
    def half_open_left(start_instant: typing.Any, end_instant: typing.Any) -> Interval:
        """
                        Create a half-open left interval.
        
                        Args:
                            start_instant (Instant): Start instant.
                            end_instant (Instant): End instant.
        
                        Returns:
                            Interval: Half-open left interval.
        """
    @staticmethod
    def half_open_right(start_instant: typing.Any, end_instant: typing.Any) -> Interval:
        """
                        Create a half-open right interval.
        
                        Args:
                            start_instant (Instant): Start instant.
                            end_instant (Instant): End instant.
        
                        Returns:
                            Interval: Half-open right interval.
        """
    @staticmethod
    def logical_and(intervals_1: list[Interval], intervals_2: list[Interval]) -> list[Interval]:
        """
                        Creates a list of intervals by a logical-and conjunction.
        
                        ```
                        intervals_1 = [[-1, 1], [2, 4]]
                        intervals_2 = [[0.5, 1.5], [3, 5], [7, 8]]
                        output = [[0.5, 1], [3, 4]]
                        ```
        
                        Args:
                            intervals_1 (list[Interval]): A list of intervals.
                            intervals_2 (list[Interval]): Another list of intervals.
        
                        Returns:
                            list[Interval]: Logical-and intervals.
        """
    @staticmethod
    def logical_or(intervals_1: list[Interval], intervals_2: list[Interval]) -> list[Interval]:
        """
                        Creates a list of intervals by a logical-or conjunction.
        
                        ```
                        intervals_1 = [[-1, 1], [2, 4]]
                        intervals_2 = [[0.5, 1.5], [3, 5], [7, 8]]
                        output = [[-1, 1.5], [2, 5], [7, 8]]
                        ```
        
                        Args:
                            intervals_1 (list[Interval]): A list of intervals.
                            intervals_2 (list[Interval]): Another list of intervals.
        
                        Returns:
                            list[Interval]: Logical-or intervals.
        """
    @staticmethod
    def merge(intervals: list[Interval]) -> list[Interval]:
        """
                        Creates a merged list of intervals.
        
                        ```
                        intervals = [[1, 3], [2, 4], [5, 7]]
                        output = [[1, 4], [5, 7]]
                        ```
        
                        Args:
                            intervals (list[Interval]): A list of intervals.
        
                        Returns:
                            list[Interval]: Merged intervals.
        """
    @staticmethod
    def open(start_instant: typing.Any, end_instant: typing.Any) -> Interval:
        """
                        Create a open interval.
        
                        Args:
                            start_instant (Instant): Start instant.
                            end_instant (Instant): End instant.
        
                        Returns:
                            Interval: Open interval.
        """
    @staticmethod
    def parse(arg0: ostk.core.type.String) -> Interval:
        """
                        Parse an interval from a string representation.
        
                        Args:
                            (str): String representation.
        
                        Returns:
                            Interval: Interval.
        """
    @staticmethod
    def sort(intervals: list[Interval], by_lower_bound: bool = True, ascending: bool = True) -> list[Interval]:
        """
                        Creates a sorted list of intervals.
        
                        Args:
                            intervals (list[Interval]): A list of intervals.
                            by_lower_bound (bool): Use lower bound for sorting. Defaults to True.
                            ascending (bool): Sort in ascending order. Defaults to True.
        
                        Returns:
                            list[Interval]: Sorted intervals.
        """
    @staticmethod
    def undefined() -> Interval:
        """
                        Create an undefined interval.
        
                        Returns:
                            Interval: Undefined interval.
        """
    def __eq__(self, arg0: Interval) -> bool:
        ...
    def __init__(self, start_instant: typing.Any, end_instant: typing.Any, type: ostk.mathematics.object.RealInterval.Type) -> None:
        """
                        Constructor.
        
                        Args:
                            start_instant (Instant): Start instant.
                            end_instant (Instant): End instant.
                            type (Interval.Type): Interval type.
        """
    def __ne__(self, arg0: Interval) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def contains_instant(self, instant: typing.Any) -> bool:
        """
                        Check if the interval contains an instant.
        
                        Args:
                            instant (Instant): An instant.
        
                        Returns:
                            bool: True if the interval contains the instant.
        """
    def contains_interval(self, interval: Interval) -> bool:
        """
                        Check if the interval contains another interval.
        
                        Args:
                            interval (Interval): Another interval.
        
                        Returns:
                            bool: True if the interval contains the other interval.
        """
    def generate_grid(self, arg0: Duration) -> list[...]:
        """
                        Generate a grid of instants with a given time step.
        
                        Args:
                            (Duration): Time step.
        
                        Returns:
                            list[Instant]: Grid of instants.
        """
    def get_center(self) -> ...:
        """
                        Get the center instant.
        
                        Returns:
                            Instant: Center instant.
        """
    def get_duration(self) -> Duration:
        """
                        Get the duration.
        
                        Returns:
                            Duration: Duration.
        """
    def get_end(self) -> ...:
        """
                        Get the end instant.
        
                        Returns:
                            Instant: End instant.
        """
    def get_intersection_with(self, arg0: Interval) -> Interval:
        """
                        Get the intersection with another interval.
        
                        Args:
                            (Interval): Another interval.
        
                        Returns:
                            Interval: Intersection interval (Undefined if there is no intersection).
        """
    def get_lower_bound(self) -> ...:
        """
                        Get the lower bound.
        
                        Returns:
                            Instant: Lower bound.
        """
    def get_start(self) -> ...:
        """
                        Get the start instant.
        
                        Returns:
                            Instant: Start instant.
        """
    def get_type(self) -> ostk.mathematics.object.RealInterval.Type:
        """
                        Get the type of the interval.
        
                        Returns:
                            Interval.Type: The type of the interval.
        """
    def get_union_with(self, arg0: Interval) -> Interval:
        """
                        Get the union with another interval.
        
                        Args:
                            (Interval): Another interval.
        
                        Returns:
                            Interval: Union interval (Undefined if there is no single-interval union).
        """
    def get_upper_bound(self) -> ...:
        """
                        Get the upper bound.
        
                        Returns:
                            Instant: Upper bound.
        """
    def intersects(self, interval: Interval) -> bool:
        """
                        Check if the interval intersects another interval.
        
                        Args:
                            interval (Interval): Another interval.
        
                        Returns:
                            bool: True if the interval intersects another interval.
        """
    def is_defined(self) -> bool:
        """
                        Check if the interval is defined.
        
                        Returns:
                            bool: True if defined.
        """
    def is_degenerate(self) -> bool:
        """
                        Check if interval is degenerate, i.e. its lower and upper bounds are the equal.
        
                        Returns:
                            bool: True if degenerate.
        """
    def to_datetime_span(self, scale: Scale = ...) -> tuple[DateTime, DateTime]:
        """
                        Get the datetime span.
        
                        Args:
                            scale (Scale): Time scale. Defaults to UTC.
        
                        Returns:
                            tuple[datetime, datetime]: Datetime span.
        """
    def to_string(self, time_scale: Scale = ...) -> ostk.core.type.String:
        """
                        Convert the interval to a string.
        
                        Args:
                            time_scale (Scale): Time scale.
        
                        Returns:
                            str: String representation of the interval.
        """
class Scale:
    """
    
                Time scale.
    
                See also:
                    - [SOFA](http://www.iausofa.org/sofa_ts_c.pdf)
                    - [Times](https://www.cv.nrao.edu/~rfisher/Ephemerides/times.html)
                    - [Time](http://stjarnhimlen.se/comp/time.html)
                    - [GNSS](http://www.navipedia.net/index.php/Time_References_in_GNSS)
                    - [GNSS](Springer Handbook of Global Navigation Satellite Systems)
            
    
    Members:
    
      Undefined : 
                    Undefined time.
                
    
      UTC : 
                    Coordinated Universal Time.
                
    
      TT : 
                    Terrestial Time (a.k.a. TDT).
                
    
      TAI : 
                    International Atomic Time.
                
    
      UT1 : 
                    Universal Time.
                
    
      TCG : 
                    Geocentric Coordinate Time.
                
    
      TCB : 
                    Barycentric Coordinate Time.
                
    
      TDB : 
                    Barycentric Dynamic Time.
                
    
      GMST : 
                    Greenwich Mean Sidereal Time.
                
    
      GPST : 
                    Global Positioning System (GPS) Time.
                
    
      GST : 
                    Galileo System Time.
                
    
      GLST : 
                    GLONASS Time.
                
    
      BDT : 
                    BeiDou Time.
                
    
      QZSST : 
                    Quasi-Zenith Satellite System (QZSS) Time.
                
    
      IRNSST : 
                    Indian Regional Navigation Satellite System (IRNSS) Time.
                
    """
    BDT: typing.ClassVar[Scale]  # value = <Scale.BDT: 12>
    GLST: typing.ClassVar[Scale]  # value = <Scale.GLST: 11>
    GMST: typing.ClassVar[Scale]  # value = <Scale.GMST: 8>
    GPST: typing.ClassVar[Scale]  # value = <Scale.GPST: 9>
    GST: typing.ClassVar[Scale]  # value = <Scale.GST: 10>
    IRNSST: typing.ClassVar[Scale]  # value = <Scale.IRNSST: 14>
    QZSST: typing.ClassVar[Scale]  # value = <Scale.QZSST: 13>
    TAI: typing.ClassVar[Scale]  # value = <Scale.TAI: 3>
    TCB: typing.ClassVar[Scale]  # value = <Scale.TCB: 6>
    TCG: typing.ClassVar[Scale]  # value = <Scale.TCG: 5>
    TDB: typing.ClassVar[Scale]  # value = <Scale.TDB: 7>
    TT: typing.ClassVar[Scale]  # value = <Scale.TT: 2>
    UT1: typing.ClassVar[Scale]  # value = <Scale.UT1: 4>
    UTC: typing.ClassVar[Scale]  # value = <Scale.UTC: 1>
    Undefined: typing.ClassVar[Scale]  # value = <Scale.Undefined: 0>
    __members__: typing.ClassVar[dict[str, Scale]]  # value = {'Undefined': <Scale.Undefined: 0>, 'UTC': <Scale.UTC: 1>, 'TT': <Scale.TT: 2>, 'TAI': <Scale.TAI: 3>, 'UT1': <Scale.UT1: 4>, 'TCG': <Scale.TCG: 5>, 'TCB': <Scale.TCB: 6>, 'TDB': <Scale.TDB: 7>, 'GMST': <Scale.GMST: 8>, 'GPST': <Scale.GPST: 9>, 'GST': <Scale.GST: 10>, 'GLST': <Scale.GLST: 11>, 'BDT': <Scale.BDT: 12>, 'QZSST': <Scale.QZSST: 13>, 'IRNSST': <Scale.IRNSST: 14>}
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
class Time:
    """
    
                Time as hour, minute, second, millisecond, microsecond and nanosecond.
            
    """
    class Format:
        """
        Members:
        
          Undefined : 
                        Undefined time format.
                    
        
          Standard : 
                        Standard time format.
                    
        
          ISO8601 : 
                        ISO 8601 time format.
                    
        """
        ISO8601: typing.ClassVar[Time.Format]  # value = <Format.ISO8601: 2>
        Standard: typing.ClassVar[Time.Format]  # value = <Format.Standard: 1>
        Undefined: typing.ClassVar[Time.Format]  # value = <Format.Undefined: 0>
        __members__: typing.ClassVar[dict[str, Time.Format]]  # value = {'Undefined': <Format.Undefined: 0>, 'Standard': <Format.Standard: 1>, 'ISO8601': <Format.ISO8601: 2>}
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
    def hours(value: ostk.core.type.Real) -> Time:
        """
                        Create a time from a real number of hours.
        
                        Args:
                            value (float): A real number of hours.
        
                        Returns:
                            Time: Time.
        """
    @staticmethod
    def midnight() -> Time:
        """
                        Create a time at midnight.
        
                        Returns:
                            Time: Time at midnight.
        """
    @staticmethod
    def noon() -> Time:
        """
                        Create a time at noon.
        
                        Returns:
                            Time: Time at noon.
        """
    @staticmethod
    def parse(string: ostk.core.type.String, format: Time.Format = ...) -> Time:
        """
                        Create a time from a string representation.
        
                        Args:
                            string (str): A string.
                            format (Time.Format, optional): A time format (automatic detection if Undefined).
        
                        Returns:
                            Time: Time.
        """
    @staticmethod
    def seconds(value: ostk.core.type.Real) -> Time:
        """
                        Create a time from a real number of seconds.
        
                        Args:
                            value (float): A real number of seconds.
        
                        Returns:
                            Time: Time.
        """
    @staticmethod
    def undefined() -> Time:
        """
                        Create an undefined time.
        
                        Returns:
                            Time: Undefined time.
        """
    def __eq__(self, arg0: Time) -> bool:
        ...
    @typing.overload
    def __init__(self, arg0: int, arg1: int, arg2: int, arg3: int, arg4: int, arg5: int) -> None:
        """
                        Constructor.
        
                        Args:
                            an_hour (int): An hour count (0 - 23).
                            a_minute (int): A minute count (0 - 59).
                            a_second (int): A second count (0 - 60).
                            a_millisecond (int): A millisecond count (0 - 999).
                            a_microsecond (int): A microsecond count (0 - 999).
                            a_nanosecond (int): A nanosecond count (0 - 999).
        """
    @typing.overload
    def __init__(self, arg0: int, arg1: int, arg2: int) -> None:
        """
                        Constructor.
        
                        Args:
                            an_hour (int): An hour count (0 - 23).
                            a_minute (int): A minute count (0 - 59).
                            a_second (int): A second count (0 - 60).
        """
    def __ne__(self, arg0: Time) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def get_floating_seconds(self) -> ostk.core.type.Real:
        """
                        Get floating seconds.
        
                        Returns:
                            float: Floating seconds.
        """
    def get_hour(self) -> int:
        """
                        Get hour count.
        
                        Returns:
                            int: Hour count.
        """
    def get_microsecond(self) -> int:
        """
                        Get microsecond count.
        
                        Returns:
                            int: Microsecond count.
        """
    def get_millisecond(self) -> int:
        """
                        Get millisecond count.
        
                        Returns:
                            int: Millisecond count.
        """
    def get_minute(self) -> int:
        """
                        Get minute count.
        
                        Returns:
                            int: Minute count.
        """
    def get_nanosecond(self) -> int:
        """
                        Get nanosecond count.
        
                        Returns:
                            int: Nanosecond count.
        """
    def get_second(self) -> int:
        """
                        Get second count.
        
                        Returns:
                            int: Second count.
        """
    def get_total_floating_hours(self) -> ostk.core.type.Real:
        """
                        Get total floating hours.
        
                        Returns:
                            float: Total floating hours.
        """
    def get_total_floating_seconds(self) -> ostk.core.type.Real:
        """
                        Get total floating seconds.
        
                        Returns:
                            float: Total floating seconds.
        """
    def is_defined(self) -> bool:
        """
                        Check if the time is defined.
        
                        Returns:
                            bool: True if defined
        """
    def set_hour(self, arg0: int) -> None:
        """
                        Set hour count.
        
                        Args:
                            an_hour (int): An hour count (0 - 23).
        """
    def set_microsecond(self, arg0: int) -> None:
        """
                        Set microsecond count.
        
                        Args:
                            a_microsecond (int): A microsecond count (0 - 999).
        """
    def set_millisecond(self, arg0: int) -> None:
        """
                        Set millisecond count.
        
                        Args:
                            a_millisecond (int): A millisecond count (0 - 999).
        """
    def set_minute(self, arg0: int) -> None:
        """
                        Set minute count.
        
                        Args:
                            a_minute (int): A minute count (0 - 59).
        """
    def set_nanosecond(self, arg0: int) -> None:
        """
                        Set nanosecond count.
        
                        Args:
                            a_nanosecond (int): A nanosecond count (0 - 999).
        """
    def set_second(self, arg0: int) -> None:
        """
                        Set second count.
        
                        Args:
                            a_second (int): A second count (0 - 60).
        """
    @typing.overload
    def to_string(self, arg0: Time.Format) -> ostk.core.type.String:
        """
                        Get string representation of time.
        
                        Returns:
                            str: String representation of time.
        """
    @typing.overload
    def to_string(self) -> ostk.core.type.String:
        """
                        Get string representation of time.
        
                        Returns:
                            str: String representation of time.
        """
    @typing.overload
    def to_string(self, arg0: Time.Format) -> ostk.core.type.String:
        """
                        Get string representation of time.
        
                        Args:
                            aFormat (Time.Format): Time format.
        
                        Returns:
                            str: String representation of time.
        """
