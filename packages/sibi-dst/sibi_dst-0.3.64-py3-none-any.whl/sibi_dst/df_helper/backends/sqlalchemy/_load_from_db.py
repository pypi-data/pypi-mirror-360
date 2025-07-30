import dask.dataframe as dd
import pandas as pd

from sibi_dst.df_helper.core import ParamsConfig, QueryConfig
from sibi_dst.utils import Logger
from ._db_connection import SqlAlchemyConnectionConfig
from ._io_dask import SQLAlchemyDask


class SqlAlchemyLoadFromDb:
    """
    Orchestrates loading data from a database using SQLAlchemy into a Dask
    DataFrame by configuring and delegating to the SQLAlchemyDask loader.
    """

    def __init__(
            self,
            plugin_sqlalchemy: SqlAlchemyConnectionConfig,
            plugin_query: QueryConfig = None,
            plugin_params: ParamsConfig = None,
            logger: Logger = None,
            **kwargs,
    ):
        """
        Initializes the loader with all necessary configurations.

        Args:
            plugin_sqlalchemy: The database connection configuration object.
            plugin_query: The query configuration object.
            plugin_params: The parameters and filters configuration object.
            logger: An optional logger instance.
            **kwargs: Must contain 'index_column' for Dask partitioning.
        """
        self.db_connection = plugin_sqlalchemy
        self.model = self.db_connection.model
        self.engine = self.db_connection.engine
        self.logger = logger or Logger.default_logger(logger_name=self.__class__.__name__)
        self.query_config = plugin_query
        self.params_config = plugin_params
        self.debug = kwargs.get("debug", False)
        self.chunk_size = kwargs.get("chunk_size", self.params_config.df_params.get("chunk_size", 1000))

    def build_and_load(self) -> dd.DataFrame:
        """
        Builds and loads a Dask DataFrame from a SQLAlchemy source.

        This method is stateless and returns the DataFrame directly.

        Returns:
            A Dask DataFrame containing the queried data or an empty,
            correctly structured DataFrame if the query fails or returns no results.
        """
        try:
            # Instantiate and use the low-level Dask loader
            sqlalchemy_dask_loader=SQLAlchemyDask(
                model=self.model,
                filters=self.params_config.filters if self.params_config else {},
                engine=self.engine,
                chunk_size=self.chunk_size,
                logger=self.logger,
                debug=self.debug
            )
            # Create the lazy DataFrame
            dask_df = sqlalchemy_dask_loader.read_frame()
            return dask_df


        except Exception as e:
            self.logger.error(f"Failed to build and load data: {e}", exc_info=True)
            # Return an empty dataframe with the correct schema on failure
            columns = [c.name for c in self.model.__table__.columns]
            return dd.from_pandas(pd.DataFrame(columns=columns), npartitions=1)


