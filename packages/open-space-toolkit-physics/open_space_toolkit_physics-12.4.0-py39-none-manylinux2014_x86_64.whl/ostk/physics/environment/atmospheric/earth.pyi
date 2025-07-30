from __future__ import annotations
import ostk.core.filesystem
import ostk.core.type
import ostk.physics
import ostk.physics.coordinate
import ostk.physics.coordinate.spherical
import ostk.physics.environment.object
import ostk.physics.time
import ostk.physics.unit
import typing
__all__ = ['CSSISpaceWeather', 'Exponential', 'Manager', 'NRLMSISE00']
class CSSISpaceWeather:
    """
    
                Center for Space Weather and Innovation (CSSI) Space Weather data file.
    
                Consolidated data set which contains solar radiation and geomagnetic indices.
                Particularly contains the F10.7 solar flux index and Ap/Kp geomagnetic indices,
                which are commonly used to model atmospheric density.
    
                :reference: http://celestrak.org/SpaceData/SpaceWx-format.php
    
            
    """
    class Reading:
        """
        
                    CSSI Space Weather reading.
        
                
        """
        @property
        def ap_1(self) -> ostk.core.type.Integer:
            """
                            Planetary Equivalent Amplitude (Ap) for 0000-0300 UT.
            """
        @property
        def ap_2(self) -> ostk.core.type.Integer:
            """
                            Planetary Equivalent Amplitude (Ap) for 0300-0600 UT.
            """
        @property
        def ap_3(self) -> ostk.core.type.Integer:
            """
                            Planetary Equivalent Amplitude (Ap) for 0600-0900 UT.
            """
        @property
        def ap_4(self) -> ostk.core.type.Integer:
            """
                            Planetary Equivalent Amplitude (Ap) for 0900-1200 UT.
            """
        @property
        def ap_5(self) -> ostk.core.type.Integer:
            """
                            Planetary Equivalent Amplitude (Ap) for 1200-1500 UT.
            """
        @property
        def ap_6(self) -> ostk.core.type.Integer:
            """
                            Planetary Equivalent Amplitude (Ap) for 1500-1800 UT.
            """
        @property
        def ap_7(self) -> ostk.core.type.Integer:
            """
                            Planetary Equivalent Amplitude (Ap) for 1800-2100 UT.
            """
        @property
        def ap_8(self) -> ostk.core.type.Integer:
            """
                            Planetary Equivalent Amplitude (Ap) for 2100-0000 UT.
            """
        @property
        def ap_avg(self) -> ostk.core.type.Integer:
            """
                            Arithmetic average of the 8 Ap indices for the day.
            """
        @property
        def bsrn(self) -> ostk.core.type.Integer:
            """
                            Bartels Solar Rotation Number. A sequence of 27-day intervals counted continuously from 1832 Feb 8.
            """
        @property
        def c9(self) -> ostk.core.type.Integer:
            """
                            C9. A conversion of the 0-to-2.5 range of the Cp index to one digit between 0 and 9.
            """
        @property
        def cp(self) -> ostk.core.type.Real:
            """
                            Cp or Planetary Daily Character Figure. A qualitative estimate of overall level of magnetic activity for the day determined from the sum of the 8 Ap indices. Cp ranges, in steps of one-tenth, from 0 (quiet) to 2.5 (highly disturbed).
            """
        @property
        def date(self) -> ostk.physics.time.Date:
            """
                            UTC day of reading.
            """
        @property
        def f107_adj(self) -> ostk.core.type.Real:
            """
                            10.7-cm Solar Radio Flux (F10.7) adjusted to 1 AU.
            """
        @property
        def f107_adj_center_81(self) -> ostk.core.type.Real:
            """
                            Centered 81-day arithmetic average of F10.7 (adjusted).
            """
        @property
        def f107_adj_last_81(self) -> ostk.core.type.Real:
            """
                            Last 81-day arithmetic average of F10.7 (adjusted).
            """
        @property
        def f107_data_type(self) -> ostk.core.type.String:
            """
                            Flux Qualifier.
                            - OBS: Observed flux measurement.
                            - INT: CelesTrak linear interpolation of missing data.
                            - PRD: 45-Day predicted flux.
                            - PRM: Monthly predicted flux.
            """
        @property
        def f107_obs(self) -> ostk.core.type.Real:
            """
                            Observed 10.7-cm Solar Radio Flux (F10.7). Measured at Ottawa at 1700 UT daily from 1947 Feb 14 until 1991 May 31 and measured at Penticton at 2000 UT from 1991 Jun 01 on. Expressed in units of 10-22 W/m2/Hz.
            """
        @property
        def f107_obs_center_81(self) -> ostk.core.type.Real:
            """
                            Centered 81-day arithmetic average of F107 (observed).
            """
        @property
        def f107_obs_last_81(self) -> ostk.core.type.Real:
            """
                            Last 81-day arithmetic average of F107 (observed).
            """
        @property
        def isn(self) -> ostk.core.type.Integer:
            """
                            International Sunspot Number. Records contain the Zurich number through 1980 Dec 31 and the International Brussels number thereafter.
            """
        @property
        def kp_1(self) -> ostk.core.type.Integer:
            """
                            Planetary 3-hour Range Index (Kp) for 0000-0300 UT.
            """
        @property
        def kp_2(self) -> ostk.core.type.Integer:
            """
                            Planetary 3-hour Range Index (Kp) for 0300-0600 UT.
            """
        @property
        def kp_3(self) -> ostk.core.type.Integer:
            """
                            Planetary 3-hour Range Index (Kp) for 0600-0900 UT.
            """
        @property
        def kp_4(self) -> ostk.core.type.Integer:
            """
                            Planetary 3-hour Range Index (Kp) for 0900-1200 UT.
            """
        @property
        def kp_5(self) -> ostk.core.type.Integer:
            """
                            Planetary 3-hour Range Index (Kp) for 1200-1500 UT.
            """
        @property
        def kp_6(self) -> ostk.core.type.Integer:
            """
                            Planetary 3-hour Range Index (Kp) for 1500-1800 UT.
            """
        @property
        def kp_7(self) -> ostk.core.type.Integer:
            """
                            Planetary 3-hour Range Index (Kp) for 1800-2100 UT.
            """
        @property
        def kp_8(self) -> ostk.core.type.Integer:
            """
                            Planetary 3-hour Range Index (Kp) for 2100-0000 UT.
            """
        @property
        def kp_sum(self) -> ostk.core.type.Integer:
            """
                            Sum of the 8 Kp indices for the day.
            """
        @property
        def nd(self) -> ostk.core.type.Integer:
            """
                            Number of Day within the Bartels 27-day cycle (01-27).
            """
    @staticmethod
    def load(file: ostk.core.filesystem.File) -> CSSISpaceWeather:
        """
                        Load CSSI Space Weather file in csv format.
        
                        Args:
                            file (File): A csv file.
        
                        Returns:
                            CSSISpaceWeather: CSSI Space Weather object.
        """
    @staticmethod
    def load_legacy(file: ostk.core.filesystem.File) -> CSSISpaceWeather:
        """
                        Load CSSI Space Weather file in legacy .txt format.
        
                        Args:
                            file (File): A txt file.
        
                        Returns:
                            CSSISpaceWeather: CSSI Space Weather object.
        """
    @staticmethod
    def undefined() -> CSSISpaceWeather:
        """
                        Create an undefined CSSI Space Weather object.
        
                        Returns:
                            CSSISpaceWeather: Undefined CSSI Space Weather object.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def access_daily_prediction_at(self, instant: ostk.physics.time.Instant) -> ...:
        """
                        Access daily prediction at instant.
        
                        Args:
                            instant (Instant): An instant.
        
                        Returns:
                            Reading: Daily prediction at instant.
        """
    def access_daily_prediction_interval(self) -> ostk.physics.time.Interval:
        """
                        Access daily prediction interval.
        
                        Returns:
                            Interval: Daily prediction interval.
        """
    def access_last_observation_date(self) -> ostk.physics.time.Date:
        """
                        Access last observation Date. File publication date is the day following the last observation.
        
                        Returns:
                            Date: Last observation Date.
        """
    def access_last_reading_where(self, predicate: typing.Callable[[...], bool], instant: ostk.physics.time.Instant) -> ...:
        """
                        Access last reading before an Instant where a Predicate is true.
        
                        Args:
                            predicate (Predicate): A predicate.
                            instant (Instant): An instant.
        
                        Returns:
                            Reading: Last Reading satisfying predicate.
        """
    def access_monthly_prediction_at(self, instant: ostk.physics.time.Instant) -> ...:
        """
                        Access monthly prediction at instant.
        
                        Args:
                            instant (Instant): An instant.
        
                        Returns:
                            Reading: Monthly prediction at instant.
        """
    def access_monthly_prediction_interval(self) -> ostk.physics.time.Interval:
        """
                        Access monthly prediction interval.
        
                        Returns:
                            Interval: Monthly prediction interval.
        """
    def access_observation_at(self, instant: ostk.physics.time.Instant) -> ...:
        """
                        Access observation at instant.
        
                        Args:
                            instant (Instant): An instant.
        
                        Returns:
                            Reading: Observation at instant.
        """
    def access_observation_interval(self) -> ostk.physics.time.Interval:
        """
                        Access observation interval.
        
                        Returns:
                            Interval: Observation interval.
        """
    def access_reading_at(self, instant: ostk.physics.time.Instant) -> ...:
        """
                        Access reading at Instant. Look first in observations, then in daily predictions, then monthly predictions.
        
                        Args:
                            instant (Instant): An instant.
        
                        Returns:
                            Reading: Reading at instant.
        """
    def is_defined(self) -> bool:
        """
                        Check if the CSSI Space Weather data is defined.
        
                        Returns:
                            bool: True if defined.
        """
class Exponential:
    """
    
                Exponential atmospheric model.
    
            
    """
    def __init__(self) -> None:
        ...
    def get_density_at(self, lla: ostk.physics.coordinate.spherical.LLA, instant: ostk.physics.time.Instant) -> ostk.core.type.Real:
        """
                        Get the atmospheric density value at a given position and instant.
        
                        Args:
                            lla (LLA): A position, expressed as latitude, longitude, altitude [deg, deg, m].
                            instant (Instant): An Instant.
        
                        Returns:
                            float: Atmospheric density value.
        """
    def is_defined(self) -> bool:
        """
                        Check if the exponential atmospheric model is defined.
        
                        Returns:
                            bool: True if the exponential atmospheric model is defined.
        """
class Manager(ostk.physics.Manager):
    """
    
                CSSI space weather manager.
    
                The following environment variables can be defined:
    
                - "OSTK_PHYSICS_ENVIRONMENT_ATMOSPHERIC_EARTH_MANAGER_MODE" will override "DefaultMode"
                - "OSTK_PHYSICS_ENVIRONMENT_ATMOSPHERIC_EARTH_MANAGER_LOCAL_REPOSITORY" will override "DefaultLocalRepository"
                - "OSTK_PHYSICS_ENVIRONMENT_ATMOSPHERIC_EARTH_MANAGER_LOCAL_REPOSITORY_LOCK_TIMEOUT" will override "DefaultLocalRepositoryLockTimeout"
    
                :reference: https://ai-solutions.com/_help_Files/cssi_space_weather_file.htm
            
    """
    @staticmethod
    def get() -> Manager:
        """
                        Get manager singleton.
        
                        Returns:
                            Manager: Reference to manager.
        """
    def fetch_latest_cssi_space_weather(self) -> ostk.core.filesystem.File:
        """
                        Fetch latest CSSI Space Weather file.
        
                        Returns:
                            File: Latest CSSI Space Weather file.
        """
    def get_ap_3_hour_solar_indices_at(self, instant: ostk.physics.time.Instant) -> list[ostk.core.type.Integer]:
        """
                        Get a list of 8 3-hourly Ap solar indices for the day containing instant.
        
                        Args:
                            instant (Instant): An instant.
        
                        Returns:
                            list[int]: list of 8 3-hourly Ap solar indices.
        """
    def get_ap_daily_index_at(self, instant: ostk.physics.time.Instant) -> ostk.core.type.Integer:
        """
                        Get daily Ap index for the day containing instant.
        
                        Args:
                            instant (Instant): An instant.
        
                        Returns:
                            Integer: Daily Ap index.
        """
    def get_cssi_space_weather_at(self, instant: ostk.physics.time.Instant) -> CSSISpaceWeather:
        """
                        Get CSSI Space Weather at instant.
        
                        Args:
                            instant (Instant): An instant.
        
                        Returns:
                            CSSISpaceWeather: CSSI Space Weather.
        """
    def get_cssi_space_weather_directory(self) -> ostk.core.filesystem.Directory:
        """
                        Get CSSI space weather directory.
        
                        Returns:
                            Directory: CSSI space weather directory.
        """
    def get_f107_solar_flux_81_day_avg_at(self, instant: ostk.physics.time.Instant) -> ostk.core.type.Real:
        """
                        Get the 81-day average value for F10.7 solar flux centered on instant.
        
                        Args:
                            instant (Instant): An instant.
        
                        Returns:
                            float: Centered 81-day average value for F10.7 solar flux.
        """
    def get_f107_solar_flux_at(self, instant: ostk.physics.time.Instant) -> ostk.core.type.Real:
        """
                        Get the daily value for F10.7 solar flux at instant.
        
                        Args:
                            instant (Instant): An instant.
        
                        Returns:
                            float: Daily value for F10.7 solar flux.
        """
    def get_kp_3_hour_solar_indices_at(self, instant: ostk.physics.time.Instant) -> list[ostk.core.type.Integer]:
        """
                        Get a list of 8 3-hourly Kp solar indices for the day containing instant.
        
                        Args:
                            instant (Instant): An instant.
        
                        Returns:
                            list[int]: list of 8 3-hourly Kp solar indices.
        """
    def get_loaded_cssi_space_weather(self) -> CSSISpaceWeather:
        """
                        Get currently loaded CSSI Space Weather file.
        
                        Returns:
                            CSSISpaceWeather: Currently loaded CSSI Space Weather file.
        """
    def load_cssi_space_weather(self, cssi_space_weather: CSSISpaceWeather) -> None:
        """
                        Load CSSI Space Weather.
        
                        Args:
                            cssi_space_weather (CSSISpaceWeather): A CSSI Space Weather.
        """
class NRLMSISE00:
    """
    
                NRLMSISE00 atmospheric model.
    
            
    """
    class InputDataType:
        """
        Members:
        
          ConstantFluxAndGeoMag : 
                        Use constant values for F10.7, F10.7a and Kp NRLMSISE00 input parameters.
                    
        
          CSSISpaceWeatherFile : 
                        Use historical and predicted values for F10.7, F10.7a and Kp NRLMSISE00 input parameters.
                    
        """
        CSSISpaceWeatherFile: typing.ClassVar[NRLMSISE00.InputDataType]  # value = <InputDataType.CSSISpaceWeatherFile: 1>
        ConstantFluxAndGeoMag: typing.ClassVar[NRLMSISE00.InputDataType]  # value = <InputDataType.ConstantFluxAndGeoMag: 0>
        __members__: typing.ClassVar[dict[str, NRLMSISE00.InputDataType]]  # value = {'ConstantFluxAndGeoMag': <InputDataType.ConstantFluxAndGeoMag: 0>, 'CSSISpaceWeatherFile': <InputDataType.CSSISpaceWeatherFile: 1>}
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
    def __init__(self, input_data_type: NRLMSISE00.InputDataType = ..., f107_constant_value: ostk.core.type.Real = 150.0, f107_average_constant_value: ostk.core.type.Real = 150.0, kp_constant_value: ostk.core.type.Real = 3.0, earth_frame: ostk.physics.coordinate.Frame = ..., earth_radius: ostk.physics.unit.Length = ..., earth_flattening: ostk.core.type.Real = ..., sun_celestial: ostk.physics.environment.object.Celestial = None) -> None:
        """
                        Constructor.
        
                        Args:
                            input_data_type (NRLMSISE00.InputDataType): Input data source type.
                            f107_constant_value (float): F10.7 constant value.
                            f107_average_constant_value (float): F10.7a constant value.
                            kp_constant_value (float): Kp constant value.
                            earth_frame (Frame): Earth frame.
                            earth_radius (Length): Earth radius [m].
                            earth_flattening (float): Earth flattening.
                            sun_celestial (Celestial): Sun celestial object. Defaults to None.
        """
    def get_density_at(self, lla: ostk.physics.coordinate.spherical.LLA, instant: ostk.physics.time.Instant) -> ostk.core.type.Real:
        """
                        Get the atmospheric density value at a given position and instant.
        
                        Args:
                            lla (LLA): A position, expressed as latitude, longitude, altitude [deg, deg, m].
                            instant (Instant): An instant.
        
                        Returns:
                            float: Atmospheric density value [kg.m^-3].
        """
    def get_input_data_type(self) -> NRLMSISE00.InputDataType:
        """
                        Get the input data source type used to construct the NRLMSISE00 atmospheric model.
        
                        Returns:
                            NRLMSISE00 input data source type.
        """
    def is_defined(self) -> bool:
        """
                        Check if the NRLMSISE00 atmospheric model is defined.
        
                        Returns:
                            bool: True if defined.
        """
