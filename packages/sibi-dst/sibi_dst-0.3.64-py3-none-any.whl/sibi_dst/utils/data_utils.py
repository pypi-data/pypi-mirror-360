
from typing import Union, List

import dask.dataframe as dd
import pandas as pd

from .log_utils import Logger


class DataUtils:
    """
    Utility class for data transformation, manipulation, and merging.

    This class provides functionalities for transforming numeric and boolean columns, merging
    lookup data, checking DataFrame emptiness, and converting columns to datetime format in
    Pandas or Dask DataFrames. It is designed to handle data preprocessing steps efficiently
    for both small-scale and large-scale datasets. Logging and debug options are available
    to trace execution and monitor operations.

    :ivar logger: Logger instance for logging messages.
    :type logger: logging.Logger
    :ivar debug: Flag to enable or disable debug mode.
    :type debug: bool
    """
    def __init__(self, logger=None, **kwargs):
        self.logger = logger or Logger.default_logger(logger_name=self.__class__.__name__)
        self.debug = kwargs.get('debug', False)

    @staticmethod
    def _transform_column(series, fill_value, dtype):
        """
        Helper method to transform a column by converting it to numeric, filling missing values,
        and casting to the specified dtype.

        :param series: The column to transform.
        :type series: pd.Series or dd.Series
        :param fill_value: Value to replace missing or invalid data.
        :type fill_value: int or float
        :param dtype: Target data type for the column.
        :type dtype: type
        :return: Transformed column.
        :rtype: pd.Series or dd.Series
        """
        return (
            pd.to_numeric(series, errors="coerce")  # Convert to numeric, invalid to NaN
            .fillna(fill_value)  # Replace NaN with fill_value
            .astype(dtype)  # Convert to target dtype
        )

    def transform_numeric_columns(self, df: Union[pd.DataFrame, dd.DataFrame], columns: List[str], fill_value=0,
                                  dtype=int):
        """
        Transform specified numeric columns in the DataFrame by converting their data types
        to the specified dtype and replacing missing values with the given fill_value.

        :param df: DataFrame to be transformed.
        :type df: pd.DataFrame or dd.DataFrame
        :param columns: List of column names to transform.
        :type columns: list[str]
        :param fill_value: Value to replace missing or invalid data. Default is 0.
        :type fill_value: int or float
        :param dtype: Target data type for the columns. Default is int.
        :type dtype: type
        :return: Transformed DataFrame.
        :rtype: pd.DataFrame or dd.DataFrame
        """
        if not columns:
            self.logger.warning("No columns specified.")
            return df

        self.logger.debug(f"DataFrame type: {type(df)}")
        columns = [col for col in columns if col in df.columns]

        for col in columns:
            df[col] = df[col].map_partitions(
                self._transform_column, fill_value, dtype, meta=(col, dtype)
            )

        return df

    def transform_numeric_cols(self, df, columns, fill_value=0, dtype=int):
        """
        This function transforms the specified numeric columns in the given dataframe by converting
        their data types to the specified dtype, with an optional parameter for replacing missing
        values. It first checks if the provided columns exist in the dataframe, processes each column
        to replace non-numeric values with NaN, fills NaN values with the given fill_value, and finally
        converts the column to the specified dtype.

        :param df: DataFrame to be transformed.
        :type df: dask.dataframe.DataFrame
        :param columns: List of column names to be transformed.
        :type columns: list[str]
        :param fill_value: Value used to replace missing or invalid data. Default is 0.
        :type fill_value: int or float
        :param dtype: Target data type for the columns after transformation. Default is int.
        :type dtype: type
        :return: Transformed dataframe with the specified numeric columns converted and modified.
        :rtype: dask.dataframe.DataFrame
        """
        if not columns:
            self.logger.warning('No columns specified')
        self.logger.debug(f'Dataframe type:{type(df)}')
        columns = [column for column in columns if column in df.columns]
        for col in columns:
            # Replace NaN with 0, then convert to boolean
            df[col] = df[col].map_partitions(
                lambda s: pd.to_numeric(s, errors='coerce')  # Convert to numeric, invalid to NaN
                .fillna(fill_value)  # Replace NaN with 0
                .astype(dtype),
                meta=(col, dtype)
            )

        return df

    def transform_boolean_columns(self, df: Union[pd.DataFrame, dd.DataFrame], columns: List[str], fill_value=0):
        """
        Convert specified columns in the DataFrame to boolean, replacing missing values with
        the given fill_value.

        :param df: DataFrame to be transformed.
        :type df: pd.DataFrame or dd.DataFrame
        :param columns: List of column names to transform.
        :type columns: list[str]
        :param fill_value: Value to replace missing or invalid data. Default is 0.
        :type fill_value: int or float
        :return: Transformed DataFrame.
        :rtype: pd.DataFrame or dd.DataFrame
        """
        return self.transform_numeric_columns(df, columns, fill_value=fill_value, dtype=bool)

    def merge_lookup_data(self, classname, df, **kwargs):
        """
        Merge lookup data into the DataFrame based on specified columns.

        Parameters:
        - classname: The class instance to use for loading lookup data.
        - df (pandas.DataFrame or dask.dataframe.DataFrame): The DataFrame.
        - kwargs: Additional keyword arguments for configuration.

        Returns:
        - pandas.DataFrame or dask.dataframe.DataFrame: Updated DataFrame with merged lookup data.
        """
        # Return early if the DataFrame is empty
        if self.is_dataframe_empty(df):
            self.logger.debug("merge_lookup_data was given an empty dataFrame")
            return df

        # Extract and validate required parameters
        required_params = ['source_col', 'lookup_col', 'lookup_description_col', 'source_description_alias']
        missing_params = [param for param in required_params if param not in kwargs]
        if missing_params:
            raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")

        source_col = kwargs.pop('source_col')
        lookup_col = kwargs.pop('lookup_col')
        lookup_description_col = kwargs.pop('lookup_description_col')
        source_description_alias = kwargs.pop('source_description_alias')

        # Optional parameters with default values
        fillna_source_description_alias = kwargs.pop('fillna_source_description_alias', False)
        fieldnames = kwargs.pop('fieldnames', (lookup_col, lookup_description_col))
        column_names = kwargs.pop('column_names', ['temp_join_col', source_description_alias])

        if source_col not in df.columns:
            self.logger.debug(f"{source_col} not in DataFrame columns")
            return df

        # Get unique IDs from source column
        ids = df[source_col].dropna().unique()
        # Compute if it's a Dask Series
        if isinstance(ids, dd.Series):
            ids = ids.compute()

        # Check if any IDs are found
        if not len(ids):
            self.logger.debug(f"No IDs found in the source column: {source_col}")
            return df

        # Convert to a list only if necessary and sort
        if not isinstance(ids, list):
            ids = ids.tolist()
        ids = sorted(ids)
        # Prepare kwargs for loading lookup data
        load_kwargs = kwargs.copy()
        load_kwargs.update({
            'fieldnames': fieldnames,
            'column_names': column_names,
            f'{lookup_col}__in': ids
        })
        # Load lookup data
        lookup_instance = classname(debug=self.debug, logger=self.logger)
        result = lookup_instance.load(**load_kwargs)
        if len(result.index) == 0:
            self.logger.debug(f"No IDs found in the source column: {source_col}")
            return df
        # Determine the join column on the result DataFrame
        temp_join_col = 'temp_join_col' if 'temp_join_col' in column_names else lookup_col

        # Merge DataFrames
        df = df.merge(result, how='left', left_on=source_col, right_on=temp_join_col)

        if fillna_source_description_alias and source_description_alias in df.columns:
            df[source_description_alias] = df[source_description_alias].fillna('')

        # Drop temp_join_col if present
        df = df.drop(columns='temp_join_col', errors='ignore')

        return df

    def is_dataframe_empty(self, df):
        """
        Check if a DataFrame (Pandas or Dask) is empty.

        Parameters:
        - df (pandas.DataFrame or dask.dataframe.DataFrame): The DataFrame.

        Returns:
        - bool: True if the DataFrame is empty, False otherwise.
        """
        if isinstance(df, dd.DataFrame):
            try:
                return len(df.index) == 0
            except Exception as e:
                self.logger.error(f"Error while processing Dask DataFrame: {e}")
                return False
        elif isinstance(df, pd.DataFrame):
            return df.empty
        else:
            self.logger.error("Input must be a pandas or dask DataFrame.")
            return False

    @staticmethod
    def convert_to_datetime_dask(df, date_fields):
        """
        Convert specified columns in a Dask DataFrame to datetime, handling errors gracefully.

        Parameters:
        - df (dask.dataframe.DataFrame): The Dask DataFrame containing the columns.
        - date_fields (list of str): List of column names to convert to datetime.

        Returns:
        - dask.dataframe.DataFrame: Updated DataFrame with specified columns converted to datetime.
        """
        for col in date_fields:
            if col in df.columns:
                df[col] = df[col].map_partitions(pd.to_datetime, errors="coerce", meta=(col, "datetime64[ns]"))
        return df

