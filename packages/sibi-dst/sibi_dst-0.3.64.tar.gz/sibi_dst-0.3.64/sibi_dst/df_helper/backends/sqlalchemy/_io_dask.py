from typing import Type

import dask
import dask.dataframe as dd
import pandas as pd
from sqlalchemy import (
    inspect,
    select,
    func,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base
import time
from sqlalchemy.exc import TimeoutError
import sqlalchemy as sa
from sibi_dst.df_helper.core import FilterHandler
from sibi_dst.utils import Logger


class SQLAlchemyDask:
    """
    Loads data from a database into a Dask DataFrame using a memory-safe,
    non-parallel, paginated approach.

    This class avoids using a numeric `index_col for parallel loading.
    """

    _SQLALCHEMY_TO_DASK_DTYPE = {
        "INTEGER": "Int64",
        "SMALLINT": "Int64",
        "BIGINT": "Int64",
        "FLOAT": "float64",
        "NUMERIC": "float64",
        "BOOLEAN": "bool",
        "VARCHAR": "object",
        "TEXT": "object",
        "DATE": "datetime64[ns]",
        "DATETIME": "datetime64[ns]",
        "TIME": "object",
        "UUID": "object",
    }

    def __init__(
            self,
            model: Type[declarative_base()],
            filters: dict,
            engine: Engine,
            chunk_size: int = 1000,
            logger=None,
            debug: bool = False,
    ):
        """
        Initializes the data loader.

        Args:
            model: The SQLAlchemy ORM model for the table.
            filters: A dictionary of filters to apply to the query.
            engine: An SQLAlchemy Engine instance.
            chunk_size: The number of records to fetch in each database query.
            logger: A logger instance.
            debug: Whether to enable detailed logging.
        """
        self.model = model
        self.filters = filters
        self.engine = engine
        self.chunk_size = chunk_size
        self.debug = debug
        self.logger = logger or Logger.default_logger(logger_name=self.__class__.__name__)
        self.logger.set_level(Logger.DEBUG if debug else Logger.INFO)
        self.filter_handler_cls = FilterHandler

    @classmethod
    def infer_meta_from_model(cls, model: Type[declarative_base()]) -> dict:
        """
        Infers a metadata dictionary for Dask based on the SQLAlchemy model.
        This helps Dask understand the DataFrame structure without reading data.
        """
        mapper = inspect(model)
        dtypes = {}
        for column in mapper.columns:
            dtype_str = str(column.type).upper().split("(")[0]
            dtype = cls._SQLALCHEMY_TO_DASK_DTYPE.get(dtype_str, "object")
            dtypes[column.name] = dtype
        return dtypes

    def read_frame(self, fillna_value=None) -> dd.DataFrame:
        """
        Builds and executes a query to load data into a Dask DataFrame.

        This method works by first running a COUNT query to get the total
        size, then creating a series of delayed tasks that each fetch a
        chunk of data using LIMIT/OFFSET.

        Args:
            fillna_value: Value to replace NaN or NULL values with, if any.

        Returns:
            A lazy Dask DataFrame.
        """
        # 1. Build the base query and apply filters
        query = select(self.model)
        if self.filters:
            query = self.filter_handler_cls(
                backend="sqlalchemy", logger=self.logger, debug=self.debug
            ).apply_filters(query, model=self.model, filters=self.filters)

        self.logger.debug(f"Base query for pagination: {query}")

        # 2. Get metadata for the Dask DataFrame structure
        ordered_columns = [column.name for column in self.model.__table__.columns]
        meta_dtypes = self.infer_meta_from_model(self.model)
        meta_df = pd.DataFrame(columns=ordered_columns).astype(meta_dtypes)

        # 3. Get the total record count to calculate the number of chunks
        # try:
        #     with self.engine.connect() as connection:
        #         count_query = select(func.count()).select_from(query.alias())
        #         total_records = connection.execute(count_query).scalar_one()
        # except Exception as e:
        #     self.logger.error(f"Failed to count records for pagination: {e}", exc_info=True)
        #     return dd.from_pandas(meta_df, npartitions=1)
        retry_attempts = 3
        backoff_factor = 0.5  # start with a 0.5-second delay

        for attempt in range(retry_attempts):
            try:
                with self.engine.connect() as connection:
                    count_query = sa.select(sa.func.count()).select_from(query.alias())
                    total_records = connection.execute(count_query).scalar_one()

                # If successful, break the loop
                break

            except TimeoutError:
                if attempt < retry_attempts - 1:
                    self.logger.warning(
                        f"Connection pool limit reached. Retrying in {backoff_factor} seconds..."
                    )
                    time.sleep(backoff_factor)
                    backoff_factor *= 2  # Double the backoff time for the next attempt
                else:
                    self.logger.error(
                        "Failed to get a connection from the pool after several retries.",
                        exc_info=True
                    )
                    return dd.from_pandas(meta_df, npartitions=1)

            except Exception as e:
                self.logger.error(f"An unexpected error occurred: {e}", exc_info=True)
                return dd.from_pandas(meta_df, npartitions=1)

        if total_records == 0:
            self.logger.warning("Query returned 0 records.")
            return dd.from_pandas(meta_df, npartitions=1)

        self.logger.debug(f"Total records to fetch: {total_records}. Chunk size: {self.chunk_size}.")

        # 4. Create a list of Dask Delayed objects, one for each chunk
        @dask.delayed
        def get_chunk(sql_query, chunk_offset):
            """A Dask-delayed function to fetch one chunk of data."""
            # LIMIT/OFFSET must be applied in the delayed function
            paginated_query = sql_query.limit(self.chunk_size).offset(chunk_offset)
            df = pd.read_sql(paginated_query, self.engine)

            if fillna_value is not None:
                df = df.fillna(fillna_value)

            # Ensure column order and types match the meta
            return df[ordered_columns].astype(meta_dtypes)

        offsets = range(0, total_records, self.chunk_size)
        delayed_chunks = [get_chunk(query, offset) for offset in offsets]

        # 5. Construct the final lazy Dask DataFrame from the delayed chunks
        ddf = dd.from_delayed(delayed_chunks, meta=meta_df)
        self.logger.debug(f"Successfully created a lazy Dask DataFrame with {ddf.npartitions} partitions.")

        return ddf
