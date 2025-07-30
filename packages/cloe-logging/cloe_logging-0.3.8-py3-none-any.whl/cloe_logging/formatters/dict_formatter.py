import logging
import json


class DictFormatter(logging.Formatter):
    def __init__(
        self,
        column_split_char: str = "|",
        key_value_split_char: str = ":",
        fmt=None,
        datefmt=None,
        style="%",
        skip_missing_key_value_split_char: bool = False,
    ):
        super().__init__(fmt, datefmt, style)
        self.column_split_char: str = column_split_char
        self.key_value_split_char: str = key_value_split_char
        self.skip_missing_key_value_split_char: bool = skip_missing_key_value_split_char

    def format(self, record):
        """
        Converts a formatted string to a dictionary.

        Parameters:
            record: The log record to be converted to a dictionary.

        Returns:
            str: The converted dictionary as a JSON string.
        """
        log_record = super().format(record)
        parts = [part.strip() for part in log_record.split(self.column_split_char)]
        result_dict = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
        }
        for part in parts:
            if self.key_value_split_char in part:
                key, value = part.split(self.key_value_split_char, maxsplit=1)
                result_dict[key.strip()] = value.strip()
            else:
                if self.skip_missing_key_value_split_char:
                    continue
                raise ValueError(f"Each part of the record must contain the key_value_split_char. Part: {part}")
        return json.dumps(result_dict)
