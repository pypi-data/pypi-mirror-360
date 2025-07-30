import logging
import os

try:
    from cloe_util_snowflake_connector.connection_parameters import ConnectionParameters
    from cloe_util_snowflake_connector.snowflake_interface import SnowflakeInterface
except ImportError:
    ConnectionParameters = None  # type: ignore
    SnowflakeInterface = None  # type: ignore
    print("Optional dependency 'snowflake' is not installed. Some functionalities may not be available.")
from cloe_logging.utility.serializer import create_logserializer


class SnowflakeHandler(logging.Handler):
    """A custom logging handler for Snowflake.

    The handler will by default always send the timestamp and loglevel of the log message.
    """

    def __init__(
        self,
        target_db: str = "",
        target_schema: str = "",
        target_table: str = "",
        column_split_char: str = "|",
        key_value_split_char: str = ":",
        **kwargs,  # required to work with the Factory
    ):
        """Initializes a new instance of the SnowflakeHandler class.

        Args:
            target_db: The name of the Database to send logs to.
            target_schema: the name of the table to send logs to.
            target_table: the name of the schema to send logs to.
            column_split_char (str, optional): The character used to split columns in the log message. Defaults to "|".
            key_value_split_char (str, optional): The character used to split keys and values in the log message.
                                                  Defaults to ":".
        """
        self.column_split_char: str = column_split_char
        self.key_value_split_char: str = key_value_split_char
        self.target_db: str = os.environ.get("CLOE_SNOWFLAKE_DATABASE", target_db)
        self.target_schema: str = os.environ.get("CLOE_SNOWFLAKE_SCHEMA", target_schema)
        self.target_table: str = os.environ.get("CLOE_SNOWFLAKE_TABLE", target_table)
        logging.Handler.__init__(self)
        self.connection = self._get_snowflake_connection()
        formatter = logging.Formatter("timestamp:%(asctime)s | level: %(levelname)-8s | %(message)s")
        self.setFormatter(formatter)
        self.serializer = create_logserializer()

    def __eq__(self, other):
        """Checks if two SnowflakeHandler instances are equal.

        Instances are considered equal if they have the same workspace_id, shared_key, and log_type.
        This will prevent the same handler from being added multiple times to a single logger.

        Args:
            other (SnowflakeHandler): The other SnowflakeHandler instance to compare with.

        Returns:
            bool: True if instances are equal, False otherwise.
        """
        if isinstance(other, SnowflakeHandler):
            return (
                self.target_db == other.target_db
                and self.target_schema == other.target_schema
                and self.target_table == other.target_table
            )
        return False

    def __hash__(self):
        """Generates a unique hash value for the object.

        This method overrides the built-in `__hash__` method to generate a unique hash value for the object,
        which is particularly useful for using the object in sets or as keys in dictionaries.

        The hash value is computed based on the target_db, target_schema, and target_table attributes.
        """
        return hash((self.target_db, self.target_schema, self.target_table))

    def _get_snowflake_connection(self) -> SnowflakeInterface:
        conn_params = ConnectionParameters.init_from_env_variables()
        snowflake_conn = SnowflakeInterface(conn_params)
        return snowflake_conn

    def _parse_dict_to_sql_insert(self, input_dict: dict) -> str:
        """
        Generate a SQL INSERT statement from a dictionary.

        Parameters:
            table_name (str): The name of the table to insert into.
            data (dict): A dictionary where keys are column names and values are the data to insert.

        Returns:
            str: A SQL INSERT statement as a string.
        """
        columns = ", ".join(input_dict.keys())
        values = ", ".join(f"'{str(v)}'" for v in input_dict.values())
        sql_statement = (
            f"INSERT INTO {self.target_db}.{self.target_schema}.{self.target_table} ({columns}) VALUES ({values})"
        )

        return sql_statement

    def emit(self, record: logging.LogRecord):
        """Sends the log message to Snowflake.

        Args:
            record (logging.LogRecord): The record instance with the log message.

        Raises:
            ValueError: If record.msg is not a string, or if failed to send log to Snowflake.

        """
        try:
            log_message = self.format(record)
            log_message_dict = self.serializer.serialize(log_message)
            log_insert_statement = self._parse_dict_to_sql_insert(log_message_dict)
            self.connection.run_one_with_return(log_insert_statement)
        except Exception as exc:
            raise ValueError(exc) from exc
