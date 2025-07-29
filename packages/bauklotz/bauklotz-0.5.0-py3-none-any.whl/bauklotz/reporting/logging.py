from typing import Protocol

from loguru import logger

from bauklotz.reporting.types import JSONType


class BauklotzLogger(Protocol):
    """
    Protocol for a logging interface.

    Defines an interface for a logging system that supports multiple
    logging levels such as info, debug, warning, error, and critical.
    Each method allows for a message accompanied by additional
    contextual data provided as keyword arguments.

    Methods of this logger can be implemented by any concrete class
    according to the defined protocol. The primary purpose is to
    standardize logging mechanisms and ensure consistency across
    components.

    Attributes:
        None
    """
    def info(self, message: str, **extra: JSONType) -> None:
        """
        Logs a message with an INFO level.

        This method logs the provided message and any additional arguments
        at the INFO logging level. Designed for general information messages.

        Args:
            message: Message string to log.
            **extra: Additional parameters to include with the log entry.
        """

    def debug(self, message: str, **extra: JSONType) -> None:
        """
        Logs a debug message with optional additional context.

        The method sends a debug-level message to the logging system. Additional
        key-value pairs can be provided to augment the log entry with contextual
        information.

        Args:
            message: The debug message to be logged.
            **extra: Arbitrary keyword arguments to include as additional context
                in the log record.

        """

    def warning(self, message: str, **extra: JSONType) -> None:
        """
        Logs a warning message with optional additional context to the logging system.

        The warning method is used to log messages at the warning level. It accepts a
        message string and an optional set of key-value pairs for additional contextual
        data, which should conform to JSON serializable types. This can be used to
        facilitate tracking, grouping, or filtering logs based on additional metadata.

        Args:
            message: A string containing the warning message to be logged.
            **extra: Additional context in the form of key-value pairs to be included
                alongside the log, which must be compatible with JSON serialization.

        """

    def error(self, message: str, **extra: JSONType) -> None:
        """
        Logs an error-level message.

        The function accepts a mandatory message that specifies the content of the log and
        any additional context that is necessary to accompany the log entry as key-value pairs.

        Args:
            message: The error message to be logged.
            **extra: Additional context parameters provided as key-value pairs to supplement
                the log entry.
        """

    def critical(self, message: str, **extra: JSONType) -> None:
        """
        Logs a critical message to the appropriate logger system. This method is used to
        log severe messages that indicate a critical problem that may cause program failure.
        Extra keyword arguments can be provided to include additional context.

        Args:
            message: The critical message to log.
            **extra: Additional context or extra data for the log message.
        """


class NoopLogger(BauklotzLogger):
    """
    A logger class that performs no operations.

    This class is used as a placeholder logger that provides basic logging
    method stubs (info, debug, warning, error, critical). All methods
    are implemented as no-op, meaning they do not perform any operations
    or produce any output. Useful for scenarios where logging functionality
    is optional or not required.
    """
    def info(self, message: str, **extra: JSONType) -> None: pass
    def debug(self, message: str, **extra: JSONType) -> None: pass
    def warning(self, message: str, **extra: JSONType) -> None: pass
    def error(self, message: str, **extra: JSONType) -> None: pass
    def critical(self, message: str, **extra: JSONType) -> None: pass


DEFAULT_LOGGER: BauklotzLogger = logger