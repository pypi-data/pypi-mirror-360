
import keyword
import re
from functools import lru_cache

from django.apps import apps
from django.db import connections
from django.db import models
from django.db.models.constants import LOOKUP_SEP

FIELD_MAP = {
    "AutoField": models.AutoField,
    "BigAutoField": models.BigAutoField,
    "BigIntegerField": models.BigIntegerField,
    "BinaryField": models.BinaryField,
    "BooleanField": models.BooleanField,
    "CharField": models.CharField,
    "DateField": models.DateField,
    "DateTimeField": models.DateTimeField,
    "DecimalField": models.DecimalField,
    "DurationField": models.DurationField,
    "EmailField": models.EmailField,
    "FileField": models.FileField,
    "FilePathField": models.FilePathField,
    "FloatField": models.FloatField,
    "ImageField": models.ImageField,
    "IntegerField": models.IntegerField,
    "GenericIPAddressField": models.GenericIPAddressField,
    "NullBooleanField": models.NullBooleanField,
    "PositiveIntegerField": models.PositiveIntegerField,
    "PositiveSmallIntegerField": models.PositiveSmallIntegerField,
    "SlugField": models.SlugField,
    "SmallIntegerField": models.SmallIntegerField,
    "TextField": models.TextField,
    "TimeField": models.TimeField,
    "URLField": models.URLField,
    "UUIDField": models.UUIDField,
    # For related fields, they may need to be handled depending on use cases
    "ForeignKey": models.ForeignKey,
    "OneToOneField": models.OneToOneField,
    "ManyToManyField": models.ManyToManyField,
}
# the following is the name of the app that will be used to associate the created on-the-fly model.
# It must be registered in INSTALLED_APPS in settings.py to prevent django from throwing an error
# when a model is reloaded.

apps_label = "datacubes"


