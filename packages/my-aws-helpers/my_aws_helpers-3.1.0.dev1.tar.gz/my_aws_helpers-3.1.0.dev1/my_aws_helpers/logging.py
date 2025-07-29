import logging
import os


def select_powertools_logger(service_name: str) -> logging.Logger:
    """
    Returns the powertools logger if it can be found,
    Returns a Logger with name = service_name if powertools logger is not found
    """
    existing_loggers = [name for name in logging.root.manager.loggerDict]
    powertools_service_name = os.environ.get("POWERTOOLS_SERVICE_NAME")
    if powertools_service_name is not None:
        logger = (
            logging.getLogger(powertools_service_name)
            if powertools_service_name in existing_loggers
            else None
        )
        if logger:
            return logger
    return logging.getLogger(service_name)
