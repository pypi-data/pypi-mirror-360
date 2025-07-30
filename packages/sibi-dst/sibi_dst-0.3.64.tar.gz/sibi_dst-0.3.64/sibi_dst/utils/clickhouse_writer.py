from concurrent.futures import ThreadPoolExecutor

import clickhouse_connect
import pandas as pd
from clickhouse_driver import Client
import dask.dataframe as dd

from .log_utils import Logger


class ClickHouseWriter:
    """
    Provides functionality to write a Dask DataFrame to a ClickHouse database using
    a specified schema. This class handles the creation of tables, schema generation,
    data transformation, and data insertion. It ensures compatibility between Dask
    data types and ClickHouse types.

    :ivar clickhouse_host: Host address of the ClickHouse database.
    :type clickhouse_host: str
    :ivar clickhouse_port: Port of the ClickHouse database.
    :type clickhouse_port: int
    :ivar clickhouse_dbname: Name of the database to connect to in ClickHouse.
    :type clickhouse_dbname: str
    :ivar clickhouse_user: Username for database authentication.
    :type clickhouse_user: str
    :ivar clickhouse_password: Password for database authentication.
    :type clickhouse_password: str
    :ivar clickhouse_table: Name of the table to store the data in.
    :type clickhouse_table: str
    :ivar logger: Logger instance for logging messages.
    :type logger: logging.Logger
    :ivar client: Instance of the ClickHouse database client.
    :type client: clickhouse_connect.Client or None
    :ivar df: Dask DataFrame to be written into ClickHouse.
    :type df: dask.dataframe.DataFrame
    :ivar order_by: Field or column name to use for table ordering.
    :type order_by: str
    """
    dtype_to_clickhouse = {
        'int64': 'Int64',
        'int32': 'Int32',
        'float64': 'Float64',
        'float32': 'Float32',
        'bool': 'UInt8',
        'datetime64[ns]': 'DateTime',
        'object': 'String',
        'category': 'String',
    }
    df: dd.DataFrame

    def __init__(self, logger=None, **kwargs):
        self.clickhouse_host = kwargs.setdefault('host', "localhost")
        self.clickhouse_port = kwargs.setdefault('port', 8123)
        self.clickhouse_dbname = kwargs.setdefault('database', 'sibi_data')
        self.clickhouse_user = kwargs.setdefault('user', 'default')
        self.clickhouse_password = kwargs.setdefault('password', '')
        self.clickhouse_table = kwargs.setdefault('table', 'test_sibi_table')

        self.logger = logger or Logger.default_logger(logger_name=self.__class__.__name__)
        self.client = None
        self.order_by = kwargs.setdefault('order_by', 'id')

    def save_to_clickhouse(self, df, **kwargs):
        self.df = df.copy()
        self.order_by = kwargs.setdefault('order_by', self.order_by)
        if len(self.df.head().index) == 0:
            self.logger.debug("Dataframe is empty")
            return
        self._handle_missing_values()
        self._connect()
        self._drop_table()
        self._create_table_from_dask()
        self._write_data()

    def _connect(self):
        try:
            self.client = clickhouse_connect.get_client(
                host=self.clickhouse_host,
                port=self.clickhouse_port,
                database=self.clickhouse_dbname,
                user=self.clickhouse_user,
                password=self.clickhouse_password
            )
            self.logger.debug("Connected to ClickHouse")
        except Exception as e:
            self.logger.error(e)
            raise

    @staticmethod
    def _generate_clickhouse_schema(dask_dtypes, dtype_map):
        schema = []
        for col, dtype in dask_dtypes.items():
            # Handle pandas nullable types explicitly
            if isinstance(dtype, pd.Int64Dtype):  # pandas nullable Int64
                clickhouse_type = 'Int64'
            elif isinstance(dtype, pd.Float64Dtype):  # pandas nullable Float64
                clickhouse_type = 'Float64'
            elif isinstance(dtype, pd.BooleanDtype):  # pandas nullable Boolean
                clickhouse_type = 'UInt8'
            elif isinstance(dtype, pd.DatetimeTZDtype) or 'datetime' in str(dtype):  # Nullable datetime
                clickhouse_type = 'Nullable(DateTime)'
            elif isinstance(dtype, pd.StringDtype):  # pandas nullable String
                clickhouse_type = 'String'
            else:
                # Default mapping using the provided dtype_map
                clickhouse_type = dtype_map.get(str(dtype), 'String')
            schema.append(f"`{col}` {clickhouse_type}")
        return ', '.join(schema)

    def _drop_table(self):
        if self.client:
            self.client.command('DROP TABLE IF EXISTS {}'.format(self.clickhouse_table))
            self.logger.debug(f"Dropped table {self.clickhouse_table}")

    def _create_table_from_dask(self, engine=None):
        if engine is None:
            engine = f"ENGINE = MergeTree() order by {self.order_by}"
        dtypes = self.df.dtypes
        clickhouse_schema = self._generate_clickhouse_schema(dtypes, self.dtype_to_clickhouse)
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {self.clickhouse_table} ({clickhouse_schema}) {engine};"
        self.logger.debug(f"Creating table SQL:{create_table_sql}")
        if self.client:
            self.client.command(create_table_sql)
            self.logger.debug("Created table '{}'".format(self.clickhouse_table))

    def _handle_missing_values(self):
        """
        Handle missing values in the Dask DataFrame before writing to ClickHouse.
        """
        self.logger.debug("Checking for missing values...")
        missing_counts = self.df.isnull().sum().compute()
        self.logger.debug(f"Missing values per column:\n{missing_counts}")

        # Replace missing values based on column types
        def replace_missing_values(df):
            for col in df.columns:
                if pd.api.types.is_integer_dtype(df[col]):
                    df[col] = df[col].fillna(0)  # Replace NA with 0 for integers
                elif pd.api.types.is_float_dtype(df[col]):
                    df[col] = df[col].fillna(0.0)  # Replace NA with 0.0 for floats
                elif pd.api.types.is_bool_dtype(df[col]):
                    df[col] = df[col].fillna(False)  # Replace NA with False for booleans
                else:
                    df[col] = df[col].fillna('')  # Replace NA with empty string for other types
            return df

        # Apply replacement
        self.df = replace_missing_values(self.df)
        self.logger.debug("Missing values replaced.")

    def _write_data(self):
        """
        Writes the Dask DataFrame to a ClickHouse table partition by partition.
        """
        if len(self.df.index) == 0:
            self.logger.debug("No data found. Nothing written.")
            return

        for i, partition in enumerate(self.df.to_delayed()):
            try:
                # Compute the current partition into a pandas DataFrame
                df = partition.compute()

                if df.empty:
                    self.logger.debug(f"Partition {i} is empty. Skipping...")
                    continue

                self.logger.debug(f"Writing partition {i} with {len(df)} rows to ClickHouse.")

                # Write the partition to the ClickHouse table
                self.client.insert_df(self.clickhouse_table, df)
            except Exception as e:
                self.logger.error(f"Error writing partition {i}: {e}")

    def _write_data_multi_not_working_yet(self):
        """
        Writes the Dask DataFrame to a ClickHouse table partition by partition.
        Ensures a separate client instance is used per thread to avoid session conflicts.
        """
        if len(self.df.index) == 0:
            self.logger.debug("No data found. Nothing written.")
            return

        def create_client():
            client = Client(
                host=self.clickhouse_host,
                port=self.clickhouse_port,
                database=self.clickhouse_dbname,
                user=self.clickhouse_user,
                password=self.clickhouse_password
            )
            """
            Create a new instance of the ClickHouse client for each thread.
            This avoids session conflicts during concurrent writes.
            """
            return client

        def write_partition(partition, index):
            """
            Write a single partition to ClickHouse using a separate client instance.
            """
            try:
                self.logger.debug(f"Starting to process partition {index}")
                client = create_client()  # Create a new client for the thread

                # Compute the Dask partition into a Pandas DataFrame
                df = partition.compute()
                if df.empty:
                    self.logger.debug(f"Partition {index} is empty. Skipping...")
                    return

                # Convert DataFrame to list of tuples
                data = [tuple(row) for row in df.to_numpy()]
                columns = df.columns.tolist()

                # Perform the insert
                self.logger.debug(f"Writing partition {index} with {len(df)} rows to ClickHouse.")
                client.execute(f"INSERT INTO {self.clickhouse_table} ({', '.join(columns)}) VALUES", data)

            except Exception as e:
                self.logger.error(f"Error writing partition {index}: {e}")
            finally:
                if 'client' in locals() and hasattr(client, 'close'):
                    client.close()
                    self.logger.debug(f"Closed client for partition {index}")

        try:
            # Get delayed partitions and enumerate them
            partitions = self.df.to_delayed()
            with ThreadPoolExecutor() as executor:
                executor.map(write_partition, partitions, range(len(partitions)))
        except Exception as e:
            self.logger.error(f"Error during multi-partition write: {e}")