class DjangoSqlModelBuilder:
    """
    Handles the dynamic creation of Django ORM models based on database table structures.

    This class takes input parameters such as database connection and table name,
    and dynamically maps the table's schema to a Django ORM model. The resultant model
    can be used for various ORM operations like querying, saving, and deleting records.
    The class utilizes Django's introspection features and allows customization
    through its fields and methods.

    :ivar connection_name: The name of the database connection being used.
    :type connection_name: str
    :ivar table: The name of the database table for which the model is being built.
    :type table: str
    :ivar model: The dynamically generated Django model or None if not created yet.
    :type model: type | None
    """
    def __init__(self, **kwargs):
        """
        Represents an initialization method for a class that handles the
        assignment of attributes and processes the given keyword arguments
        through an internal utility function. This method sets up the
        necessary attributes for later use.

        :param kwargs: A collection of keyword arguments used by the internal
            parsing method to populate the attributes of the class. Specific
            expected keys and their usage should be detailed in the internal
            implementation.
        """
        self.connection_name = None
        self.table = None
        self.model = None
        self.__parse_builder(**kwargs)

    def __parse_builder(self, **kwargs):
        """
        Parses and initializes the builder properties based on provided keyword
        arguments. Validates that the required 'connection_name' and 'table'
        values are present and sets the corresponding attributes. If validation
        fails, raises appropriate errors. Returns the updated builder object
        after initialization. This method is primarily intended for internal
        use to configure the builder.

        :param kwargs: Keyword arguments containing configuration values for
                       initializing the builder. Should include 'connection_name'
                       and 'table' keys.
        :type kwargs: dict
        :return: Returns the instance of the builder object after initialization.
        :rtype: self
        :raises ValueError: If 'connection_name' or 'table' is not provided in
                            the keyword arguments.
        """
        self.connection_name = kwargs.get("connection_name", None)
        self.table = kwargs.get("table", None)
        self.model = None
        if not self.connection_name:
            raise ValueError("Connection name is required")
        if not self.table:
            raise ValueError("Table name is required")
        return self

    @lru_cache(maxsize=None)
    def build_model(self):
        """
        Builds and retrieves a model instance with dynamically defined fields.

        This method attempts to retrieve a model instance by its name and, if it
        does not exist, creates a new model with the specified table structure.
        The model is either fetched or constructed using the provided data about
        its fields. The result is cached for repeated calls to improve performance
        and avoid redundant computations.

        :raises LookupError: If the model cannot be fetched or created due to an
                             invalid lookup.

        :return: A model instance dynamically constructed or retrieved for the
                 specified table and fields.
        :rtype: Model
        """
        model = None
        model_fields = self.get_model_fields()
        model_name = self.table2model(self.table)
        if model_fields:
            try:
                model = apps.get_model(apps_label, model_name)
            except LookupError:
                model = self.create_model(model_name, model_fields)
        return model

    def create_model(self, name, fields) -> type:
        """
        Creates a Django model class dynamically.

        This function takes in a model name and a dictionary of fields, dynamically
        creates a Meta class where additional metadata for the model (like
        `db_table`, `managed`, `app_label`) is defined, and then uses Python's
        standard library `type()` function to generate and return the model class
        on the fly.

        :param name: The name of the model class to create.
        :type name: str
        :param fields: A dictionary mapping field names to their definitions in
            Django's model field format. Each field definition should include
            the field type and optional parameters.
        :type fields: dict
        :return: The dynamically created Django model class based on the provided
            name and fields.
        :rtype: type
        """
        def parse_args(arg_string):
            arg_dict = {}
            # Match keyword arguments in the form key=value
            for match in re.finditer(r"(\w+)=(\w+)", arg_string):
                key, value = match.groups()
                # Try to convert value to an integer, if possible
                try:
                    value = int(value)
                except ValueError:
                    # If it's not an integer, leave it as a string
                    pass
                arg_dict[key] = value
            return arg_dict

        class Meta:
            pass

        setattr(Meta, "db_table", self.table)
        setattr(Meta, "managed", False)
        setattr(Meta, "app_label", apps_label)

        model = None
        attrs = {
            "Meta": Meta,
            "__module__": f"{apps_label}.models",
            "objects": models.Manager(),
        }
        if fields:
            for field_name, field_type in fields.items():
                field_type, args = field_type.replace("models.", "").split("(", 1)
                args = args.rstrip(")")
                field_params = parse_args(args)
                field_class = FIELD_MAP[field_type]
                attrs[field_name] = field_class(**field_params)
            model = type(name, (models.Model,), attrs)

        return model

    @staticmethod
    def table2model(table_name):
        """
        Converts a database table name to a corresponding model name by transforming
        it from snake_case to CamelCase. This method takes a string representing
        a table name, splits it by underscores, capitalizes the first letter of
        each part, and then joins them into a single string.

        :param table_name: The name of the database table in snake_case format
        :type table_name: str
        :return: A string representing the equivalent model name in CamelCase format
        :rtype: str
        """
        return "".join([x.title() for x in table_name.split("_")])

    def get_model_fields(self):
        """
        Generates the data structure for model fields from a database table using
        introspection. The method extracts information about columns, primary keys,
        unique constraints, and additional metadata to define the fields of the model.

        :raises ValueError: If the specified connection or table is not found.
        :raises Exception: For any database or introspection-related errors.

        :returns: Dictionary containing the model field definitions based on the
            table's structure and metadata.
        :rtype: dict
        """
        connection = connections[self.connection_name]
        if connection is None:
            raise ValueError("Connection %s not found" % self.connection_name)
        current_model = None
        try:
            with connection.cursor() as cursor:
                if hasattr(connection, "introspection"):
                    table_info = connection.introspection.get_table_list(cursor)
                    table_info = {
                        info.name: info
                        for info in table_info
                        if info.name == self.table
                    }
                    if len(table_info) == 0:
                        raise ValueError("Table %s not found" % self.table)
                    try:
                        relations = connection.introspection.get_relations(
                            cursor, self.table
                        )
                    except NotImplementedError:
                        relations = {}
                    try:
                        constraints = connection.introspection.get_constraints(
                            cursor, self.table
                        )
                    except NotImplementedError:
                        constraints = {}
                    if hasattr(connection.introspection, "get_primary_columns"):
                        primary_key_columns = (
                            connection.introspection.get_primary_columns(
                                cursor, self.table
                            )
                        )
                        primary_key_column = (
                            primary_key_columns[0] if primary_key_columns else None
                        )
                    else:
                        primary_key_columns = []
                        primary_key_column = (
                            connection.introspection.get_primary_key_column(
                                cursor, self.table
                            )
                        )

                    unique_columns = [
                        c["columns"][0]
                        for c in constraints.values()
                        if c["unique"] and len(c["columns"]) == 1
                    ]
                    table_description = connection.introspection.get_table_description(
                        cursor, self.table
                    )

                used_column_names = []  # Holds column names used in the table so far
                column_to_field_name = {}  # Maps column names to names of model fields
                current_model = {}
                for row in table_description:
                    comment_notes = (
                        []
                    )  # Holds Field notes, to be displayed in a Python comment.
                    extra_params = {}  # Holds Field parameters such as 'db_column'.
                    column_name = row.name
                    # we do not want to use model relations
                    # is_relation = column_name in relations
                    is_relation = False
                    att_name, params, notes = self.normalize_col_name(
                        column_name, used_column_names, is_relation
                    )
                    extra_params.update(params)
                    comment_notes.extend(notes)

                    used_column_names.append(att_name)
                    column_to_field_name[column_name] = att_name

                    # Add primary_key and unique, if necessary.
                    if column_name == primary_key_column:
                        extra_params["primary_key"] = True
                        if len(primary_key_columns) > 1:
                            comment_notes.append(
                                "The composite primary key (%s) found, that is not "
                                "supported. The first column is selected."
                                % ", ".join(primary_key_columns)
                            )
                    elif column_name in unique_columns:
                        extra_params["unique"] = True

                    field_type, field_params, field_notes = self.get_field_type(
                        connection, row
                    )
                    extra_params.update(field_params)
                    comment_notes.extend(field_notes)

                    field_type += "("

                    if att_name == "id" and extra_params == {"primary_key": True}:
                        if field_type == "AutoField(":
                            continue
                        elif (
                                field_type
                                == connection.features.introspected_field_types["AutoField"]
                                + "("
                        ):
                            comment_notes.append("AutoField?")

                    # Add 'null' and 'blank', if the 'null_ok' flag was present in the
                    # table description.
                    if row.null_ok:  # If it's NULL...
                        extra_params["blank"] = True
                        extra_params["null"] = True

                    field_desc = "%s%s" % (
                        "" if "." in field_type else "models.",
                        field_type,
                    )
                    if field_type.startswith(("ForeignKey(", "OneToOneField(")):
                        field_desc += ", models.DO_NOTHING"

                    # Add comment.
                    if (
                            hasattr(connection.features, "supports_comments")
                            and row.comment
                    ):
                        extra_params["db_comment"] = row.comment
                    # if connection.features.supports_comments and row.comment:
                    #    extra_params["db_comment"] = row.comment

                    if extra_params:
                        if not field_desc.endswith("("):
                            field_desc += ", "
                        field_desc += ", ".join(
                            "%s=%r" % (k, v) for k, v in extra_params.items()
                        )
                    field_desc += ")"
                    if comment_notes:
                        field_desc += "  # " + " ".join(comment_notes)
                    current_model[att_name] = field_desc
        except Exception as e:
            print(e)
            raise e
        return current_model

    @staticmethod
    def normalize_col_name(col_name, used_column_names, is_relation):
        """
        Normalizes a column name to conform to Python's variable naming conventions and addresses potential
        name conflicts or issues with reserved words. Applies transformations to ensure the column name:
        - Is lowercase.
        - Replaces unsuitable characters with underscores.
        - Avoids conflicts with Python keywords and digits at the start of the name.
        - Resolves conflicts with previously used column names.

        :param col_name: The original column name provided from the schema.
        :param used_column_names: A list of previously used column names to avoid naming collisions.
        :param is_relation: A boolean indicating if the column represents a relation (e.g., foreign key).
        :return: A tuple containing:
            - The normalized column name (str).
            - A dictionary (`field_params`) with any relevant information for database configuration.
              Includes the original column name if specific transformations were applied.
            - A list (`field_notes`) containing strings explaining the applied transformations.
        """
        field_params = {}
        field_notes = []

        new_name = col_name.lower()
        if new_name != col_name:
            field_notes.append("Field name made lowercase.")

        if is_relation:
            if new_name.endswith("_id"):
                new_name = new_name.removesuffix("_id")
            else:
                field_params["db_column"] = col_name

        new_name, num_repl = re.subn(r"\W", "_", new_name)
        if num_repl > 0:
            field_notes.append("Field renamed to remove unsuitable characters.")

        if new_name.find(LOOKUP_SEP) >= 0:
            while new_name.find(LOOKUP_SEP) >= 0:
                new_name = new_name.replace(LOOKUP_SEP, "_")
            if col_name.lower().find(LOOKUP_SEP) >= 0:
                # Only add the comment if the double underscore was in the original name
                field_notes.append(
                    "Field renamed because it contained more than one '_' in a row."
                )
        # Commented this because we want to keep the original name regardless of the name given
        # if new_name.startswith("_"):
        #    new_name = "field%s" % new_name
        #    field_notes.append("Field renamed because it started with '_'.")

        if new_name.endswith("_"):
            new_name = "%sfield" % new_name
            field_notes.append("Field renamed because it ended with '_'.")

        if keyword.iskeyword(new_name):
            new_name += "_field"
            field_notes.append("Field renamed because it was a Python reserved word.")

        if new_name[0].isdigit():
            new_name = "number_%s" % new_name
            field_notes.append(
                "Field renamed because it wasn't a valid Python identifier."
            )

        if new_name in used_column_names:
            num = 0
            while "%s_%d" % (new_name, num) in used_column_names:
                num += 1
            new_name = "%s_%d" % (new_name, num)
            field_notes.append("Field renamed because of name conflict.")

        if col_name != new_name and field_notes:
            field_params["db_column"] = col_name

        return new_name, field_params, field_notes

    @staticmethod
    def get_field_type(connection, row):
        """
        Determines the type of a database field based on its description and connection
        introspection, and includes metadata such as parameters and additional notes.

        This function extracts the field type from the database's introspection
        interface and adds corresponding parameters (e.g., `max_length`, `decimal_places`)
        and relevant notes if certain properties are inferred or guessed.

        :param connection: The database connection object used for introspection.
        :type connection: Any
        :param row: An object containing field metadata, such as type code,
            display size, collation, precision, and scale.
        :type row: Any
        :return: A tuple containing the field type, its parameters, and any notes.
        :rtype: tuple[str, dict, list[str]]
        """
        field_params = {}
        field_notes = []

        try:
            field_type = connection.introspection.get_field_type(row.type_code, row)
        except KeyError:
            field_type = "TextField"
            field_notes.append("This field type is a guess.")

        # Add max_length for all CharFields.
        if field_type == "CharField" and row.display_size:
            size = int(row.display_size)
            if size and size > 0:
                field_params["max_length"] = size

        if field_type in {"CharField", "TextField"} and row.collation:
            field_params["db_collation"] = row.collation

        if field_type == "DecimalField":
            if row.precision is None or row.scale is None:
                field_notes.append(
                    "max_digits and decimal_places have been guessed, as this "
                    "database handles decimal fields as float"
                )
                field_params["max_digits"] = (
                    row.precision if row.precision is not None else 10
                )
                field_params["decimal_places"] = (
                    row.scale if row.scale is not None else 5
                )
            else:
                field_params["max_digits"] = row.precision
                field_params["decimal_places"] = row.scale

        return field_type, field_params, field_notes
