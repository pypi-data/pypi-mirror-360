import logging

logger = logging.getLogger('pytcube')

LOG_FORMAT = '%(asctime)s|%(levelname)-8s|%(message)-100s|%(filename)s:%(lineno)d@%(funcName)s()'

def setup_logging(
    app_logger: logging.Logger,
) -> bool:
    """Set up logging for the specified logger."""

    app_logger.setLevel(logging.DEBUG)
    app_logger.handlers = []
    handler = logging.StreamHandler()
    formatter = logging.Formatter(fmt=LOG_FORMAT)
    handler.setFormatter(formatter)
    app_logger.addHandler(handler)

    return True
