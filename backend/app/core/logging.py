import logging
import sys


def setup_logger(name: str = "lexguard") -> logging.Logger:
    """
    Configures an enterprise-grade structured logger for LexGuard.
    Crucial Privacy Guideline:
    Never log raw document contents, legal text, or sensitive client information.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.propagate = False
    return logger


logger = setup_logger()
