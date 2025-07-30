import base64
import hashlib
import hmac
import logging
import os
from datetime import datetime

try:
    import requests
except ImportError:
    requests = None  # type: ignore
    print("Optional dependency 'log_analytics' is not installed. Some functionalities may not be available.")

from cloe_logging.utility.serializer import create_logserializer


class LogAnalyticsHandler(logging.Handler):
    """A custom logging handler for Azure Log Analytics.

    The handler will by default always send the timestamp and loglevel of the log message.

    Attributes:
        METHOD (str): The HTTP method for the requests.
        RESOURCE (str): The resource path for the requests.
        CONTENT_TYPE (str): The content type for the requests.
    """

    METHOD = "POST"
    RESOURCE = "/api/logs"
    CONTENT_TYPE = "application/json; charset=utf-8"

    def __init__(
        self,
        workspace_id: str | None = None,
        shared_key: str | None = None,
        log_type: str | None = None,
        test_connectivity: bool = True,
        column_split_char: str = "|",
        key_value_split_char: str = ":",
        **kwargs,  # required to work with the Factory
    ):
        """Initializes a new instance of the LogAnalyticsHandler class.

        Args:
            workspace_id (str): The workspace ID for Azure Log Analytics.
            shared_key (str): The shared key for Azure Log Analytics.
            log_type (str): The log type for Azure Log Analytics.
            column_split_char (str, optional): The character used to split columns in the log message. Defaults to "|".
            key_value_split_char (str, optional): The character used to split keys and values in the log message.
                                                  Defaults to ":".
            test_connectivity (bool, optional): Whether to test connectivity to Azure Log Analytics when initializing
                                                the handler. Defaults to True.
        """
        self.column_split_char: str = column_split_char
        self.key_value_split_char: str = key_value_split_char
        self.workspace_id: str | None = workspace_id or os.environ.get("LOG_ANALYTICS_WORKSPACE_ID")
        self.shared_key: str | None = shared_key or os.environ.get("LOG_ANALYTICS_WORKSPACE_SHARED_KEY")
        self.log_type: str | None = log_type or os.environ.get("LOG_TYPE")
        if not self.workspace_id or not self.shared_key or not self.log_type:
            raise ValueError(
                "The workspace_id, shared_key, and log_type must be provided or set as environment variables."
            )
        logging.Handler.__init__(self)
        self.session = requests.Session()
        formatter = logging.Formatter("timestamp:%(asctime)s | level: %(levelname)-8s | %(message)s")
        self.setFormatter(formatter)
        self.serializer = create_logserializer()
        self.serializer.column_split_char = self.column_split_char
        self.serializer.key_value_split_char = self.key_value_split_char
        if test_connectivity:
            self.test_connectivity()

    def test_connectivity(self):
        """Checks the connectivity to the Log Analytics workspace without sending a log.

        Raises:
            ValueError: If the connection to Azure Log Analytics fails.
        """

        class FakeRecord(logging.LogRecord):
            """Mock Record to use in the emit method."""

            def __init__(self, msg, level=logging.INFO):
                name = "test"
                pathname = "test_path"
                lineno = 1
                args = ()
                exc_info = None
                super().__init__(
                    name,
                    level,
                    pathname,
                    lineno,
                    msg,
                    args,
                    exc_info,
                    func=None,
                    sinfo=None,
                )
                self.levelname = "INFO"

            def getMessage(self):
                return self.msg

        try:
            self.emit(FakeRecord(msg=f"''{self.key_value_split_char}''"))
        except ValueError as err:
            raise ValueError(f"Failed to connect to Azure Log Analytics: {str(err)}") from err

    def __eq__(self, other):
        """Checks if two LogAnalyticsHandler instances are equal.

        Instances are considered equal if they have the same workspace_id, shared_key, and log_type.
        This will prevent the same handler from being added multiple times to a single logger.

        Args:
            other (LogAnalyticsHandler): The other LogAnalyticsHandler instance to compare with.

        Returns:
            bool: True if instances are equal, False otherwise.
        """
        if isinstance(other, LogAnalyticsHandler):
            return (
                self.workspace_id == other.workspace_id
                and self.shared_key == other.shared_key
                and self.log_type == other.log_type
            )
        return False

    def __hash__(self):
        """Generates a unique hash value for the object.

        This method overrides the built-in `__hash__` method to generate a unique hash value for the object,
        which is particularly useful for using the object in sets or as keys in dictionaries.

        The hash value is computed based on the 'workspace_id', 'shared_key', and 'log_type' attributes of the object.
        """
        return hash((self.workspace_id, self.shared_key, self.log_type))

    def _build_signature(self, date, content_length):
        """Builds the signature for the request.

        Args:
            date (str): The date of the request.
            content_length (int): The length of the content in the request.

        Returns:
            str: The authorization signature for the request.
        """
        x_headers = "x-ms-date:" + date
        string_to_hash = f"{self.METHOD}\n{content_length}\n{self.CONTENT_TYPE}\n{x_headers}\n{self.RESOURCE}"
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
        decoded_key = base64.b64decode(self.shared_key)
        encoded_hash = base64.b64encode(
            hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest(),
        ).decode()
        authorization = f"SharedKey {self.workspace_id}:{encoded_hash}"
        return authorization

    def _make_message_compliant(self, input_string):
        """Encodes the input string as UTF-8 to make it compliant.

        Args:
            input_string (str): The string to be encoded.

        Returns:
            str: The encoded string.
        """
        return str(input_string).encode("utf-8")

    def _get_url(self):
        """Generates the URL for the Azure Log Analytics workspace.

        Returns:
            str: The URL of the Azure Log Analytics workspace.
        """
        uri = f"https://{self.workspace_id}.ods.opinsights.azure.com{self.RESOURCE}?api-version=2016-04-01"
        return uri

    def emit(self, record: logging.LogRecord):
        """Sends the log message to Azure Log Analytics.

        Args:
            record (logging.LogRecord): The record instance with the log message.

        Raises:
            ValueError: If record.msg is not a string, or if failed to send log to Azure Log Analytics.

        Note:
            This method uses the following methods:
            - _parse_string_to_dict to convert the log message to a dictionary.
            - _make_message_compliant to make the log message compliant.
            - _build_signature to build the signature for the request.
            - _get_url to get the URL of the Azure Log Analytics workspace.
        """
        try:
            log_message = self.format(record)
            log_message_dict = self.serializer.serialize(log_message)
            compliant_log_message = self._make_message_compliant(str(log_message_dict))
            content_length = len(compliant_log_message)
            rfc1123date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
            signature = self._build_signature(rfc1123date, content_length)

            headers = {
                "content-type": self.CONTENT_TYPE,
                "Authorization": signature,
                "Log-Type": self.log_type,
                "x-ms-date": rfc1123date,
            }
            response = self.session.post(self._get_url(), data=compliant_log_message, headers=headers, timeout=30)
            response.raise_for_status()
        except AttributeError as exc:
            raise ValueError(exc) from exc
        except requests.exceptions.RequestException as exc:
            raise ValueError(f"Failed to send log to Azure Log Analytics: {exc}") from exc
        except Exception as exc:
            raise ValueError(exc) from exc
