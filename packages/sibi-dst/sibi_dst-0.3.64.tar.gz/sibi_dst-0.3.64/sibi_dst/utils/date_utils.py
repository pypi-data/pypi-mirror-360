import datetime
from typing import Union, Tuple, Callable, Dict, Optional

import fsspec
import numpy as np
import pandas as pd

from .log_utils import Logger


class DateUtils:
    """
    Utility class for date-related operations.

    The DateUtils class provides a variety of operations to manipulate and retrieve
    information about dates, such as calculating week ranges, determining start or
    end dates for specific periods (quarters, months, years), and dynamically
    registering custom time period functions. It also supports parsing specific
    periods for date range computations and ensuring the input date is correctly
    converted to the desired format.

    :ivar logger: Logger instance used for logging messages. Defaults to the logger
                  for the current class if not provided.
    :type logger: Logger

    :ivar _PERIOD_FUNCTIONS: Stores dynamically registered period functions that
                             return start and end dates.
    :type _PERIOD_FUNCTIONS: Dict[str, Callable[[], Tuple[datetime.date, datetime.date]]]
    """
    _PERIOD_FUNCTIONS: Dict[str, Callable[[], Tuple[datetime.date, datetime.date]]] = {}

    def __init__(self, logger=None):
        self.logger = logger or Logger.default_logger(logger_name=self.__class__.__name__)

    @classmethod
    def _ensure_date(cls, value: Union[str, datetime.date, datetime.datetime, pd.Timestamp]) -> datetime.date:
        """
        Ensure the input is converted to a datetime.date object.
        """
        if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
            return value
        elif isinstance(value, datetime.datetime):
            return value.date()
        elif isinstance(value, pd.Timestamp):
            return value.to_pydatetime().date()
        elif isinstance(value, str):
            for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
                try:
                    return datetime.datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
        raise ValueError(f"Unsupported date format: {value}")

    # Public alias to access _ensure_date from other classes
    ensure_date = _ensure_date

    @classmethod
    def calc_week_range(cls, reference_date: Union[str, datetime.date, datetime.datetime, pd.Timestamp]) -> Tuple[
        datetime.date, datetime.date]:
        """
        Calculate the start and end of the week for a given reference date.
        """
        reference_date = cls._ensure_date(reference_date)
        start = reference_date - datetime.timedelta(days=reference_date.weekday())
        end = start + datetime.timedelta(days=6)
        return start, end

    @staticmethod
    def get_year_timerange(year: int) -> Tuple[datetime.date, datetime.date]:
        """
        Get the start and end dates for a given year.
        """
        return datetime.date(year, 1, 1), datetime.date(year, 12, 31)

    @classmethod
    def get_first_day_of_the_quarter(cls, reference_date: Union[
        str, datetime.date, datetime.datetime, pd.Timestamp]) -> datetime.date:
        """
        Get the first day of the quarter for a given date.
        """
        reference_date = cls._ensure_date(reference_date)
        quarter = (reference_date.month - 1) // 3 + 1
        return datetime.date(reference_date.year, 3 * quarter - 2, 1)

    @classmethod
    def get_last_day_of_the_quarter(cls, reference_date: Union[
        str, datetime.date, datetime.datetime, pd.Timestamp]) -> datetime.date:
        """
        Get the last day of the quarter for a given date.
        """
        reference_date = cls._ensure_date(reference_date)
        quarter = (reference_date.month - 1) // 3 + 1
        first_day_of_next_quarter = datetime.date(reference_date.year, 3 * quarter + 1, 1)
        return first_day_of_next_quarter - datetime.timedelta(days=1)

    @classmethod
    def get_month_range(cls, n: int = 0) -> Tuple[datetime.date, datetime.date]:
        """
        Get the date range for the current month or the month `n` months in the past or future.
        """
        today = datetime.date.today()
        target_month = (today.month - 1 + n) % 12 + 1
        target_year = today.year + (today.month - 1 + n) // 12
        start = datetime.date(target_year, target_month, 1)
        if n == 0:
            return start, today
        next_month = (target_month % 12) + 1
        next_year = target_year + (target_month == 12)
        end = datetime.date(next_year, next_month, 1) - datetime.timedelta(days=1)
        return start, end

    @classmethod
    def register_period(cls, name: str, func: Callable[[], Tuple[datetime.date, datetime.date]]):
        """
        Dynamically register a new period function.
        """
        cls._PERIOD_FUNCTIONS[name] = func

    @classmethod
    def parse_period(cls, **kwargs) -> Tuple[datetime.date, datetime.date]:
        """
        Parse the period keyword to determine the start and end date for date range operations.
        """
        period = kwargs.setdefault('period', 'today')
        period_functions = cls._get_default_periods()
        period_functions.update(cls._PERIOD_FUNCTIONS)
        if period not in period_functions:
            raise ValueError(f"Unknown period '{period}'. Available periods: {list(period_functions.keys())}")
        return period_functions[period]()

    @classmethod
    def _get_default_periods(cls) -> Dict[str, Callable[[], Tuple[datetime.date, datetime.date]]]:
        """
        Get default period functions.
        """
        today = datetime.date.today
        return {
            'today': lambda: (today(), today()),
            'yesterday': lambda: (today() - datetime.timedelta(days=1), today() - datetime.timedelta(days=1)),
            'current_week': lambda: cls.calc_week_range(today()),
            'last_week': lambda: cls.calc_week_range(today() - datetime.timedelta(days=7)),
            'current_month': lambda: cls.get_month_range(n=0),
            'last_month': lambda: cls.get_month_range(n=-1),
            'current_year': lambda: cls.get_year_timerange(today().year),
            'current_quarter': lambda: (
                cls.get_first_day_of_the_quarter(today()), cls.get_last_day_of_the_quarter(today())),
            'ytd': lambda: (datetime.date(today().year, 1, 1), today()),
        }


