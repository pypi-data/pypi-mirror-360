import logging
import logging.handlers


def athena_logger(logger_name: str):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.CRITICAL)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "[%(name)s][%(asctime)s] %(levelname)s in %(funcName)s: %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger
