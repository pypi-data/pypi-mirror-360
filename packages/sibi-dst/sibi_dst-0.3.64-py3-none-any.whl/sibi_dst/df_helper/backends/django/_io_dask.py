import itertools

import dask.dataframe as dd
import django
import pandas as pd
from django.core.cache import cache
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.models import Field
from django.utils.encoding import force_str as force_text


class ReadFrameDask:
    """
    Handles Django ORM QuerySet to Dask DataFrame conversion with support for field
    type inference, chunked data retrieval, and verbose updates.

    This class provides methods to efficiently convert a Django QuerySet into a
    Dask DataFrame while preserving field types and incorporating additional
    capabilities such as replacing fields with verbose choices or related object
    information. The class design leverages static and class methods to maintain
    flexibility and reusability for handling Django model fields and their data
    types.

    :ivar qs: The Django QuerySet to be converted into a Dask DataFrame.
    :type qs: django.db.models.query.QuerySet
    :ivar coerce_float: Whether to attempt to coerce numeric values to floats.
    :type coerce_float: bool
    :ivar chunk_size: The number of records to fetch and process per chunk from
        the QuerySet.
    :type chunk_size: int
    :ivar verbose: If True, provides verbose updates during DataFrame creation
        by replacing fields with readable representations (e.g., verbose names).
    :type verbose: bool
    """
    FieldDoesNotExist = (
        django.core.exceptions.FieldDoesNotExist
        if django.VERSION < (1, 8)
        else django.core.exceptions.FieldDoesNotExist
    )

    def __init__(
            self,
            qs,
            **kwargs,
    ):
        """
        An initialization method for a class that sets class attributes based on provided
        arguments or default values using the keyword arguments. The method allows
        customization of behaviors like coercing data types, handling chunked operations,
        and verbosity level during execution.

        :param qs: A data source or query set for processing; its type is dependent
            on the expected data being handled.
        :param kwargs: Additional keyword arguments that may include:
            - coerce_float: A boolean indicating whether floats should be coerced
              during handling. Default is False.
            - chunk_size: An integer value representing the size of chunks for
              data processing. Default is 1000.
            - verbose: A boolean to specify if verbose logging or output
              should occur during execution. Default is True.
        """
        self.qs = qs
        self.coerce_float = kwargs.setdefault("coerce_float", False)
        self.chunk_size = kwargs.setdefault("chunk_size", 1000)
        self.verbose = kwargs.setdefault("verbose", True)

    @staticmethod
    def replace_from_choices(choices):
        """
        Provides a method to replace elements in a list of values based on a mapping of choices.

        This static method generates a closure function that replaces items in a list by
        looking up their corresponding values in a provided dictionary of choices. If an
        item cannot be found in the dictionary, it is left unchanged.

        :param choices:
            Dictionary where keys are original values and values are their replacements.
        :return:
            A function that takes a list of values and replaces elements using the
            provided choices dictionary.
        """
        def inner(values):
            return [choices.get(v, v) for v in values]

        return inner

    @staticmethod
    def get_model_name(model):
        """
        Retrieves the model name from a given Django model instance.

        This method accesses the `_meta.model_name` attribute of the provided
        model object to extract and return the model's name.

        :param model: A Django model instance from which the model name is
            derived.
        :type model: object
        :return: The name of the model as a string.
        :rtype: str
        """
        return model._meta.model_name

    @staticmethod
    def get_related_model(field):
        """
        Retrieve the related model from the provided field.

        This function determines the related model associated with the given field.
        It checks various attributes commonly used to indicate relations in models and
        retrieves the related model if present.

        :param field: The field from which the related model is to be extracted.
                      It must be an object that potentially contains attributes like
                      `related_model` or `rel`.
        :return: The related model associated with the provided field, or None if
                 no such model is found.
        """
        model = None
        if hasattr(field, "related_model") and field.related_model:
            model = field.related_model
        elif hasattr(field, "rel") and field.rel:
            model = field.rel.to
        return model

    @classmethod
    def get_base_cache_key(cls, model):
        """
        Generates a base cache key for caching purposes.

        This method constructs a base cache key that can be used in conjunction with
        Django models to uniquely identify cache entries. The key is formatted to
        include the app label and model name, ensuring that cache entries are
        namespaced accordingly.

        :param model: A Django model instance for which the base cache key is generated.
        :type model: Model
        :return: The string template for the base cache key, where `%s` can be replaced
                 with specific identifiers to create unique keys.
        :rtype: str
        """
        return (
            f"dask_{model._meta.app_label}_{cls.get_model_name(model)}_%s_rendering"
        )

    @classmethod
    def replace_pk(cls, model):
        """
        Generates a function that replaces primary keys in a pandas Series with their
        corresponding cached values or database-retrieved representations.

        The function uses a cache mechanism to retrieve pre-stored values for primary
        keys in the series. If some primary keys are not found in the cache, it queries
        the database for their representations, updates the cache, and replaces the
        primary keys in the series accordingly.

        :param model: The Django model class associated with the primary keys to be
            processed.
        :type model: Type[Model]

        :return: A function that takes a pandas Series of primary keys as input and
            returns a Series with replaced values based on cache or database retrieval.
        :rtype: callable
        """
        base_cache_key = cls.get_base_cache_key(model)

        def get_cache_key_from_pk(pk):
            return None if pk is None else base_cache_key % str(pk)

        def inner(pk_series):
            pk_series = pk_series.astype(object).where(pk_series.notnull(), None)
            cache_keys = pk_series.apply(get_cache_key_from_pk, convert_dtype=False)
            unique_cache_keys = list(filter(None, cache_keys.unique()))
            if not unique_cache_keys:
                return pk_series

            out_dict = cache.get_many(unique_cache_keys)
            if len(out_dict) < len(unique_cache_keys):
                out_dict = dict(
                    [
                        (base_cache_key % obj.pk, force_text(obj))
                        for obj in model.objects.filter(
                        pk__in=list(filter(None, pk_series.unique()))
                    )
                    ]
                )
                cache.set_many(out_dict)
            return list(map(out_dict.get, cache_keys))

        return inner

    @classmethod
    def build_update_functions(cls, fieldnames, fields):
        """
        This method is responsible for building update functions based on the provided
        fieldnames and fields. It performs validation for the field type, checks for
        specific conditions such as `choices` or `ForeignKey` field types, and generates
        a generator of update functions for the given fieldnames and fields.

        :param fieldnames: A list of field names to be processed.
        :type fieldnames: list[str]
        :param fields: A list of field objects corresponding to the fieldnames.
        :type fields: list[Field]
        :return: A generator yielding tuples where the first element is a fieldname,
                 and the second element is the corresponding update function or None.
        :rtype: generator[tuple[str, Callable | None]]
        """
        for fieldname, field in zip(fieldnames, fields):
            if not isinstance(field, Field):
                yield fieldname, None
            else:
                if field.choices:
                    choices = dict([(k, force_text(v)) for k, v in field.flatchoices])
                    yield fieldname, cls.replace_from_choices(choices)
                elif field.get_internal_type() == "ForeignKey":
                    yield fieldname, cls.replace_pk(cls.get_related_model(field))

    @classmethod
    def update_with_verbose(cls, df, fieldnames, fields):
        """
        Updates the provided dataframe by applying transformation functions to specified fields.
        The method iterates over the provided field names and their corresponding functions, applying
        each transformation function to its related column in the dataframe.

        :param df: The input dataframe to be updated.
        :param fieldnames: A list of field names in the dataframe that need to be updated.
        :param fields: A list of transformation functions or mappings corresponding to the field names.
        :return: The dataframe with updated fields.
        """
        for fieldname, function in cls.build_update_functions(fieldnames, fields):
            if function is not None:
                df[fieldname] = df[fieldname].map_partitions(lambda x: function(x))

    @classmethod
    def to_fields(cls, qs, fieldnames):
        """
        Converts field names from a queryset into corresponding field objects, resolving relationships
        and related objects if necessary. This method is typically used to yield fully-resolved field
        objects for further interaction.

        :param qs: A QuerySet object from which the fields are resolved. This object provides access
                   to the model and its metadata from which the fields are retrieved.
        :type qs: QuerySet

        :param fieldnames: A list of field name strings. These can include nested fields separated by
                           double underscores (__) to denote relationships or subfields.
        :type fieldnames: List[str]

        :return: A generator that yields resolved field objects corresponding to the provided field names.
        :rtype: Generator[Field, None, None]
        """
        for fieldname in fieldnames:
            model = qs.model
            for fieldname_part in fieldname.split("__"):
                try:
                    field = model._meta.get_field(fieldname_part)
                except cls.FieldDoesNotExist:
                    try:
                        rels = model._meta.get_all_related_objects_with_model()
                    except AttributeError:
                        field = fieldname
                    else:
                        for relobj, _ in rels:
                            if relobj.get_accessor_name() == fieldname_part:
                                field = relobj.field
                                model = field.model
                                break
                else:
                    model = cls.get_related_model(field)
            yield field

    @staticmethod
    def is_values_queryset(qs):
        """
        Determines whether the provided queryset is a values queryset.

        This method checks if the `_iterable_class` attribute of the queryset corresponds
        to `django.db.models.query.ValuesIterable`. If an exception occurs during the check,
        the method returns `False`.

        :param qs: The queryset to be checked.
        :type qs: django.db.models.query.QuerySet
        :return: A boolean indicating whether the queryset is a values queryset.
        :rtype: bool
        """
        try:
            return qs._iterable_class == django.db.models.query.ValuesIterable
        except:
            return False

    @staticmethod
    def object_to_dict(obj, fields=None):
        """
        Converts an object to a dictionary representation.

        This static method transforms an object's attributes into a dictionary.
        If no specific fields are provided, all attribute key-value pairs are
        included. The "_state" attribute, if present, is safely removed in this
        case. When specific fields are supplied, only those fields are included
        in the resulting dictionary.

        :param obj: The object to be serialized into a dictionary. This object
            must have the `__dict__` attribute available.
        :param fields: A list of strings representing the attribute names to
            include in the dictionary. If None or not provided, all attributes
            are included except for "_state".
        :return: A dictionary representation of the object's attributes. If the
            provided object is None, an empty dictionary is returned.
        :rtype: dict
        """
        if obj is None:
            return {}  # Return an empty dictionary if obj is None
        if not fields:
            obj.__dict__.pop("_state", None)  # Remove _state safely
            return obj.__dict__
        return {field: obj.__dict__.get(field) for field in fields if field is not None}

    @staticmethod
    def infer_dtypes_from_django(qs):
        """
        Infer dtypes from a Django QuerySet model and annotated fields.

        This method infers the appropriate data types (dtypes) for a given
        Django QuerySet (`qs`) based on the fields defined in its model and
        any annotated fields included in the QuerySet. The function maps
        Django model field types to corresponding dtypes compatible with
        Dask or Pandas dataframes.

        - Fields in the model are identified through their metadata.
        - Reverse relationships and non-concrete fields are ignored.
        - Annotated fields are processed separately and default to object
          dtype if their type cannot be determined.

        :param qs: Django QuerySet whose model is used to infer dtypes.
        :type qs: QuerySet
        :return: A mapping of field names to inferred dtypes.
        :rtype: dict
        """
        django_to_dask_dtype = {
            'AutoField': 'Int64',  # Use nullable integer
            'BigAutoField': 'Int64',
            'BigIntegerField': 'Int64',
            'BooleanField': 'bool',
            'CharField': 'object',
            'DateField': 'datetime64[ns]',
            'DateTimeField': 'datetime64[ns]',
            'DecimalField': 'float64',
            'FloatField': 'float64',
            'IntegerField': 'Int64',  # Use nullable integer
            'PositiveIntegerField': 'Int64',
            'SmallIntegerField': 'Int64',
            'TextField': 'object',
            'TimeField': 'object',
            'UUIDField': 'object',
            'ForeignKey': 'Int64',  # Use nullable integer for FK fields
        }

        dtypes = {}
        # Handle model fields
        for field in qs.model._meta.get_fields():
            # Skip reverse relationships and non-concrete fields
            if not getattr(field, 'concrete', False):
                continue

            # Check for AutoField or BigAutoField explicitly
            if isinstance(field, (models.AutoField, models.BigAutoField)):
                dtypes[field.name] = 'Int64'  # Nullable integer for autoincremented fields
            else:
                # Use field type to infer dtype
                field_type = field.get_internal_type()
                dtypes[field.name] = django_to_dask_dtype.get(field_type, 'object')

        # Handle annotated fields
        for annotation_name, annotation in qs.query.annotation_select.items():
            if hasattr(annotation, 'output_field'):
                field_type = annotation.output_field.get_internal_type()
                dtype = django_to_dask_dtype.get(field_type, 'object')
            else:
                dtype = 'object'  # Default to object for untyped annotations
            dtypes[annotation_name] = dtype

        return dtypes

    def read_frame(self, fillna_value=None):
        """
        Reads a Django QuerySet and returns a dask DataFrame by iterating over the QuerySet in chunks. It
        handles data type inference, missing values, timezone awareness, and creates partitions to form a
        single dask DataFrame efficiently.

        This method includes functionality for managing missing values, inferring data types from Django fields,
        and handling timezone-aware datetime objects. It processes data in chunks to optimize memory usage and
        supports converting chunks into pandas DataFrames before combining them into a unified dask DataFrame.

        :param fillna_value: The value to fill NaN values in the DataFrame. If None, NaNs are not filled.
        :type fillna_value: Any
        :return: A dask DataFrame constructed from the QuerySet after processing and combining all
                 its partitions.
        :rtype: dask.dataframe.DataFrame
        """
        qs = self.qs
        coerce_float = self.coerce_float
        verbose = self.verbose
        chunk_size = self.chunk_size

        fields = qs.model._meta.fields
        fieldnames = [f.name for f in fields]
        fieldnames += list(qs.query.annotation_select.keys())
        fieldnames = tuple(fieldnames)
        # Infer dtypes from Django fields
        dtypes = self.infer_dtypes_from_django(qs)
        if fieldnames:
            dtypes = {field: dtype for field, dtype in dtypes.items() if field in fieldnames}

        # Create partitions for Dask by iterating through chunks
        partitions = []
        iterator = iter(qs.iterator(chunk_size=chunk_size))

        while True:
            chunk = list(itertools.islice(iterator, chunk_size))
            if not chunk:
                break

            # Convert chunk to DataFrame with inferred dtypes
            df = pd.DataFrame.from_records(
                [self.object_to_dict(obj, fieldnames) for obj in chunk],
                columns=fieldnames,
                coerce_float=coerce_float,
            )
            # Handle NaN values before casting, if specified
            if fillna_value is not None:
                df = df.fillna(fillna_value)

            # Convert timezone-aware columns to timezone-naive if needed
            for col in df.columns:
                if isinstance(df[col].dtype, pd.DatetimeTZDtype):
                    df[col] = df[col].dt.tz_localize(None)

            # Convert to the appropriate data types
            df = df.astype(dtypes)
            partitions.append(dd.from_pandas(df, npartitions=1))

        # Concatenate partitions into a single Dask DataFrame
        # Ensure all partitions have the same columns

        dask_df = dd.concat(partitions, axis=0, ignore_index=True)

        if verbose:
            self.update_with_verbose(dask_df, fieldnames, fields)

        return dask_df