class FileAgeChecker:
    def __init__(self, debug=False, logger=None):
        self.logger = logger or Logger.default_logger(logger_name=self.__class__.__name__)
        self.logger.set_level(Logger.DEBUG if debug else Logger.INFO)
    def is_file_older_than(
            self,
            file_path: str,
            max_age_minutes: int,
            fs: Optional[fsspec.AbstractFileSystem] = None,
            ignore_missing: bool = False,
            verbose: bool = False,
    ) -> bool:
        """
        Check if a file or directory is older than the specified max_age_minutes.

        :param file_path: Path to the file or directory.
        :param max_age_minutes: Maximum allowed age in minutes.
        :param fs: Filesystem object. Defaults to local filesystem.
        :param ignore_missing: Treat missing paths as not old if True.
        :param verbose: Enable detailed logging.
        :return: True if older than max_age_minutes, False otherwise.
        """
        fs = fs or fsspec.filesystem("file")
        self.logger.debug(f"Checking age for {file_path}...")

        try:
            if not fs.exists(file_path):
                self.logger.debug(f"Path not found: {file_path}.")
                return not ignore_missing

            if fs.isdir(file_path):
                self.logger.debug(f"Found directory: {file_path}")
                age = self._get_directory_age_minutes(file_path, fs, verbose)
            elif fs.isfile(file_path):
                age = self._get_file_age_minutes(file_path, fs, verbose)
            else:
                self.logger.warning(f"Path {file_path} is neither file nor directory.")
                return True

            return age > max_age_minutes

        except Exception as e:
            self.logger.warning(f"Error checking {file_path}: {str(e)}")
            return True

    def get_file_or_dir_age_minutes(
            self,
            file_path: str,
            fs: Optional[fsspec.AbstractFileSystem] = None,
    ) -> float:
        """
        Get age of file/directory in minutes. Returns infinity for errors/missing paths.

        :param file_path: Path to check.
        :param fs: Filesystem object. Defaults to local filesystem.
        :return: Age in minutes or infinity if unavailable.
        """
        fs = fs or fsspec.filesystem("file")
        try:
            if not fs.exists(file_path):
                self.logger.debug(f"Path not found: {file_path}")
                return float("inf")

            if fs.isdir(file_path):
                return self._get_directory_age_minutes(file_path, fs, verbose=False)
            if fs.isfile(file_path):
                return self._get_file_age_minutes(file_path, fs, verbose=False)

            self.logger.warning(f"Invalid path type: {file_path}")
            return float("inf")

        except Exception as e:
            self.logger.warning(f"Error getting age for {file_path}: {str(e)}")
            return float("inf")

    def _get_directory_age_minutes(
            self,
            dir_path: str,
            fs: fsspec.AbstractFileSystem,
            verbose: bool,
    ) -> float:
        """Calculate age of oldest file in directory."""
        try:
            all_files = fs.ls(dir_path)
        except Exception as e:
            self.logger.warning(f"Error listing {dir_path}: {str(e)}")
            return float("inf")

        if not all_files:
            self.logger.debug(f"Empty directory: {dir_path}")
            return float("inf")

        modification_times = []
        for file in all_files:
            try:
                info = fs.info(file)
                mod_time = self._get_modification_time(info, file)
                modification_times.append(mod_time)
            except Exception as e:
                self.logger.warning(f"Skipping {file}: {str(e)}")

        if not modification_times:
            self.logger.warning(f"No valid files in {dir_path}")
            return float("inf")

        oldest = min(modification_times)
        age = (datetime.datetime.now(datetime.timezone.utc) - oldest).total_seconds() / 60
        self.logger.debug(f"Oldest in {dir_path}: {age:.2f} minutes")

        return age

    def _get_file_age_minutes(
            self,
            file_path: str,
            fs: fsspec.AbstractFileSystem,
            verbose: bool,
    ) -> float:
        """Calculate file age in minutes."""
        try:
            info = fs.info(file_path)
            mod_time = self._get_modification_time(info, file_path)
            age = (datetime.datetime.now(datetime.timezone.utc) - mod_time).total_seconds() / 60

            if verbose:
                self.logger.debug(f"{file_path} info: {info}")
                self.logger.debug(f"File age: {age:.2f} minutes")

            return age

        except Exception as e:
            self.logger.warning(f"Error processing {file_path}: {str(e)}")
            return float("inf")

    def _get_modification_time(self, info: Dict, file_path: str) -> datetime.datetime:
        """Extract modification time from filesystem info with timezone awareness."""
        try:
            if "LastModified" in info:  # S3-like
                lm = info["LastModified"]
                return lm if isinstance(lm, datetime.datetime) else datetime.datetime.fromisoformat(
                    lm[:-1]).astimezone()

            if "mtime" in info:  # Local filesystem
                return datetime.datetime.fromtimestamp(info["mtime"], tz=datetime.timezone.utc)

            if "modified" in info:  # FTP/SSH
                return datetime.datetime.strptime(
                    info["modified"], "%Y-%m-%d %H:%M:%S"
                ).replace(tzinfo=datetime.timezone.utc)

            raise KeyError("No valid modification time key found")

        except (KeyError, ValueError) as e:
            self.logger.warning(f"Invalid mod time for {file_path}: {str(e)}")
            raise ValueError(f"Unsupported modification time format for {file_path}") from e


