import logging
from collections.abc import Callable

from cloe_logging.handlers import UnityCatalogHandler, SnowflakeHandler, LogAnalyticsHandler


class LoggerFactory:
    DEFAULT_COLUMN_SPLIT_CHAR = "|"
    DEFAULT_KEY_VALUE_SPLIT_CHAR = ":"

    @staticmethod
    def get_logger(
        handler_types: str | list[str],
        logger_name: str = __name__,
        logging_level: int = logging.INFO,
        log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        **kwargs,
    ) -> logging.Logger:
        """Creates a logger with the specified handler types.

        Args:
            handler_types: The type of handler to use for the logger.
            logger_name: The name of the logger.
            logging_level: The logging level for the logger.
            log_format: The format of the log messages.
            kwargs: Additional arguments to pass to the handler.

        Note:
            Supported handler types are "console", "file", "unity_catalog", "snowflake", and "log_analytics".

        Returns:
            The logger with the specified handler types.
        """
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging_level)
        if isinstance(handler_types, str):
            handler_types = [handler_types]

        for handler_type in handler_types:
            handler = LoggerFactory.get_handler(handler_type, log_format, **kwargs)
            LoggerFactory.add_handler_if_not_exists(logger, handler)
        return logger

    @staticmethod
    def get_handler(
        handler_type: str,
        log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        **kwargs,
    ) -> logging.Handler:
        HANDLER_FUNCTIONS: dict[str, Callable] = {
            "console": LoggerFactory.get_console_handler,
            "file": LoggerFactory.get_file_handler,
            "unity_catalog": LoggerFactory.get_unity_catalog_handler,
            "snowflake": LoggerFactory.get_snowflake_handler,
            "log_analytics": LoggerFactory.get_log_analytics_handler,
        }
        handler = HANDLER_FUNCTIONS[handler_type](**kwargs, log_format=log_format)
        return handler

    @staticmethod
    def get_console_handler(log_format: str, **kwargs) -> logging.Handler:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(log_format))
        return handler

    @staticmethod
    def get_file_handler(
        log_format: str,
        filename: str | None = None,
        mode: str = "a",
        encoding: str | None = None,
        delay: bool = False,
        **kwargs,
    ) -> logging.Handler:
        if filename is None:
            raise ValueError("filename is required for file logger")
        handler = logging.FileHandler(filename, mode, encoding, delay)
        handler.setFormatter(logging.Formatter(log_format))
        return handler

    @classmethod
    def get_unity_catalog_handler(
        cls,
        uc_table_name: str,
        uc_catalog_name: str,
        uc_schema_name: str,
        uc_table_columns: dict[str, str],
        workspace_url: str,
        warehouse_id: str,
        column_split_char: str = DEFAULT_COLUMN_SPLIT_CHAR,
        key_value_split_char: str = DEFAULT_KEY_VALUE_SPLIT_CHAR,
        **kwargs,
    ) -> logging.Handler:
        return UnityCatalogHandler(
            catalog=uc_catalog_name,
            schema=uc_schema_name,
            table=uc_table_name,
            columns=uc_table_columns,
            workspace_url=workspace_url,
            warehouse_id=warehouse_id,
            column_split_char=column_split_char,
            key_value_split_char=key_value_split_char,
        )

    @classmethod
    def get_snowflake_handler(
        cls,
        target_db: str,
        target_schema: str,
        target_table: str,
        column_split_char: str = DEFAULT_COLUMN_SPLIT_CHAR,
        key_value_split_char: str = DEFAULT_KEY_VALUE_SPLIT_CHAR,
        **kwargs,
    ) -> logging.Handler:
        return SnowflakeHandler(
            target_db=target_db,
            target_schema=target_schema,
            target_table=target_table,
            column_split_char=column_split_char,
            key_value_split_char=key_value_split_char,
        )

    @classmethod
    def get_log_analytics_handler(
        cls,
        workspace_id: str,
        shared_key: str,
        log_type: str,
        test_connectivity: bool,
        column_split_char: str = DEFAULT_COLUMN_SPLIT_CHAR,
        key_value_split_char: str = DEFAULT_KEY_VALUE_SPLIT_CHAR,
        **kwargs,
    ) -> logging.Handler:
        return LogAnalyticsHandler(
            workspace_id=workspace_id,
            shared_key=shared_key,
            log_type=log_type,
            test_connectivity=test_connectivity,
            column_split_char=column_split_char,
            key_value_split_char=key_value_split_char,
        )

    @staticmethod
    def add_handler_if_not_exists(logger: logging.Logger, handler: logging.Handler) -> logging.Logger:
        """Adds a handler to the logger if it does not already exist.

        Args:
            logger: The logger to add the handler to.
            handler: The handler to add to the logger.

        Returns:
            The logger with the handler added.
        """
        if len(logger.handlers) > 0:
            if not any([isinstance(h, handler.__class__) for h in logger.handlers]):
                logger.addHandler(handler)
        else:
            logger.addHandler(handler)
        return logger
