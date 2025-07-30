import datetime
import logging
import threading
from typing import Optional, Any, Dict

import dask.dataframe as dd
import fsspec

from sibi_dst.df_helper import DfHelper
from sibi_dst.utils import DataWrapper, DateUtils, Logger, ParquetSaver, UpdatePlanner
from sibi_dst.utils import MissingManifestManager


class ParquetArtifact(DfHelper):
    """
    Class designed to manage Parquet data storage and retrieval using a specified
    DataWrapper class for data processing. It provides functionality for loading,
    updating, rebuilding, and generating Parquet files within a configurable
    storage filesystem. The class ensures that all essential configurations and
    filesystems are properly set up before operations.

    Detailed functionality includes support for dynamically managing and generating
    Parquet files based on time periods, with customizable options for paths,
    filenames, date fields, and more. It is an abstraction for efficiently handling
    storage tasks related to distributed or local file systems.

    :ivar config: Configuration dictionary containing all configurable parameters
                  for managing Parquet data storage, such as paths, filenames,
                  and date ranges.
    :type config: dict
    :ivar df: Cached Dask DataFrame used to store and manipulate data loaded
              from the Parquet file.
    :type df: Optional[dask.dataframe.DataFrame]
    :ivar data_wrapper_class: Class responsible for abstracting data processing
                              operations required for Parquet file generation.
    :type data_wrapper_class: type
    :ivar date_field: Name of the field used to identify and process data by date.
    :type date_field: Optional[str]
    :ivar parquet_storage_path: Filesystem path to store Parquet files.
    :type parquet_storage_path: Optional[str]
    :ivar parquet_filename: Name of the Parquet file to be generated and managed.
    :type parquet_filename: Optional[str]
    :ivar parquet_start_date: Date string specifying the start date for data range
                              processing.
    :type parquet_start_date: Optional[str]
    :ivar parquet_end_date: Date string specifying the end date for data range
                            processing.
    :type parquet_end_date: Optional[str]
    :ivar filesystem_type: Type of the filesystem used for managing storage
                           operations (e.g., `file`, `s3`, etc.).
    :type filesystem_type: str
    :ivar filesystem_options: Additional options for configuring the filesystem.
    :type filesystem_options: dict
    :ivar fs: Filesystem object used for storage operations.
    :type fs: fsspec.AbstractFileSystem
    """
    DEFAULT_CONFIG = {
        'backend': 'parquet'
    }

    # DEFAULT_UPDATE_PLANNER_CONFIG = {
    #     'reverse_order': True,
    #     'overwrite': False,
    #     'ignore_missing': True,
    #     'history_days_threshold': 30,
    #     'max_age_minutes': 10,
    #     'show_progress': False
    # }

    def __init__(self, data_wrapper_class, **kwargs):
        """
        Initializes an instance of the class with given configuration and validates
        required parameters. Sets up the filesystem to handle storage, ensuring
        necessary directories exist. The configuration supports a variety of options
        to manage parquet storage requirements, including paths, filenames, and date
        ranges.

        :param data_wrapper_class: The class responsible for wrapping data to be managed
                                   by this instance.
        :type data_wrapper_class: type
        :param kwargs: Arbitrary keyword arguments to override default configuration.
                       Includes settings for `date_field`, `parquet_storage_path`,
                       `parquet_filename`, `parquet_start_date`, `parquet_end_date`,
                       `filesystem_type`, `filesystem_options`, and `fs`.
        :type kwargs: dict

        :raises ValueError: If any of the required configuration options
                            (`date_field`, `parquet_storage_path`,
                            `parquet_filename`, `parquet_start_date`,
                            or `parquet_end_date`) are missing or not set properly.
        """

        """Initialize with config, validate required fields, and setup filesystem."""
        self._lock = threading.Lock()
        self.config = {
            **self.DEFAULT_CONFIG,
            **kwargs,
        }
        self.df: Optional[dd.DataFrame] = None
        self._setup_logging()
        self.data_wrapper_class = data_wrapper_class

        self.date_field = self._validate_required('date_field')
        self.parquet_storage_path = self._validate_required('parquet_storage_path')
        self.parquet_filename = self._validate_required('parquet_filename')
        self.parquet_start_date = self._validate_required('parquet_start_date')
        self.parquet_end_date = self._validate_required('parquet_end_date')

        # Filesystem setup
        self.filesystem_type = self.config.setdefault('filesystem_type', 'file')
        self.filesystem_options = self.config.setdefault('filesystem_options', {})
        self.fs = self.config.setdefault('fs', None)
        self._own_fs = self.fs is None
        if self.fs is None:
            self.fs = fsspec.filesystem(self.filesystem_type, **self.filesystem_options)
            self._own_fs = True
        self.config.setdefault('fs', self.fs)
        ## Populate to parameters to pass to data_wrapper_class
        self.class_params = self.config.pop('class_params', {
            'debug': self.debug,
            'logger': self.logger,
            'fs': self.fs,
        })
        # Populate parameters to pass to load method of DataWrapper class
        self.load_params = self.config.setdefault('load_params', {})
        # Ensure the directory exists
        self.ensure_directory_exists(self.parquet_storage_path)
        super().__init__(**self.config)
        self.update_planner_params = {}
        self.datawrapper_params = {}

    def _setup_logging(self):
        """Initialize logger and debug settings."""
        self.debug = self.config.get('debug', False)
        self.logger = self.config.get('logger',
                                      Logger.default_logger(
                                          logger_name=f'Parquet_Artifact_InstanceOf_{self.__class__.__name__}'))
        self.logger.set_level(Logger.DEBUG if self.debug else Logger.INFO)

    def _validate_required(self, key: str) -> Any:
        """Validate required configuration fields."""
        value = self.config.setdefault(key, None)
        if value is None:
            raise ValueError(f'{key} must be set')
        return value

    def _setup_manifest(self, overwrite: bool = False, ignore_missing: bool = False):
        self.skipped = []
        self.missing_manifest_path = f"{self.parquet_storage_path}_manifests/missing.parquet"
        self.mmanifest = MissingManifestManager(
            fs=self.fs,
            manifest_path=self.missing_manifest_path,
            clear_existing=overwrite
        )

        # Initialize skipped files
        manifest_exists = self.mmanifest._safe_exists(self.missing_manifest_path)
        if not manifest_exists:
            self.logger.info(f"Creating new manifest at {self.missing_manifest_path}")
            self.mmanifest.save()
            self.mmanifest.cleanup_temp_manifests()
        else:
            self.logger.info(f"Manifest already exists at {self.missing_manifest_path}")

        # Load skipped files if manifest exists and ignore_missing is True
        self.skipped = self.mmanifest.load_existing()  # if ignore_missing and manifest_exists else []
        self.logger.info(f"Skipped: {self.skipped}")
        if overwrite:
            self.skipped = []
            self.ignore_missing = False

    def _setup_update_planner(self, **kwargs) -> None:
        self._prepare_update_params(**kwargs)
        self.update_planner = UpdatePlanner(**self.update_planner_params)
        self.update_planner.generate_plan(self.start_date, self.end_date)

    def load(self, **kwargs):
        with self._lock:
            self.df = super().load(**kwargs)
        return self.df

    def generate_parquet(self, **kwargs) -> None:
        """
        Generate a Parquet file using the configured DataWrapper class.
        """
        with self._lock:
            overwrite = kwargs.get('overwrite', False)
            ignore_missing = kwargs.get('ignore_missing', False)
            self._setup_manifest(overwrite, ignore_missing)
            self._setup_update_planner(**kwargs)
            params = self.datawrapper_params.copy()
            params.update({
                'mmanifest': self.mmanifest,
                'update_planner': self.update_planner
            })

            with DataWrapper(self.data_wrapper_class, **params) as dw:
                dw.process()

    def __enter__(self):
        if getattr(self, "_entered", False):
            return self
        self._entered = True
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            if self.mmanifest and self.mmanifest._new_records:
                self.mmanifest.save()
                self.mmanifest.cleanup_temp_manifests()
            if getattr(self, "_entered", False) and self.fs and self._own_fs:
                self.fs.close()
        except Exception as e:
            self.logger.warning(f"Error closing filesystem: {e}")
        finally:
            self._entered = False
        # return False so exceptions aren’t suppressed
        return False

    @classmethod
    def get_size_estimate(cls, parquet_path: str, **kwargs) -> int:
        """
        Estimate complexity as total bytes of all .parquet files under parquet_path.
        Returns size in megabytes (so you can cap or scale priority sensibly).
        """
        fs, _, paths = cls.fs.get_fs_token_paths(parquet_path)
        files = fs.glob(f"{parquet_path}/*.parquet")
        total_bytes = sum(fs.size(f) for f in files)
        # convert to “units” (e.g. MB) so priorities stay in a reasonable range
        return max(1, int(total_bytes / (1024 ** 2)))

    def update_parquet(self, period: str = 'today', **kwargs) -> None:
        """Update the Parquet file with data from a specific period."""

        def itd_config():
            try:
                start_date = kwargs.pop('history_begins_on')
            except KeyError:
                raise ValueError("For period 'itd', you must provide 'history_begins_on' in kwargs.")
            return {'parquet_start_date': start_date, 'parquet_end_date': datetime.date.today().strftime('%Y-%m-%d')}

        def ytd_config():
            return {
                'parquet_start_date': datetime.date(datetime.date.today().year, 1, 1).strftime('%Y-%m-%d'),
                'parquet_end_date': datetime.date.today().strftime('%Y-%m-%d')
            }

        def custom_config():
            try:
                start_date = kwargs.pop('start_on')
                end_date = kwargs.pop('end_on')
            except KeyError:
                raise ValueError("For period 'custom', you must provide 'start_on' in kwargs.")
            return {
                'parquet_start_date': start_date,
                'parquet_end_date': end_date
            }

        config_map = {
            'itd': itd_config,
            'ytd': ytd_config,
            'custom': custom_config,
        }

        if period in config_map:
            kwargs.update(config_map[period]())
        else:
            kwargs.update(self.parse_parquet_period(period=period))
        self.logger.debug(f"kwargs passed to update parquet: {kwargs}")
        self.generate_parquet(**kwargs)

    def rebuild_parquet(self, **kwargs) -> None:
        """Rebuild the Parquet file from the start to end date."""
        kwargs.update(self._get_rebuild_params(kwargs))
        self.generate_parquet(**kwargs)

    def _get_rebuild_params(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare parameters for rebuilding the Parquet file."""
        return {
            'overwrite': True,
            'reverse_order': True,
            'start_date': kwargs.get('parquet_start_date', self.parquet_start_date),
            'end_date': kwargs.get('parquet_end_date', self.parquet_end_date),
        }

    def _prepare_update_params(self, **kwargs) -> Dict[str, Any]:
        self.reverse_order = kwargs.pop('reverse_order', True)
        self.overwrite = kwargs.pop('overwrite', False)
        self.ignore_missing = kwargs.pop('ignore_missing', False)
        self.history_days_threshold = kwargs.pop('history_days_threshold', 30)
        self.max_age_minutes = kwargs.pop('max_age_minutes', 10)
        self.show_progress = kwargs.pop('show_progress', False)
        self.start_date = kwargs.pop('parquet_start_date', self.parquet_start_date)
        self.end_date = kwargs.pop('parquet_end_date', self.parquet_end_date)
        self.parquet_filename = kwargs.pop('parquet_filename', self.parquet_filename)
        self.verbose = kwargs.pop('verbose', False)

        self.update_planner_params.update({
            'filename': self.parquet_filename,
            'data_path': self.parquet_storage_path,
            'fs': self.fs,
            'debug': self.debug,
            'logger': self.logger,
            'reverse_order': self.reverse_order,
            'overwrite': self.overwrite,
            'ignore_missing': self.ignore_missing,
            'history_days_threshold': self.history_days_threshold,
            'max_age_minutes': self.max_age_minutes,
            'show_progress': self.show_progress,
            'description': f"{self.data_wrapper_class.__name__}",
            'skipped': self.skipped,
            'verbose': self.verbose,
        })

        self.datawrapper_params = {
            'parquet_filename': self.parquet_filename,
            'data_path': self.parquet_storage_path,
            'fs': self.fs,
            'class_params': self.class_params,
            'date_field': self.date_field,
            'load_params': self.load_params,
            'verbose': self.verbose
        }

    def parse_parquet_period(self, **kwargs):
        start_date, end_date = DateUtils.parse_period(**kwargs)
        self.parquet_start_date = start_date.strftime('%Y-%m-%d')
        self.parquet_end_date = end_date.strftime('%Y-%m-%d')
        return {
            'parquet_start_date': self.parquet_start_date,
            'parquet_end_date': self.parquet_end_date,
        }

    def ensure_directory_exists(self, path: str) -> None:
        """Ensure the directory exists in the specified filesystem."""
        with self._lock:
            try:
                self.fs.makedirs(path, exist_ok=True)
            except Exception as e:
                raise ValueError(f"Error creating directory {path} in filesystem {self.filesystem_type}: {e}")
