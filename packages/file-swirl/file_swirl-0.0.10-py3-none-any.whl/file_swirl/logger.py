# https://pypi.org/project/colorlog/
import logging
import logging.config
from pathlib import Path

# Base configurations
_LOG_LEVEL = "DEBUG"  # Set your default log level
LOG_PATH = Path("./logs")  # Replace with your actual log directory
LOG_PATH.mkdir(parents=True, exist_ok=True)  # Ensure the log directory exists

# Logger configuration
def get_dict_logger(name: str, file_name: str = None) -> logging.Logger:
    """
    Creates a logger with console and file handlers based on a dictionary configuration.

    :param name: Name of the logger.
    :param file_name: Name of the log file (within the LOG_PATH directory).
    :return: Configured logger instance.
    """

    if file_name is None:
        file_name = f"{name}.log"

    log_file_path = LOG_PATH / file_name

    # Define the logger configuration as a dictionary
    logger_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "file": {
                "format": (
                    "%(asctime)s [%(levelname)-6s] (%(module)s.%(funcName)s : %(lineno)d) %(message)s"
                ),
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "console": {
                "()": "colorlog.ColoredFormatter",  # Special syntax for external class
                "format": (
                    "%(log_color)s%(asctime)s [%(levelname)-6s] (%(module)s.%(funcName)s : %(lineno)d) %(message)s"
                ),
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "log_colors": {
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "bold_red",
                },
            },
        },
        "handlers": {
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": _LOG_LEVEL,
                "formatter": "file",
                "filename": str(log_file_path),
                "maxBytes": 1024 * 1024 * 5,  # 5MB
                "backupCount": 5,
            },
            "console": {
                "class": "logging.StreamHandler",
                "level": _LOG_LEVEL,
                "formatter": "console",
            },
        },
        "loggers": {
            name: {
                "handlers": ["file", "console"],
                "level": _LOG_LEVEL,
                "propagate": False,
            },
        },
    }

    # Apply the logging configuration
    logging.config.dictConfig(logger_config)

    # Return the configured logger
    return logging.getLogger(name)


if __name__ == "__main__":
    background_logger = get_dict_logger("test_logger")

    background_logger.debug("DEBUG COLOR")
    background_logger.info("This is a log message for the DC logger.")
    background_logger.warning("WARNING")
    background_logger.error("ERROR")
    background_logger.critical("CRITICAL")
