import logging


def clear_handlers() -> None:
    for logger in logging.root.manager.loggerDict.values():
        if isinstance(logger, logging.PlaceHolder):
            continue
        logger.handlers.clear()
        logger.propagate = True
