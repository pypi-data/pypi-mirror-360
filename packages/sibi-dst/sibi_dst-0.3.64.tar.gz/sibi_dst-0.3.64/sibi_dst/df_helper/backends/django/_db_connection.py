from typing import Any

from pydantic import BaseModel, model_validator

from ._sql_model_builder import DjangoSqlModelBuilder


class DjangoConnectionConfig(BaseModel):
    """
    Represents a configuration for establishing a Django database connection.

    This class is used for defining the configurations necessary to establish a Django
    database connection. It supports dynamic model generation if the model is not
    provided explicitly. It also validates the connection configuration to ensure it
    is properly set up before being used.

    :ivar live: Indicates whether the connection is live. Automatically set to False if
        a table is provided without a pre-built model.
    :type live: bool
    :ivar connection_name: The name of the database connection to use. This is a mandatory
        parameter and must be provided.
    :type connection_name: str
    :ivar table: The name of the database table to use. Required for dynamic model
        generation when no model is provided.
    :type table: str
    :ivar model: The Django model that represents the database table. If not provided,
        this can be generated dynamically by using the table name.
    :type model: Any
    """
    live: bool = False
    connection_name: str = None
    table: str = None
    model: Any = None

    @model_validator(mode="after")
    def check_model(self):
        """
        Validates and modifies the instance based on the provided attributes and conditions.
        This method ensures that all required parameters are populated and consistent, and it
        dynamically builds a model if necessary. The method also ensures the connection is
        validated after the model preparation process.

        :raises ValueError: If `connection_name` is not provided.
        :raises ValueError: If `table` name is not specified when building the model dynamically.
        :raises ValueError: If there are errors during the dynamic model-building process.
        :raises ValueError: If `validate_connection` fails due to invalid configuration.
        :return: The validated and potentially mutated instance.
        """
        # connection_name is mandatory
        if self.connection_name is None:
            raise ValueError("Connection name must be specified")

        # If table is provided, enforce live=False
        if self.table:
            self.live = False

        # If model is not provided, build it dynamically
        if not self.model:
            if not self.table:
                raise ValueError("Table name must be specified to build the model")
            try:
                self.model = DjangoSqlModelBuilder(
                    connection_name=self.connection_name, table=self.table
                ).build_model()
            except Exception as e:
                raise ValueError(f"Failed to build model: {e}")
        else:
            self.live = True
        # Validate the connection after building the model
        self.validate_connection()
        return self

    def validate_connection(self):
        """
        Ensures the database connection is valid by performing a simple
        query. Raises a ValueError if the connection is broken or if any
        other exception occurs during the query.

        :raises ValueError: If the connection to the database cannot be
            established or if the query fails.
        """
        try:
            # Perform a simple query to test the connection
            self.model.objects.using(self.connection_name).exists()
        except Exception as e:
            raise ValueError(
                f"Failed to connect to the database '{self.connection_name}': {e}"
            )
