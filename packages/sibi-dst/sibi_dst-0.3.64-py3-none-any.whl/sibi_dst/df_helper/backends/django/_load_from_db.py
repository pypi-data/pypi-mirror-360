import warnings

import dask.dataframe as dd
import pandas as pd
from django.db.models import Q

from sibi_dst.df_helper.backends.django import ReadFrameDask
from sibi_dst.df_helper.core import django_field_conversion_map_dask
from sibi_dst.utils import Logger


class DjangoLoadFromDb:
    """
    Handles loading data from a Django database into a Dask DataFrame, with support for filtering
    and column type conversion.

    This class is designed to interface with Django ORM models, allowing data querying and mapping
    Django model fields to Dask DataFrame columns. It accommodates filtering logic provided via
    parameters and ensures that excessive data is not accidentally loaded when no filters are applied.

    :ivar connection_config: Configuration for the database connection, including the Django model
        and connection details.
    :type connection_config: Any
    :ivar query_config: Configuration for the query, including the number of records to retrieve.
    :type query_config: Any
    :ivar params_config: Configuration for query parameters, including filters and DataFrame options.
    :type params_config: Any
    :ivar logger: Logger instance used for debugging and reporting runtime information.
    :type logger: Logger
    :ivar debug: Indicates whether debug mode is active for verbose logging.
    :type debug: bool
    :ivar df: Dask DataFrame to hold the loaded query results.
    :type df: dd.DataFrame
    """
    df: dd.DataFrame

    def __init__(self, db_connection, db_query, db_params, logger, **kwargs):
        """
        This class initializes and configures a database connection along with the
        specified query and parameters. It ensures the required model is defined
        and sets up logging. Additional configurations can be provided via keyword
        arguments.

        :param db_connection: The configuration object representing the database
            connection details.
        :type db_connection: Any
        :param db_query: The configuration or object for defining the database
            query.
        :type db_query: Any
        :param db_params: The configuration or object for defining parameters
            to be passed to the query.
        :type db_params: Any
        :param logger: An instance of a logging class used to log debug or
            error messages, defaults to the class's default logger if not
            specified.
        :type logger: Any, optional
        :param kwargs: Additional keyword arguments for custom configurations
            like `debug`. These can include optional parameters to be parsed by
            `params_config`.
        :type kwargs: dict
        :raises ValueError: If no model is specified in the given database
            connection configuration.
        """
        self.connection_config = db_connection
        self.debug = kwargs.pop('debug', False)
        self.logger = logger or Logger.default_logger(logger_name=self.__class__.__name__)
        self.logger.set_level(Logger.DEBUG if self.debug else Logger.INFO)
        if self.connection_config.model is None:
            if self.debug:
                self.logger.debug('Model must be specified')

            raise ValueError('Model must be specified')

        self.query_config = db_query
        self.params_config = db_params
        self.params_config.parse_params(kwargs)

    def build_and_load(self):
        """
        Builds and loads data into a DataFrame by invoking the `_build_and_load` method.
        This is a utility method designed to perform specific operations for constructing
        and preparing the data. The loaded data will then be assigned to the instance
        attribute `df`.

        :param self: Reference to the current instance of the class.
        :type self: object

        :return: DataFrame containing the built and loaded data.
        """
        self.df = self._build_and_load()
        # self.df = self._convert_columns(self.df)
        return self.df

    def _build_and_load(self) -> dd.DataFrame:
        """
        Builds and loads a Dask DataFrame based on the provided query and configuration. This method queries the data
        model using the specified connection, applies filters if provided, and converts the query result into a
        Dask DataFrame. If filters are not provided, only the first `n_records` entries are processed to avoid
        unintentionally loading the entire table.

        :raises Exception: If an error occurs while loading the query, it logs the error and initializes an
            empty Dask DataFrame.

        :return: A Dask DataFrame containing the queried data. If no filters or valid results are provided,
            an empty Dask DataFrame is returned.
        :rtype: dd.DataFrame
        """
        query = self.connection_config.model.objects.using(self.connection_config.connection_name)
        if not self.params_config.filters:
            # IMPORTANT: if no filters are provided show only the first n_records
            # this is to prevent loading the entire table by mistake
            n_records = self.query_config.n_records if self.query_config.n_records else 100
            queryset = query.all()[:n_records]
        else:
            q_objects = self.__build_query_objects(self.params_config.filters, self.query_config.use_exclude)
            queryset = query.filter(q_objects)
        if queryset is not None:
            try:
                self.df = ReadFrameDask(queryset, **self.params_config.df_params).read_frame()
            except Exception as e:
                self.logger.debug(f'Error loading query: {str(queryset.query)}, error message: {e}')
                self.df = dd.from_pandas(pd.DataFrame(), npartitions=1)
        else:
            self.df = dd.from_pandas(pd.DataFrame(), npartitions=1)

        return self.df

    @staticmethod
    def __build_query_objects(filters: dict, use_exclude: bool):
        """
        Constructs and returns a composite Q object based on the provided `filters` dictionary.
        The function determines whether to include or exclude the filter conditions in the final
        query based on the `use_exclude` parameter. If `use_exclude` is False, the filters are
        directly added to the composite Q object. If `use_exclude` is True, the negation of
        the filters is added instead.

        :param filters: A dictionary containing filter conditions where keys represent field names
            and values represent the conditions to be applied.
        :type filters: dict
        :param use_exclude: A boolean flag determining whether to exclude (`True`) or include
            (`False`) the provided filter conditions.
        :type use_exclude: bool
        :return: A composite Q object that aggregates the filters based on the given conditions.
        :rtype: Q
        """
        q_objects = Q()
        for key, value in filters.items():
            if not use_exclude:
                q_objects.add(Q(**{key: value}), Q.AND)
            else:
                q_objects.add(~Q(**{key: value}), Q.AND)
        return q_objects

    def _convert_columns(self, df: dd.DataFrame) -> dd.DataFrame:
        """
        [DEPRECATED] Convert the data types of columns in a Dask DataFrame based on the field type in the Django model.

        This function is deprecated and will be removed in a future release. The method converts the data
        types of columns in a Dask DataFrame to match their corresponding field types defined in a Django model.
        It emits warnings and logs deprecation notes. The conversions are applied lazily and partition-wise
        to support distributed computation.

        :param df: Dask DataFrame whose columns' data types are to be converted.
        :type df: dd.DataFrame
        :return: Dask DataFrame with converted column data types.
        :rtype: dd.DataFrame
        """
        """
            [DEPRECATED] Convert the data types of columns in a Dask DataFrame based on the field type in the Django model.

            :param df: Dask DataFrame whose columns' data types are to be converted.
            :return: Dask DataFrame with converted column data types.
            """
        # Emit deprecation warning
        warnings.warn(
            "_convert_columns is deprecated and will be removed in a future release. "
            "Consider using <new_method_name> instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        # Log deprecation message if debug mode is enabled
        if self.debug:
            self.logger.warning(
                "[DEPRECATION NOTICE] The `_convert_columns` method is deprecated and will be removed in a future release. "
                "Consider using <new_method_name> instead."
            )

        self.logger.debug(f'Converting columns: {list(df.columns)}')

        # Get field information from the Django model
        model_fields = self.connection_config.model._meta.get_fields()
        field_type_map = {field.name: type(field).__name__ for field in model_fields}
        # Simplified loop to apply conversions partition-wise
        for field_name, field_type in field_type_map.items():
            if field_name not in df.columns:
                self.logger.debug(f"Column '{field_name}' not found in DataFrame columns.")
                continue

            conversion_func = django_field_conversion_map_dask.get(field_type)
            if not conversion_func:
                message = f"Field type '{field_type}' not found in conversion_map."
                self.logger.debug(message)
                continue

            def apply_conversion(partition):
                """
                Apply the conversion function to a single partition for the given column.
                """
                try:
                    if field_name in partition.columns:
                        partition[field_name] = conversion_func(partition[field_name])
                except Exception as e:
                    self.logger.debug(f"Error converting column '{field_name}' in partition: {str(e)}")
                return partition

            try:
                # Apply conversion lazily to each partition
                df = df.map_partitions(
                    apply_conversion,
                    meta=df,
                )
                self.logger.debug(f"Successfully queued conversion for column '{field_name}' to type '{field_type}'.")
            except Exception as e:
                self.logger.debug(f"Failed to queue conversion for column '{field_name}': {str(e)}")

        return df
