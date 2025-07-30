import logging
from typing import Optional

import dask.dataframe as dd
import fsspec

from sibi_dst.df_helper import DfHelper
from sibi_dst.utils import Logger

class ParquetReader(DfHelper):
    """
    This class is a specialized helper for reading and managing Parquet files.

    The `ParquetReader` class is designed to facilitate working with Parquet
    datasets stored across different filesystems. It initializes the required
    resources, ensures the existence of the specified Parquet directory,
    and provides an abstraction to load the data into a Dask DataFrame.

    The class requires configuration for the storage path and dates defining
    a range of interest. It also supports various filesystem types through
    `fsspec`.

    :ivar config: Holds the final configuration for this instance, combining
        `DEFAULT_CONFIG` with user-provided configuration.
    :type config: dict
    :ivar df: Stores the loaded Dask DataFrame after the `load()` method is
        invoked. Initially set to None.
    :type df: Optional[dd.DataFrame]
    :ivar parquet_storage_path: The path to the Parquet storage directory.
    :type parquet_storage_path: str
    :ivar parquet_start_date: Start date for Parquet data selection. Must
        be set in the configuration.
    :type parquet_start_date: str
    :ivar parquet_end_date: End date for Parquet data selection. Must be
        set in the configuration.
    :type parquet_end_date: str
    :ivar filesystem_type: The type of filesystem the Parquet files are
        stored on (e.g., "file", "s3").
    :type filesystem_type: str
    :ivar filesystem_options: Any additional options required for the
        specified filesystem type.
    :type filesystem_options: dict
    :ivar fs: Instance of `fsspec` filesystem used to interact with the
        Parquet storage.
    :type fs: fsspec.AbstractFileSystem
    """
    DEFAULT_CONFIG = {
        'backend': 'parquet'
    }

    def __init__(self, filesystem_type="file", filesystem_options=None, **kwargs):
        self.config = {
            **self.DEFAULT_CONFIG,
            **kwargs,
        }
        self.df: Optional[dd.DataFrame] = None
        self.debug = self.config.setdefault('debug', False)
        self.logger = self.config.setdefault('logger', Logger.default_logger(logger_name=self.__class__.__name__))
        self.logger.set_level(logging.DEBUG if self.debug else logging.INFO)
        self.parquet_storage_path = self.config.setdefault('parquet_storage_path', None)
        if self.parquet_storage_path is None:
            raise ValueError('parquet_storage_path must be set')
        self.parquet_start_date = self.config.setdefault('parquet_start_date', None)
        if self.parquet_start_date is None:
            raise ValueError('parquet_start_date must be set')

        self.parquet_end_date = self.config.setdefault('parquet_end_date', None)
        if self.parquet_end_date is None:
            raise ValueError('parquet_end_date must be set')

        # Filesystem setup
        self.filesystem_type = filesystem_type
        self.filesystem_options = filesystem_options or {}
        self.fs = self.config.setdefault('fs', None)
        if self.fs is None:
            self.fs = fsspec.filesystem(self.filesystem_type, **self.filesystem_options)
        self.config.setdefault('fs', self.fs)

        if not self.directory_exists():
            raise ValueError(f"{self.parquet_storage_path} does not exist")

        super().__init__(**self.config)

    def load(self, **kwargs):
        self.df = super().load(**kwargs)
        return self.df

    def directory_exists(self):
        try:
            info = self.fs.info(self.parquet_storage_path)
            return info['type'] == 'directory'
        except FileNotFoundError:
            return False

    def __exit__(self, exc_type, exc_value, traceback):
        # Ensure resources are cleaned up
        if self.fs:
            self.fs.close()
