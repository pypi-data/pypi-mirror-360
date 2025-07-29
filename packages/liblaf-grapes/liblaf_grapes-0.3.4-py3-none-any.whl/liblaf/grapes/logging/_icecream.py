from loguru import logger

from liblaf.grapes import deps


def init_icecream() -> None:
    if not deps.has_module("icecream"):
        return
    from icecream import ic

    ic.configureOutput(prefix="", outputFunction=icecream_output_function)


def icecream_output_function(s: str) -> None:
    logger.opt(depth=2).log("ICECREAM", s)
