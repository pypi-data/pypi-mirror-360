import json
import logging
from typing import cast

try:
    from databricks.sdk import WorkspaceClient
    from databricks.sdk.service.sql import ExecuteStatementRequestOnWaitTimeout
except ImportError:
    WorkspaceClient = None  # type: ignore
    ExecuteStatementRequestOnWaitTimeout = None  # type: ignore
    print("Optional dependency 'databricks' is not installed. Some functionalities may not be available.")

from ..formatters import DictFormatter


class UnityCatalogHandler(logging.Handler):
    """A custom logging handler for Databricks Unity Catalog.

    The handler will by default always send the timestamp and loglevel of the log message.
    """

    def __init__(
        self,
        catalog: str | None = None,
        schema: str | None = None,
        table: str | None = None,
        columns: dict[str, str] | None = None,
        workspace_url: str | None = None,
        warehouse_id: str | None = None,
        column_split_char: str = "|",
        key_value_split_char: str = ":",
        workspace_client: WorkspaceClient | None = None,
        formatter: DictFormatter | None = None,
        **kwargs,  # required to work with the Factory
    ):
        """Initializes a new instance of the DatabricksHandler class.

        Note:
            The handler will reuse the existing authentication from the Azure and Databricks CLI or any
            other spark connection that is already established.

        Args:
            catalog: The name of the catalog to send logs to.
            schema: The name of the schema to send logs to.
            table: The name of the table to send logs to.
            columns: A dictionary of column names and their corresponding data types.
            workspace_url: The URL of the Azure Databricks workspace.
            warehouse_id: The ID of the Databricks warehouse.
            column_split_char: The character used to split columns in the log message. Defaults to "|".
            key_value_split_char: The character used to split keys and values in the log message. Defaults to ":".
            workspace_client: An instance of WorkspaceClient for dependency injection.
            formatter: An instance of DictFormatter for dependency injection.
        """
        self.workspace_url = workspace_url
        self.column_split_char = column_split_char
        self.key_value_split_char = key_value_split_char
        self.catalog = catalog
        self.schema = schema
        self.table = table
        self.warehouse_id = cast(str, warehouse_id)
        if not all([self.catalog, self.schema, self.table, self.warehouse_id, self.workspace_url]):
            raise ValueError(
                "You must provide a workspace_url, warehouse_id, catalog, schema, and table to create a DatabricksHandler."
            )
        self.table_identifier = f"{self.catalog}.{self.schema}.{self.table}"
        self.workspace_client = workspace_client or WorkspaceClient(host=self.workspace_url)
        super().__init__(**kwargs)
        self.setFormatter(
            formatter or DictFormatter(column_split_char=column_split_char, key_value_split_char=key_value_split_char)
        )
        self.ensure_table_exists(columns)

    def ensure_table_exists(self, columns: dict[str, str] | None) -> None:
        """Ensure that the table exists in the catalog.

        This method will create the table in the catalog if it does not already exist.

        Args:
            columns: A dictionary of column names and their corresponding data types

        Raises:
            ValueError: If the columns dictionary is empty.
        """
        if not columns:
            raise ValueError("You must provide a dictionary of columns to create the logging table.")
        columns = {**columns, "timestamp": "timestamp", "level": "string"}
        table_exists = self.workspace_client.tables.exists(self.table_identifier).table_exists is True
        if table_exists is False:
            columns["timestamp"] = "TIMESTAMP"
            columns["level"] = "STRING"
            columns_definition = ", ".join([f"{col_name} {col_type}" for col_name, col_type in columns.items()])

            self.workspace_client.statement_execution.execute_statement(
                statement=f"CREATE TABLE IF NOT EXISTS {self.table_identifier} ({columns_definition})",
                warehouse_id=self.warehouse_id,
                wait_timeout="30s",
            )

    def __eq__(self, other: object) -> bool:
        """Checks if two DatabricksHandler instances are equal.

        Instances are considered equal if they have the same catalog, schema, and table.
        This will prevent the same handler from being added multiple times to a single logger.

        Args:
            other: The other DatabricksHandler instance to compare with.

        Returns:
            True if instances are equal, False otherwise.
        """
        return (
            isinstance(other, UnityCatalogHandler)
            and self.catalog == other.catalog
            and self.schema == other.schema
            and self.table == other.table
        )

    def __hash__(self):
        """Generates a unique hash value for the object.

        This method overrides the built-in `__hash__` method to generate a unique hash value for the object,
        which is particularly useful for using the object in sets or as keys in dictionaries.
        The hash value is computed based on the catalog, schema, and table attributes.
        """
        return hash((self.catalog, self.schema, self.table))

    def _parse_dict_to_sql_insert(self, input_dict: dict) -> str:
        """Generate a SQL INSERT statement from a dictionary.

        Parameters:
            input_dict (dict): A dictionary where keys are column names and values are the data to insert.
        """
        columns = ", ".join(input_dict.keys())
        values = ", ".join(f"'{str(v)}'" for v in input_dict.values())
        split_values = values.split(", ")
        timestamp = split_values[0]
        casted_timestamp = f"to_timestamp({timestamp}, 'yyyy-MM-dd HH:mm:ss,SSS')"
        joined_values = ", ".join([casted_timestamp] + split_values[1:])
        sql_statement = f"INSERT INTO {self.table_identifier} ({columns}) VALUES ({joined_values})"
        return sql_statement

    def emit(self, record: logging.LogRecord) -> None:
        """Put a log record into the Queue.

        Args:
            record (logging.LogRecord): The log record to put into the Queue.
        """
        log_message = self.format(record)
        log_insert_statement = self._parse_dict_to_sql_insert(json.loads(log_message))
        self.workspace_client.statement_execution.execute_statement(
            statement=log_insert_statement,
            warehouse_id=self.warehouse_id,
            on_wait_timeout=ExecuteStatementRequestOnWaitTimeout.CONTINUE,
        )
