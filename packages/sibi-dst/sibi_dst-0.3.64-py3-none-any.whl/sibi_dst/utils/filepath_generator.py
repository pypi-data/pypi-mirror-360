import datetime
import re

import fsspec

from .log_utils import Logger


class FilePathGenerator:
    """
    Dynamically generates file paths by scanning directories starting from the base path
    and determining the innermost directory structure.

    Now supports generating appropriate paths for both pandas and Dask.
    """

    def __init__(self, base_path='', fs=None, logger=None, **kwargs):
        """
        Initialize the FilePathGenerator.

        Parameters:
            base_path (str): Base directory path where data files are stored.
            fs (fsspec.AbstractFileSystem, optional): Filesystem object to use for file operations.
            logger (Logger, optional): Logger instance for logging information.
            **kwargs: Additional keyword arguments.
                - debug (bool): If True, enables debug logging.
                - storage_options (dict): Options for the filesystem (e.g., credentials, tokens).
                - exclude_patterns (list): List of regex patterns to exclude from file paths.
                - file_extension (str): File extension to look for (default: 'parquet').
        """
        self.base_path = base_path.rstrip('/')
        self.fs = fs  # Filesystem object
        self.logger = logger or Logger.default_logger(logger_name=self.__class__.__name__)
        self.debug = kwargs.get('debug', False)
        self.storage_options = kwargs.get('storage_options', {})
        self.exclude_patterns = kwargs.get('exclude_patterns', [])
        self.file_extension = kwargs.get('file_extension', 'parquet').lstrip('.')

        # If fs is not provided, initialize it based on base_path and storage_options
        if self.fs is None:
            self.fs, _ = fsspec.core.url_to_fs(self.base_path, **self.storage_options)

    def generate_file_paths(self, start_date, end_date, engine='dask'):
        """
        Generate paths dynamically for files within the date range by scanning directories.
        Returns a list of file paths compatible with the specified engine.

        Parameters:
            start_date (str or datetime): Start date in 'YYYY-MM-DD' format or datetime object.
            end_date (str or datetime): End date in 'YYYY-MM-DD' format or datetime object.
            engine (str): 'pandas' or 'dask' to specify which library the paths are intended for.

        Returns:
            list: List of file paths.
        """
        start_date = self._convert_to_datetime(start_date)
        end_date = self._convert_to_datetime(end_date)

        paths = []
        curr_date = start_date

        while curr_date <= end_date:
            year, month, day = curr_date.year, curr_date.month, curr_date.day
            day_paths = self._collect_paths(year, month, day, engine)
            if day_paths:
                paths.extend(day_paths)
            curr_date += datetime.timedelta(days=1)

        return paths

    def _collect_paths(self, year, month, day, engine):
        """
        Collect appropriate paths for a given date, depending on the engine.

        Parameters:
            year (int): Year component of the date.
            month (int): Month component of the date.
            day (int): Day component of the date.
            engine (str): 'pandas' or 'dask'.

        Returns:
            list: List of file or directory paths.
        """
        base_dir = f"{self.base_path}/{year}/{str(month).zfill(2)}/{str(day).zfill(2)}"

        if not self.fs.exists(base_dir):
            if self.debug:
                self.logger.debug(f"Directory does not exist: {base_dir}")
            return []

        if engine == 'dask':
            # Collect individual file paths
            file_pattern = f"{base_dir}/**/*.{self.file_extension}"
            all_paths = self.fs.glob(file_pattern)

            if not all_paths and self.debug:
                self.logger.debug(f"No files found with pattern: {file_pattern}")

            # Exclude unwanted files and directories
            filtered_paths = self._exclude_unwanted_paths(all_paths)

            # Filter out directories
            file_paths = [path for path in filtered_paths if not self.fs.isdir(path)]

        elif engine == 'pandas':
            # Collect dataset directories
            # Assume that the base_dir is a Parquet dataset
            if self.fs.isdir(base_dir):
                file_paths = [base_dir]
            else:
                file_paths = []

        else:
            raise ValueError("Engine must be 'pandas' or 'dask'.")

        protocol = self.fs.protocol if isinstance(self.fs.protocol, str) else self.fs.protocol[0]

        # Ensure the protocol is included in the paths
        file_paths = [
            f"{protocol}://{path}" if not path.startswith(f"{protocol}://") else path
            for path in file_paths
        ]

        if self.debug:
            self.logger.debug(f"Collected {len(file_paths)} paths from {base_dir} for engine '{engine}'")

        return file_paths

    def _exclude_unwanted_paths(self, paths):
        """
        Exclude paths that match any of the exclusion patterns.
        """
        # Combine default patterns with user-provided patterns
        exclude_patterns = self.exclude_patterns

        # Compile regex patterns for efficiency
        compiled_patterns = [re.compile(pattern) for pattern in exclude_patterns]

        # Filter out paths matching any of the exclude patterns
        filtered_paths = [
            path for path in paths
            if not any(pattern.match(path) for pattern in compiled_patterns)
        ]

        return filtered_paths

    @staticmethod
    def _convert_to_datetime(date):
        """Convert a date string or datetime object into a datetime object."""
        if isinstance(date, str):
            return datetime.datetime.strptime(date, '%Y-%m-%d')
        return date


"""
Usage:
# Initialize the generator
generator = FilePathGenerator(
    base_path='/Users/lvalverdeb/TeamDev/sibi-dst/IbisDataWH/logistics_storage/products/tracking',
    debug=True
)

# Generate dataset paths for Dask
dataset_paths = generator.generate_file_paths('2024-01-01', '2024-01-05', engine='dask')

# Read data with Dask
import dask.dataframe as dd

df = dd.read_parquet(dataset_paths)

# Now you can use df as a Dask DataFrame
print(df.head())

# Generate file paths for pandas
file_paths = generator.generate_file_paths('2024-01-01', '2024-01-05', engine='pandas')

# Read data with pandas
import pandas as pd

dataframes = []
for fp in file_paths:
    df = pd.read_parquet(fp)
    dataframes.append(df)

df_pandas = pd.concat(dataframes, ignore_index=True)
print(df_pandas.head())
"""
