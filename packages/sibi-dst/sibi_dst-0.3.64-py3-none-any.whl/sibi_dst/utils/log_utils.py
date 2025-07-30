import logging
import os
import sys
import time
from typing import Optional


class Logger:
    """
    Handles the creation, setup, and management of logging functionalities.

    This class facilitates logging by creating and managing a logger instance with
    customizable logging directory, name, and file. It ensures logs from a script
    are stored in a well-defined directory and file, and provides various logging
    methods for different log levels. The logger automatically formats and handles
    log messages. Additionally, this class provides a class method to initialize a
    logger with default behaviors.

    :ivar log_dir: Path to the directory where log files are stored.
    :type log_dir: str
    :ivar logger_name: Name of the logger instance.
    :type logger_name: str
    :ivar log_file: Base name of the log file.
    :type log_file: str
    :ivar logger: The initialized logger instance used for logging messages.
    :type logger: logging.Logger
    """

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    def __init__(self, log_dir: str, logger_name: str, log_file: str, log_level: int = logging.DEBUG):
        """
        Initialize the Logger instance.

        :param log_dir: Directory where logs are stored.
        :param logger_name: Name of the logger instance.
        :param log_file: Base name of the log file.
        :param log_level: Logging level (defaults to DEBUG).
        """
        self.log_dir = log_dir
        self.logger_name = logger_name
        self.log_file = log_file
        self.log_level = log_level
        self.logger = None

        self._setup()

    def _setup(self):
        """Set up the logger with file and console handlers."""
        # Ensure the log directory exists
        os.makedirs(self.log_dir, exist_ok=True)

        # Get the name of the calling script
        calling_script = os.path.splitext(os.path.basename(sys.argv[0]))[0]

        # Create a log file path
        log_file_path = os.path.join(self.log_dir, f"{self.log_file}_{calling_script}.log")

        # Delete the existing log file if it exists
        if os.path.exists(log_file_path):
            os.remove(log_file_path)

        # Create a logger
        self.logger = logging.getLogger(self.logger_name)
        self.logger.setLevel(self.log_level)

        # Create a formatter
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        formatter.converter = time.localtime  # << Set local time explicitly

        # Create a file handler
        file_handler = logging.FileHandler(log_file_path, delay=True)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Create a console handler (optional)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    @classmethod
    def default_logger(
            cls,
            log_dir: str = './logs/',
            logger_name: Optional[str] = None,
            log_file: Optional[str] = None,
            log_level: int = logging.INFO
    ) -> 'Logger':
        """
        Class-level method to create a default logger with generic parameters.

        :param log_dir: Directory where logs are stored (defaults to './logs/').
        :param logger_name: Name of the logger (defaults to __name__).
        :param log_file: Name of the log file (defaults to logger_name).
        :param log_level: Logging level (defaults to INFO).
        :return: Instance of Logger.
        """
        logger_name = logger_name or __name__
        log_file = log_file or logger_name
        return cls(log_dir=log_dir, logger_name=logger_name, log_file=log_file, log_level=log_level)

    def set_level(self, level: int):
        """
        Set the logging level for the logger.

        :param level: Logging level (e.g., logging.DEBUG, logging.INFO).
        """
        self.logger.setLevel(level)

    def debug(self, msg: str, *args, **kwargs):
        """Log a debug message."""
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        """Log an info message."""
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        """Log a warning message."""
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        """
        Log an error message.

        To log exception information, use the `exc_info=True` keyword argument.
        """
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        """Log a critical message."""
        self.logger.critical(msg, *args, **kwargs)
