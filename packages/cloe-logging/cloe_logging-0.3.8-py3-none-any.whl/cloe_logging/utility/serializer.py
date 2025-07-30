from abc import ABC, abstractmethod


class LogSerializer(ABC):
    """
    Used to serialize log records into various formats.

    Currently supported formats:
    -   'dict'
    """

    @abstractmethod
    def serialize(self, log_record):
        """
        Serializes a log record into the specified format.

        Args:
            log_record: The log record to be serialized.
            format: The format to serialize the log record into. Currently supports "dict".

        Returns:
            dict: The serialized log record in dictionary format.

        Raises:
            NotImplementedError: If the specified format is not supported.
        """
        pass


class DictSerializer(LogSerializer):
    def __init__(
        self,
        column_split_char: str = "|",
        key_value_split_char: str = ":",
    ):
        self.column_split_char: str = column_split_char
        self.key_value_split_char: str = key_value_split_char

    def serialize(self, log_record):
        """
        Converts a formatted string to a dictionary.

        Parameters:
            log_record: The string to be converted to a dictionary.
            column_split_char: The character that separates different key-value pairs in the string (default is "|").
            key_value_split_char: The character that separates keys from values in the string (default is ":").

        Returns:
            dict: The converted dictionary.

        Raises:
            ValueError: If the log_record is not a string, or if any part of the log_record does not contain the key_value_split_char.
        """
        if not isinstance(log_record, str):
            raise ValueError("record must be a string.")
        parts = [part.strip() for part in log_record.split(self.column_split_char)]
        result_dict = {}

        for part in parts:
            try:
                key, value = part.split(self.key_value_split_char, maxsplit=1)
            except ValueError as exc:
                raise ValueError(
                    f"Each part of the record must contain the key_value_split_char. Error: {str(exc)}",
                ) from exc
            result_dict[key.strip()] = value.strip()
        return result_dict


def create_logserializer(format="dict"):
    logserializers = {
        "dict": DictSerializer,
    }
    try:
        serializer = logserializers[format]()
    except KeyError as exc:
        raise NotImplementedError(
            f"The selected format is not supported yet. Error: {str(exc)}",
        ) from exc
    return serializer