class BusinessDays:
    """
    Provides functionality for handling business days calculations with a custom
    holiday list. The class includes methods for calculating the number of
    business days, modifying dates by adding business days, and applying these
    operations to Dask DataFrames.

    :ivar logger: Logger instance for logging error, warning, and debug messages.
    :type logger: logging.Logger
    :ivar HOLIDAY_LIST: Dictionary mapping years to lists of holiday dates.
    :type HOLIDAY_LIST: dict
    :ivar bd_cal: Numpy busdaycalendar object containing holidays and week mask.
    :type bd_cal: numpy.busdaycalendar
    :ivar holidays: Array of holiday dates used by the business day calendar.
    :type holidays: numpy.ndarray
    :ivar week_mask: Boolean array indicating working days within a week.
    :type week_mask: numpy.ndarray
    """

    def __init__(self, holiday_list, logger):
        """
        Initialize a BusinessDays object with a given holiday list.
        """
        self.logger = logger
        self.HOLIDAY_LIST = holiday_list
        bd_holidays = [day for year in self.HOLIDAY_LIST for day in self.HOLIDAY_LIST[year]]
        self.bd_cal = np.busdaycalendar(holidays=bd_holidays, weekmask="1111100")
        self.holidays = self.bd_cal.holidays
        self.week_mask = self.bd_cal.weekmask

    def get_business_days_count(self, begin_date, end_date):
        """
        Calculate the number of business days between two dates.
        """
        try:
            begin_date = pd.to_datetime(begin_date)
            end_date = pd.to_datetime(end_date)
        except Exception as e:
            raise ValueError(f"Invalid date format: {e}")

        years = [str(year) for year in range(begin_date.year, end_date.year + 1)]
        if not all(year in self.HOLIDAY_LIST for year in years):
            raise ValueError("Not all years in date range are in the holiday list")

        return np.busday_count(
            begin_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
            busdaycal=self.bd_cal,
        )

    def calc_business_days_from_df(self, df, begin_date_col, end_date_col, result_col="business_days"):
        """
        Add a column to a Dask DataFrame with the number of business days between two date columns.
        """
        if not all(col in df.columns for col in [begin_date_col, end_date_col]):
            self.logger.error("Column names not found in DataFrame")
            raise ValueError("Required columns are missing")

        # Extract holidays and weekmask to recreate the busdaycalendar
        holidays = self.bd_cal.holidays
        weekmask = self.bd_cal.weekmask

        # Define a function to calculate business days
        def calculate_business_days(row, holidays, weekmask):
            begin_date = pd.to_datetime(row[begin_date_col])
            end_date = pd.to_datetime(row[end_date_col])
            if pd.isna(begin_date) or pd.isna(end_date):
                return np.nan
            busdaycal = np.busdaycalendar(holidays=holidays, weekmask=weekmask)
            return np.busday_count(
                begin_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
                busdaycal=busdaycal,
            )

        # Define a wrapper function for partition-wise operations
        def apply_business_days(partition, holidays, weekmask):
            return partition.apply(
                calculate_business_days, axis=1, holidays=holidays, weekmask=weekmask
            )

        # Apply the function using map_partitions
        df[result_col] = df.map_partitions(
            apply_business_days,
            holidays,
            weekmask,
            meta=(result_col, "int64"),
        )

        return df

    def add_business_days(self, start_date, n_days):
        """
        Add n_days business days to start_date.
        """
        try:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date should be a string in the format YYYY-MM-DD")

        if str(start_date.year) not in self.HOLIDAY_LIST:
            self.logger.warning(f"Year {start_date.year} is not in the holiday list")

        return np.busday_offset(
            start_date.strftime("%Y-%m-%d"),
            n_days,
            roll="forward",
            busdaycal=self.bd_cal,
        )

    def calc_sla_end_date(self, df, start_date_col, n_days_col, result_col="sla_end_date"):
        """
        Add a column to a Dask DataFrame with SLA end dates based on start date and SLA days.
        """
        if not all(col in df.columns for col in [start_date_col, n_days_col]):
            raise ValueError("Column names not found in DataFrame")

        # Extract holidays and weekmask to recreate the busdaycalendar
        holidays = self.bd_cal.holidays
        weekmask = self.bd_cal.weekmask

        # Define a function to calculate SLA end dates
        def calculate_sla_end_date(row, holidays, weekmask):
            start_date = pd.to_datetime(row[start_date_col])
            n_days = row[n_days_col]
            busdaycal = np.busdaycalendar(holidays=holidays, weekmask=weekmask)
            return np.busday_offset(
                start_date.strftime("%Y-%m-%d"),
                n_days,
                roll="forward",
                busdaycal=busdaycal,
            )

        # Define a wrapper for partition-wise operation
        def apply_sla_end_date(partition, holidays, weekmask):
            return partition.apply(
                calculate_sla_end_date, axis=1, holidays=holidays, weekmask=weekmask
            )

        # Apply the function using map_partitions
        df[result_col] = df.map_partitions(
            apply_sla_end_date,
            holidays,
            weekmask,
            meta=(result_col, "object"),
        )

        return df
# Class enhancements
# DateUtils.register_period('next_week', lambda: (datetime.date.today() + datetime.timedelta(days=7),
#                                                 datetime.date.today() + datetime.timedelta(days=13)))
# start, end = DateUtils.parse_period(period='next_week')
# print(f"Next Week: {start} to {end}")
