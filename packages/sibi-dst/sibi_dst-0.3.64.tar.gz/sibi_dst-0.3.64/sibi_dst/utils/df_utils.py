import dask.dataframe as dd
import pandas as pd

from .log_utils import Logger
import warnings
warnings.filterwarnings("ignore", message="Sorting a Dask DataFrame is expensive and may not be efficient")

class DfUtils:
    def __init__(self, logger=None):
        """
        Utility class for DataFrame operations compatible with both pandas and Dask DataFrames.

        Parameters:
            logger (Logger, optional): Logger instance for logging information.
        """
        self.logger = logger or Logger.default_logger(logger_name=self.__class__.__name__)

    @classmethod
    def compute_to_list(cls, series):
        return series.compute().tolist() if hasattr(series, "compute") else series.tolist()

    def extract_unique_values(self, df, *columns):
        return {col: self.compute_to_list(df[col].dropna().unique()) for col in columns}

    def align_and_merge_by_type(self, df_left, df_right, type_mapping, how='left'):
        """
        Align column data types in two DataFrames based on a type mapping dictionary and perform the merge.

        Parameters:
        - df_left (pd.DataFrame or dd.DataFrame): Left DataFrame
        - df_right (pd.DataFrame or dd.DataFrame): Right DataFrame
        - type_mapping (dict): Dictionary mapping target dtypes to column pairs.
          Example: {
              'integer': [('customer_id', 'temp1'), ('product_type_id', 'temp2')],
              'string': [('group2', 'temp4')]
          }

        Returns:
        - Merged DataFrame
        """
        # Map string keys to actual dtypes
        dtype_map = {
            'integer': 'int64',
            'float': 'float64',
            'string': 'string',
            'datetime': 'datetime64[ns]',
            'boolean': 'bool',
        }

        # Iterate over each dtype and align the column pairs
        for target_type, column_pairs in type_mapping.items():
            if target_type not in dtype_map:
                self.logger.error(f"Unsupported type: {target_type}")

            for left_col, right_col in column_pairs:
                # Align dtypes in left and right DataFrames
                if left_col in df_left.columns and right_col in df_right.columns:
                    df_left[left_col] = df_left[left_col].astype(dtype_map[target_type])
                    df_right[right_col] = df_right[right_col].astype(dtype_map[target_type])

        # Flatten all column pairs for the merge operation
        all_pairs = [pair for pairs in type_mapping.values() for pair in pairs]

        # Perform the merge
        return df_left.merge(
            df_right,
            how=how,
            left_on=[pair[0] for pair in all_pairs],
            right_on=[pair[1] for pair in all_pairs]
        )

    def exclude_from_dataframe(self, df, conditions):
        """
        Generic function to filter rows from a DataFrame (Pandas or Dask).

        Parameters:
        - df (pandas.DataFrame or dask.dataframe.DataFrame): The DataFrame to filter.
        - conditions (list of tuples): List of conditions to apply for filtering.
          Each condition is a tuple: (column_name, operator, value).

        Returns:
        - pandas.DataFrame or dask.dataframe.DataFrame: Filtered DataFrame.
        """
        import operator

        # Mapping string operators to actual Python operators
        ops = {
            "==": operator.eq,
            "!=": operator.ne,
            "<": operator.lt,
            "<=": operator.le,
            ">": operator.gt,
            ">=": operator.ge,
        }
        # Ensure all specified columns exist in the DataFrame
        missing_columns = [col for col, _, _ in conditions if col not in df.columns]
        if missing_columns:
            self.logger.debug(f"The following columns are missing in the DataFrame: {', '.join(missing_columns)}")
            return df

        # Build the combined filtering condition
        combined_condition = None
        for col, op, value in conditions:
            if op not in ops:
                raise ValueError(f"Unsupported operator: {op}")

            # Get the individual condition
            condition = ops[op](df[col], value)

            # Combine the condition with AND (&)
            combined_condition = condition if combined_condition is None else (combined_condition & condition)

        # Apply the filtering and return the DataFrame
        return df[~combined_condition]

    def load_grouped_activity(self, df, group_by_expr, group_expr='count', debug=False):
        """
        Groups the DataFrame by the specified expression and computes the size.

        Parameters:
            df (DataFrame): Pandas or Dask DataFrame to be grouped.
            group_by_expr (str or list): Column(s) to group by.
            group_expr (str): Name of the size/count column.
            debug (bool): If True, logs grouping information.

        Returns:
            DataFrame: Grouped DataFrame with counts.
        """
        if debug:
            self.logger.debug(f"Grouping by: {group_by_expr}")

        df_grouped = df.groupby(by=group_by_expr).size().reset_index(name=group_expr)
        return df_grouped

    def eval_duplicate_removal(self, df, duplicate_expr, sort_field=None, keep='last', debug=False):
        """
        Removes duplicate rows based on the specified columns.

        Parameters:
            df (DataFrame): Pandas or Dask DataFrame from which duplicates are to be removed.
            duplicate_expr (str or list): Column(s) to identify duplicates.
            sort_field (str, optional): Column to sort by before dropping duplicates.
            keep (str): Which duplicate to keep ('first' or 'last').
            debug (bool): If True, logs duplicate rows.

        Returns:
            DataFrame: DataFrame with duplicates removed.
        """
        if duplicate_expr is None:
            return df

        if debug:
            df_duplicates = df[df.duplicated(subset=duplicate_expr)]
            self.logger.debug(f"Duplicate Rows based on columns {duplicate_expr} are:\n{df_duplicates}")

        if sort_field:
            if isinstance(df, dd.DataFrame):
                self.logger.warning("Sorting a Dask DataFrame is expensive and may not be efficient.")
            df = df.sort_values(sort_field)

        # Optimize duplicate removal for Dask DataFrames
        if isinstance(df, dd.DataFrame):
            df = df.drop_duplicates(subset=duplicate_expr, keep=keep, split_every=False)
        else:
            df = df.drop_duplicates(subset=duplicate_expr, keep=keep)

        return df

    def load_latest(self, df, duplicate_expr, sort_field=None, debug=False):
        """
        Removes duplicates keeping the latest occurrence.

        Parameters:
            df (DataFrame): Pandas or Dask DataFrame.
            duplicate_expr (str or list): Column(s) to identify duplicates.
            sort_field (str, optional): Column to sort by before dropping duplicates.
            debug (bool): If True, logs duplicate rows.

        Returns:
            DataFrame: DataFrame with latest duplicates removed.
        """
        return self.eval_duplicate_removal(df, duplicate_expr, sort_field=sort_field, keep='last', debug=debug)

    def load_earliest(self, df, duplicate_expr, sort_field=None, debug=False):
        """
        Removes duplicates keeping the earliest occurrence.

        Parameters:
            df (DataFrame): Pandas or Dask DataFrame.
            duplicate_expr (str or list): Column(s) to identify duplicates.
            sort_field (str, optional): Column to sort by before dropping duplicates.
            debug (bool): If True, logs duplicate rows.

        Returns:
            DataFrame: DataFrame with the earliest duplicates removed.
        """
        return self.eval_duplicate_removal(df, duplicate_expr, sort_field=sort_field, keep='first', debug=debug)

    @staticmethod
    def add_df_totals(df):
        """
        Adds total row and column to the DataFrame.

        Parameters:
            df (DataFrame): Pandas or Dask DataFrame.

        Returns:
            DataFrame: DataFrame with total row and column added.
        """
        if isinstance(df, dd.DataFrame):
            # Dask DataFrames are immutable; compute sums and convert to pandas
            col_totals = df.sum(numeric_only=True).compute()
            row_totals = df.sum(axis=1, numeric_only=True).compute()

            df = df.compute()
            df.loc['Total'] = col_totals
            df['Total'] = row_totals
        else:
            df.loc['Total'] = df.sum(numeric_only=True)
            df['Total'] = df.sum(axis=1, numeric_only=True)
        return df

    def summarise_data(self, df, summary_column, values_column, rule='D', agg_func='count'):
        """
        Summarizes data by creating a pivot table and resampling.

        Parameters:
            df (DataFrame): Pandas or Dask DataFrame.
            summary_column (str or list): Column(s) for summarization.
            values_column (str or list): Column(s) to aggregate.
            rule (str): Resampling frequency (e.g., 'D' for daily).
            agg_func (str or function): Aggregation function.

        Returns:
            DataFrame: Resampled pivot table.
        """
        if isinstance(df, dd.core.DataFrame):
            # Implement Dask-compatible pivot and resample
            self.logger.debug("Performing summarization with Dask DataFrame.")
            # Ensure the index is a datetime for resampling
            if not isinstance(df.index, (pd.DatetimeIndex, dd.core.DatetimeIndex)):
                self.logger.warning("Index is not a DatetimeIndex. Converting index to datetime.")
                df = df.set_index(dd.to_datetime(df.index))

            # Group by index and summary columns
            df_grouped = df.groupby([dd.to_datetime(df.index)] + [summary_column])[values_column].agg(
                agg_func).reset_index()

            # Pivot the table
            df_pivot = df_grouped.pivot_table(index='index', columns=summary_column, values=values_column,
                                              aggfunc='sum').fillna(0)

            # Resample
            df_pivot.index = dd.to_datetime(df_pivot.index)
            df_pivot = df_pivot.repartition(freq=rule)
            df_resampled = df_pivot.map_partitions(lambda df: df.resample(rule).sum())

            return df_resampled.compute()
        else:
            df_pivot = df.pivot_table(
                index=df.index,
                columns=summary_column,
                values=values_column,
                aggfunc=agg_func
            ).fillna(0)
            df_resampled = df_pivot.resample(rule).sum()
            return df_resampled

    @staticmethod
    def summarize_and_resample_data(df, summary_columns, value_columns, rule='D', agg_func='count'):
        """
        Summarizes and resamples data.

        Parameters:
            df (DataFrame): Pandas or Dask DataFrame.
            summary_columns (str or list): Column(s) for summarization.
            value_columns (str or list): Column(s) to aggregate.
            rule (str): Resampling frequency.
            agg_func (str or function): Aggregation function.

        Returns:
            DataFrame: Resampled pivot table.
        """
        return DfUtils.summarise_data(df, summary_columns, value_columns, rule=rule, agg_func=agg_func)
