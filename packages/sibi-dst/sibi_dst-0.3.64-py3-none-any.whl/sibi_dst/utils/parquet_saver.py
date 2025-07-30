import base64
import hashlib
import logging
import threading
import warnings
from typing import Optional

import pyarrow as pa

# Suppress the specific UserWarning message
warnings.filterwarnings("ignore")
from .log_utils import Logger


class ParquetSaver:
    def __init__(self, df_result, parquet_storage_path, logger=None, fs=None, debug=False):
        """
        Initialize ParquetSaver.
        :param df_result: Dask DataFrame to save.
        :param parquet_storage_path: Base storage path (e.g., "s3://bucket-name/path/").
        :param logger: Logger instance for logging messages.
        :param fs: Pre-initialized fsspec filesystem instance. Defaults to 'file' if None.
        """
        self.df_result = df_result
        self.parquet_storage_path = parquet_storage_path.rstrip("/")
        self.debug = debug
        self.logger = logger or Logger.default_logger(logger_name=self.__class__.__name__)
        self.logger.set_level(logging.DEBUG if self.debug else logging.INFO)
        self.fs = fs
        self.protocol = self.parquet_storage_path.split(":")[0]
        self._lock = threading.Lock()

    def save_to_parquet(self, parquet_filename: Optional[str] = None, clear_existing=True):
        """
        Save the DataFrame to Parquet format.
        :param parquet_filename: Filename for the Parquet file.
        :param clear_existing: Whether to clear existing files in the target directory.
        """
        with self._lock:
            full_path = self._construct_full_path(parquet_filename)
            self.logger.info(f"Save method for :{full_path}")
            # Ensure directory exists and clear if necessary
            self._ensure_directory_exists(full_path, clear_existing=clear_existing)

            # Define schema and save DataFrame to Parquet
            schema = self._define_schema()
            self._convert_dtypes(schema)
            self._save_dataframe_to_parquet(full_path, schema)
            # Close the filesystem if the close method exists
            if hasattr(self.fs, 'close') and callable(getattr(self.fs, 'close', None)):
                self.fs.close()

    def _define_schema(self) -> pa.Schema:
        """Define a PyArrow schema dynamically based on df_result column types."""
        pandas_dtype_to_pa = {
            "object": pa.string(),
            "string": pa.string(),
            "Int64": pa.int64(),
            "int64": pa.int64(),
            "float64": pa.float64(),
            "float32": pa.float32(),
            "bool": pa.bool_(),
            "boolean": pa.bool_(),  # pandas nullable boolean
            "datetime64[ns]": pa.timestamp("ns"),
            "timedelta[ns]": pa.duration("ns"),
        }

        dtypes = self.df_result.dtypes

        fields = [
            pa.field(col, pandas_dtype_to_pa.get(str(dtype), pa.string()))
            for col, dtype in dtypes.items()
        ]
        return pa.schema(fields)

    def _convert_dtypes(self, schema: pa.Schema):
        """Convert DataFrame columns to match the specified schema."""
        dtype_mapping = {}
        for field in schema:
            col_name = field.name
            if col_name in self.df_result.columns:
                if pa.types.is_string(field.type):
                    dtype_mapping[col_name] = "string"
                elif pa.types.is_int64(field.type):
                    dtype_mapping[col_name] = "Int64"
                elif pa.types.is_float64(field.type):
                    dtype_mapping[col_name] = "float64"
                elif pa.types.is_float32(field.type):
                    dtype_mapping[col_name] = "float32"
                elif pa.types.is_boolean(field.type):
                    dtype_mapping[col_name] = "boolean"
                elif pa.types.is_timestamp(field.type):
                    dtype_mapping[col_name] = "datetime64[ns]"
                else:
                    dtype_mapping[col_name] = "object"
        self.df_result = self.df_result.astype(dtype_mapping)

    def _construct_full_path(self, parquet_filename: Optional[str]) -> str:
        """Construct and return the full path for the Parquet file."""
        parquet_filename = parquet_filename or "default.parquet"
        return f"{self.parquet_storage_path}/{parquet_filename}"

    def _ensure_directory_exists(self, full_path: str, clear_existing=False):
        """
        Ensure that the directory for the path exists, clearing it if specified.
        :param full_path: Full path for the target file.
        :param clear_existing: Whether to clear existing files/directories.
        """
        directory = "/".join(full_path.split("/")[:-1])
        if self.fs.exists(directory):
            self.logger.info(f"Directory already exists: {directory}")
            if clear_existing:
                self._clear_directory(directory)

        if not self.fs.exists(directory):
            self.logger.info(f"Creating directory: {directory}")
            self.fs.mkdirs(directory, exist_ok=True)

    def _save_dataframe_to_parquet(self, full_path: str, schema: pa.Schema):
        """Save the DataFrame to Parquet using the specified schema."""
        #self._clear_directory(full_path)
        self.logger.info(f"Saving/Overwrite Parquet file to: {full_path}")
        self.df_result.to_parquet(
             path=full_path,
             engine="pyarrow",
             schema=schema,
             #overwrite=True,
             filesystem=self.fs,
             write_index=False,
        )

    def _clear_directory(self, directory: str):
        """
        Clears the specified directory by removing all the files within it. If the
        directory is not associated with the "s3" protocol, it will be removed using
        the local filesystem's functionality. For directories using the "s3" protocol,
        the bucket name and prefix are parsed, and files are deleted using the S3
        client's `delete_objects` method.

        :param directory: The directory path to clear. If the protocol is not "s3", it
                          represents a local filesystem path. Otherwise, it is assumed
                          to be an S3 path (e.g., "s3://bucket_name/prefix").
        :type directory: str
        """
        if self.protocol != "s3":
            if self.fs.exists(directory):
                self.logger.info(f"Clearing directory: {directory}")
                self.fs.rm(directory, recursive=True)
            return
        # Parse bucket name and prefix
        bucket_name, prefix = self._parse_s3_path(directory)

        # List files in the directory
        files = self.fs.ls(directory, detail=True)
        if not files:
            self.logger.info(f"No files to delete in directory: {directory}")
            return

        # Generate the delete payload
        objects_to_delete = [{"Key": file["name"].replace(f"{bucket_name}/", "", 1)} for file in files]
        delete_payload = {
            "Objects": objects_to_delete,
            "Quiet": True,
        }

        # Calculate Content-MD5
        payload_bytes = str(delete_payload).encode("utf-8")
        md5_hash = hashlib.md5(payload_bytes).digest()
        content_md5 = base64.b64encode(md5_hash).decode("utf-8")

        # Use the underlying s3 client to delete objects
        try:
            self.fs.s3.delete_objects(
                Bucket=bucket_name,
                Delete=delete_payload,
                ContentMD5=content_md5,
            )
            self.logger.info(f"Successfully deleted files in {directory}.")
        except Exception as e:
            self.logger.error(f"Failed to delete objects in {directory}: {e}")
            pass

    @staticmethod
    def _parse_s3_path(s3_path: str):
        """
        Parse an S3 path into bucket name and prefix.
        :param s3_path: Full S3 path (e.g., s3://bucket-name/path/).
        :return: Tuple of bucket name and prefix.
        """
        if not s3_path.startswith("s3://"):
            raise ValueError("Invalid S3 path. Must start with 's3://'.")
        path_parts = s3_path[5:].split("/", 1)
        bucket_name = path_parts[0]
        prefix = path_parts[1] if len(path_parts) > 1 else ""
        return bucket_name, prefix

