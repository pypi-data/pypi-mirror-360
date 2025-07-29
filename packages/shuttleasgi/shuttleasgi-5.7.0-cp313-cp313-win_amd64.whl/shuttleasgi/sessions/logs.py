import logging


def get_logger():
    """
    Returns a "shuttleasgi.sessions" logger.
    """
    logger = logging.getLogger("shuttleasgi.sessions")
    logger.setLevel(logging.INFO)
    return logger
