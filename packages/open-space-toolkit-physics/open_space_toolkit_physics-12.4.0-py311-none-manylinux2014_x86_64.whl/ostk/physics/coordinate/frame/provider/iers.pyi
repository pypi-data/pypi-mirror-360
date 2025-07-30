from __future__ import annotations
import numpy
import ostk.core.filesystem
import ostk.core.type
import ostk.physics
import ostk.physics.time
__all__ = ['BulletinA', 'Finals2000A', 'Manager']
class BulletinA:
    """
    
                Contains rapid determinations for Earth orientation parameters:
                x/y pole, UT1-UTC and their errors at daily intervals and predictions for 1 year into
                the future.
    
                The contents of IERS Bulletin A are divided into four sections:
    
                1. General information including key definitions and the most recently adopted values of
                DUT1 and TAI-UTC.
    
                2. Quick-look daily estimates of the EOPs determined by smoothing the observed data.
                This involves the application of systematic corrections and statistical weighting.
                The results are published with a delay of about one to three days between the date of
                publication and the last available date with estimated EOP.
    
                3. Predictions of x, y, and UT1-UTC, up to 365 days following the last day of data.
                The predictions use similar algorithms based on seasonal filtering and autoregressive
                processing for x, y, and UT1.
    
                4. The combination series for the celestial pole offsets.
                Bulletin A contains celestial pole offsets with respect to the IAU1980 Nutation theory
                (dpsi and deps) and the IAU 2000 Resolutions (dX and dY), beginning on 1 January 2003.
    
                :reference: https://datacenter.iers.org/productMetadata.php?id=6
            
            
    """
    class Observation:
        @property
        def day(self) -> ostk.core.type.Integer:
            """
                            Day of month.
            """
        @property
        def mjd(self) -> ostk.core.type.Real:
            """
                            Modified Julian Day.
            """
        @property
        def month(self) -> ostk.core.type.Integer:
            """
                            Month number.
            """
        @property
        def ut1_minus_utc(self) -> ostk.core.type.Real:
            """
                            UT1-UTC [s].
            """
        @property
        def ut1_minus_utc_error(self) -> ostk.core.type.Real:
            """
                            UT1-UTC error [s].
            """
        @property
        def x(self) -> ostk.core.type.Real:
            """
                            PM-x [asec].
            """
        @property
        def x_error(self) -> ostk.core.type.Real:
            """
                            PM-x error [asec].
            """
        @property
        def y(self) -> ostk.core.type.Real:
            """
                            PM-y [asec].
            """
        @property
        def y_error(self) -> ostk.core.type.Real:
            """
                            PM-y error [asec].
            """
        @property
        def year(self) -> ostk.core.type.Integer:
            """
                            Year (to get true calendar year, add 1900 for MJD <= 51543 or add 2000 for MJD >= 51544).
            """
    class Prediction:
        @property
        def day(self) -> ostk.core.type.Integer:
            """
                            Day of month.
            """
        @property
        def mjd(self) -> ostk.core.type.Real:
            """
                            Modified Julian Day.
            """
        @property
        def month(self) -> ostk.core.type.Integer:
            """
                            Month number.
            """
        @property
        def ut1_minus_utc(self) -> ostk.core.type.Real:
            """
                            UT1-UTC [s].
            """
        @property
        def x(self) -> ostk.core.type.Real:
            """
                            PM-x [asec].
            """
        @property
        def y(self) -> ostk.core.type.Real:
            """
                            PM-y [asec].
            """
        @property
        def year(self) -> ostk.core.type.Integer:
            """
                            Year (to get true calendar year, add 1900 for MJD <= 51543 or add 2000 for MJD >= 51544).
            """
    @staticmethod
    def load(file: ostk.core.filesystem.File) -> BulletinA:
        """
                        Load Bulletin A from a file.
        
                        Parameters:
                            file (File): The file.
        
                        Returns:
                            BulletinA: The Bulletin A object.
        """
    @staticmethod
    def undefined() -> BulletinA:
        """
                        Undefined factory function.
        
                        Returns:
                            BulletinA: An undefined Bulletin A object.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def access_observation_interval(self) -> ostk.physics.time.Interval:
        """
                        Access the observation interval.
        
                        Returns:
                            Interval: The observation Interval of Instants.
        """
    def access_prediction_interval(self) -> ostk.physics.time.Interval:
        """
                        Access the prediction interval.
        
                        Returns:
                            Interval: The prediction Interval of Instants.
        """
    def access_release_date(self) -> ostk.physics.time.Date:
        """
                        Access the release date.
        
                        Returns:
                            Date: The release date.
        """
    def access_tai_minus_utc(self) -> ostk.physics.time.Duration:
        """
                        Access the TAI-UTC.
        
                        Returns:
                            Duration: The TAI-UTC.
        """
    def access_tai_minus_utc_epoch(self) -> ostk.physics.time.Instant:
        """
                        Access the TAI-UTC epoch.
        
                        Returns:
                            Instant: The TAI-UTC epoch.
        """
    def get_observation_at(self, instant: ostk.physics.time.Instant) -> ...:
        """
                        Get observation at a given instant.
        
                        Parameters:
                            instant (Instant): The instant.
        
                        Returns:
                            Observation: The observation.
        """
    def get_observation_interval(self) -> ostk.physics.time.Interval:
        """
                        Get observation interval.
        
                        Returns:
                            Interval: Observation Interval of Instants.
        """
    def get_prediction_at(self, instant: ostk.physics.time.Instant) -> ...:
        """
                        Get prediction at a given instant.
        
                        Parameters:
                            instant (Instant): The instant.
        
                        Returns:
                            Prediction: The prediction.
        """
    def get_prediction_interval(self) -> ostk.physics.time.Interval:
        """
                        Get prediction interval.
        
                        Returns:
                            Interval: Prediction Interval of Instants.
        """
    def get_release_date(self) -> ostk.physics.time.Date:
        """
                        Get release Date of Bulletin A.
        
                        Returns:
                            Date: Release Date of Bulletin A.
        """
    def get_tai_minus_utc(self) -> ostk.physics.time.Duration:
        """
                        Get TAI-UTC.
        
                        Returns:
                            Duration: TAI-UTC.
        """
    def get_tai_minus_utc_epoch(self) -> ostk.physics.time.Instant:
        """
                        Get TAI-UTC epoch.
        
                        Returns:
                            Instant: TAI-UTC epoch.
        """
    def is_defined(self) -> bool:
        """
                        Returns true if the bulletin is defined.
        
                        Returns:
                            bool: True if the bulletin is defined.
        """
class Finals2000A:
    """
    
                Standard Rapid EOP Data since 01. January 1992 (IAU2000)
    
                This file (updated weekly) is the complete Earth orientation data set, since 1 January
                1992 with 1 year of predictions. The nutation series in dX and dY uses the IAU 2000A
                Nutation Theory.
    
                :reference: https://www.iers.org/IERS/EN/DataProducts/EarthOrientationData/eop.html -> finals.data
    
            
    """
    class Data:
        @property
        def day(self) -> ostk.core.type.Integer:
            """
                            Day of month.
            """
        @property
        def dx_a(self) -> ostk.core.type.Real:
            """
                            Bulletin A dX wrt IAU2000A Nutation, Free Core Nutation NOT Removed [amsec].
            """
        @property
        def dx_b(self) -> ostk.core.type.Real:
            """
                            Bulletin B dX wrt IAU2000A Nutation [amsec].
            """
        @property
        def dx_error_a(self) -> ostk.core.type.Real:
            """
                            Error in dX [amsec].
            """
        @property
        def dy_a(self) -> ostk.core.type.Real:
            """
                            Bulletin A dY wrt IAU2000A Nutation, Free Core Nutation NOT Removed [amsec].
            """
        @property
        def dy_b(self) -> ostk.core.type.Real:
            """
                            Bulletin B dY wrt IAU2000A Nutation [amsec].
            """
        @property
        def dy_error_a(self) -> ostk.core.type.Real:
            """
                            Error in dY [amsec].
            """
        @property
        def lod_a(self) -> ostk.core.type.Real:
            """
                            Bulletin A LOD (not always filled) [ms].
            """
        @property
        def lod_error_a(self) -> ostk.core.type.Real:
            """
                            Error in LOD (not always filled) [ms].
            """
        @property
        def mjd(self) -> ostk.core.type.Real:
            """
                            Modified Julian Date.
            """
        @property
        def month(self) -> ostk.core.type.Integer:
            """
                            Month number.
            """
        @property
        def nutation_flag(self) -> str:
            """
                            IERS (I) or Prediction (P) flag for Bulletin A nutation values.
            """
        @property
        def polar_motionflag(self) -> str:
            """
                            IERS (I) or Prediction (P) flag for Bulletin A polar motion values.
            """
        @property
        def ut1_minus_utc_a(self) -> ostk.core.type.Real:
            """
                            Bulletin A UT1-UTC [s].
            """
        @property
        def ut1_minus_utc_b(self) -> ostk.core.type.Real:
            """
                            Bulletin B UT1-UTC [s].
            """
        @property
        def ut1_minus_utc_error_a(self) -> ostk.core.type.Real:
            """
                            Error in UT1-UTC [s].
            """
        @property
        def ut1_minus_utc_flag(self) -> str:
            """
                            IERS (I) or Prediction (P) flag for Bulletin A UT1-UTC values.
            """
        @property
        def x_a(self) -> ostk.core.type.Real:
            """
                            Bulletin A PM-x [asec].
            """
        @property
        def x_b(self) -> ostk.core.type.Real:
            """
                            Bulletin B PM-x [asec].
            """
        @property
        def x_error_a(self) -> ostk.core.type.Real:
            """
                            Error in PM-x [asec].
            """
        @property
        def y_a(self) -> ostk.core.type.Real:
            """
                            Bulletin A PM-y [asec].
            """
        @property
        def y_b(self) -> ostk.core.type.Real:
            """
                            Bulletin B PM-y [asec].
            """
        @property
        def y_error_a(self) -> ostk.core.type.Real:
            """
                            Error in PM-y [asec].
            """
        @property
        def year(self) -> ostk.core.type.Integer:
            """
                            Year (to get true calendar year, add 1900 for MJD <= 51543 or add 2000 for MJD >= 51544).
            """
    @staticmethod
    def load(file: ostk.core.filesystem.File) -> Finals2000A:
        """
                        Load data from file.
        
                        Args:
                            file (str): File.
        
                        Returns:
                            Finals2000A: Finals2000A object.
        """
    @staticmethod
    def undefined() -> Finals2000A:
        """
                        Undefined factory function.
        
                        Returns:
                            Finals2000A: Undefined Finals2000A object.
        """
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def get_data_at(self, instant: ostk.physics.time.Instant) -> ...:
        """
                        Get data at instant.
        
                        Args:
                            instant (Instant): Instant.
        
                        Returns:
                            Finals2000.Data: Data.
        """
    def get_interval(self) -> ostk.physics.time.Interval:
        """
                        Get data interval.
        
                        Returns:
                            Interval: Data Interval of Instants.
        """
    def get_lod_at(self, instant: ostk.physics.time.Instant) -> ostk.core.type.Real:
        """
                        Get LOD at instant.
        
                        Args:
                            instant (Instant): Instant.
        
                        Returns:
                            float: LOD.
        """
    def get_polar_motion_at(self, instant: ostk.physics.time.Instant) -> numpy.ndarray[numpy.float64[2, 1]]:
        """
                        Get polar motion at instant.
        
                        Args:
                            instant (Instant): Instant.
        
                        Returns:
                            np.ndarray: Polar motion.
        """
    def get_ut1_minus_utc_at(self, instant: ostk.physics.time.Instant) -> ostk.core.type.Real:
        """
                        Get UT1-UTC at instant.
        
                        Args:
                            instant (Instant): Instant.
        
                        Returns:
                            float: UT1-UTC.
        """
    def is_defined(self) -> bool:
        """
                        Returns true if defined.
        
                        Returns:
                            bool: True if defined.
        """
class Manager(ostk.physics.Manager):
    """
    
                IERS bulletins manager (thread-safe)
    
                The following environment variables can be defined:
    
                - "OSTK_PHYSICS_COORDINATE_FRAME_PROVIDER_IERS_MANAGER_MODE" will override
                "DefaultMode"
                - "OSTK_PHYSICS_COORDINATE_FRAME_PROVIDER_IERS_MANAGER_LOCAL_REPOSITORY" will override
                "DefaultLocalRepository"
                - "OSTK_PHYSICS_COORDINATE_FRAME_PROVIDER_IERS_MANAGER_LOCAL_REPOSITORY_LOCK_TIMEOUT"
                will override "DefaultLocalRepositoryLockTimeout"
    
                :reference: https://www.iers.org/IERS/EN/DataProducts/EarthOrientationData/eop.html
    
            
    """
    @staticmethod
    def get() -> Manager:
        """
                        Get manager singleton.
        
                        Returns:
                            Manager: Reference to manager.
        """
    def fetch_latest_bulletin_a(self) -> ostk.core.filesystem.File:
        """
                        Fetch latest Bulletin A file.
        
                        Returns:
                            File: Latest Bulletin A file.
        """
    def fetch_latest_finals_2000a(self) -> ostk.core.filesystem.File:
        """
                        Fetch latest Finals 2000A file.
        
                        Returns:
                            File: Latest Finals 2000A file.
        """
    def get_bulletin_a(self) -> ...:
        """
                        Get Bulletin A.
        
                        Returns:
                            BulletinA: Bulletin A.
        """
    def get_bulletin_a_directory(self) -> ostk.core.filesystem.Directory:
        """
                        Get Bulletin A directory.
        
                        Returns:
                            Directory: Bulletin A directory.
        """
    def get_finals_2000a(self) -> ...:
        """
                        Get Finals 2000A.
        
                        Returns:
                            Finals2000A: Finals 2000A.
        """
    def get_finals_2000a_directory(self) -> ostk.core.filesystem.Directory:
        """
                        Get Finals 2000A directory.
        
                        Returns:
                            Directory: Finals 2000A directory.
        """
    def get_lod_at(self, instant: ostk.physics.time.Instant) -> ostk.core.type.Real:
        """
                        Get length of day at instant.
        
                        Args:
                            instant (Instant): Instant.
        
                        Returns:
                            float: Length of day [ms].
        """
    def get_polar_motion_at(self, instant: ostk.physics.time.Instant) -> numpy.ndarray[numpy.float64[2, 1]]:
        """
                        Get polar motion at instant.
        
                        Args:
                            instant (Instant): Instant.
        
                        Returns:
                            np.ndarray: Polar motion.
        """
    def get_ut1_minus_utc_at(self, instant: ostk.physics.time.Instant) -> ostk.core.type.Real:
        """
                        Get UT1 - UTC at instant.
        
                        Args:
                            instant (Instant): Instant.
        
                        Returns:
                            float: UT1 - UTC [sec].
        """
    def load_bulletin_a(self, bulletin_a: typing.Any) -> None:
        """
                        Load Bulletin A.
        
                        Returns:
                            bulletin_a (BulletinA): Bulletin A.
        """
    def load_finals_2000a(self, finals_2000a: typing.Any) -> None:
        """
                        Load Finals 2000A.
        
                        Returns:
                            finals_2000a (Finals2000A): Finals 2000A.
        """
