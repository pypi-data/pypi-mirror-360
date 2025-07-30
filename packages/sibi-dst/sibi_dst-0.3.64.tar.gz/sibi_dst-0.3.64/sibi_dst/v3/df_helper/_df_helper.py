from typing import Union, Optional
import pandas as pd
import dask.dataframe as dd

# Refactored DfHelper class
class DfHelper:
    """
    DfHelper is a utility class that orchestrates loading and processing data.
    It uses a configured BackendStrategy to handle the specifics of data loading.
    """
    df: Union[dd.DataFrame, pd.DataFrame] = None

    def __init__(self, backend_strategy: BackendStrategy,
                 params_config: ParamsConfig,
                 as_pandas: bool = False,
                 debug: bool = False,
                 logger: Optional[Logger] = None):

        self.backend_strategy = backend_strategy
        self._backend_params = params_config  # Needed for post-processing and field mapping
        self.as_pandas = as_pandas
        self.debug = debug
        self.logger = logger or Logger.default_logger(logger_name=self.__class__.__name__)
        self.logger.set_level(Logger.DEBUG if self.debug else Logger.INFO)

        # Other attributes like parquet saving paths can be passed in here if needed
        # self.parquet_storage_path = kwargs.get("parquet_storage_path")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        # Cleanup logic for resources that DfHelper itself might manage
        # The connection cleanup is now the responsibility of the caller who creates the strategy
        if hasattr(self.backend_strategy, 'connection') and hasattr(self.backend_strategy.connection, 'close'):
            self.backend_strategy.connection.close()
        return False

    def load(self, **options):
        """
        Loads data using the configured backend strategy, applies transformations,
        and returns a DataFrame.
        """
        try:
            self.logger.debug(f"Loading data using {self.backend_strategy.__class__.__name__}...")
            # 1. Delegate loading to the strategy object
            self.df = self.backend_strategy.load(**options)

            # 2. Perform post-processing (these methods remain in DfHelper)
            self.__process_loaded_data()
            self.__post_process_df()
            self.logger.debug("Data successfully loaded and processed.")

        except Exception as e:
            self.logger.error(f"Failed to load data using {self.backend_strategy.__class__.__name__}: {e}")
            self.df = dd.from_pandas(pd.DataFrame(), npartitions=1)

        if self.as_pandas and isinstance(self.df, dd.DataFrame):
            return self.df.compute()
        return self.df

    def load_period(self, start: str, end: str, dt_field: str, **kwargs):
        """
        Loads data for a specific period by delegating filter creation to the strategy.
        """
        if dt_field is None:
            raise ValueError("dt_field must be provided")

        # Parse and validate dates
        start_dt = self.parse_date(start)
        end_dt = self.parse_date(end)
        if start_dt > end_dt:
            raise ValueError("The 'start' date cannot be later than the 'end' date.")

        # Delegate the creation of filter logic to the current strategy
        field_map = getattr(self._backend_params, 'field_map', {}) or {}
        period_filters = self.backend_strategy.build_period_filter(
            dt_field, start_dt, end_dt, field_map
        )

        # Combine with other filters and load
        all_filters = {**kwargs, **period_filters}
        self.logger.debug(f"Loading period with combined filters: {all_filters}")
        return self.load(**all_filters)

    # The methods __process_loaded_data, __post_process_df, save_to_parquet,
    # save_to_clickhouse, and parse_date remain unchanged as they are
    # part of the orchestration logic, not the loading strategy itself.

    # ... (paste those methods here without modification) ...
    # ... __process_loaded_data, __post_process_df, save_to_parquet, etc. ...