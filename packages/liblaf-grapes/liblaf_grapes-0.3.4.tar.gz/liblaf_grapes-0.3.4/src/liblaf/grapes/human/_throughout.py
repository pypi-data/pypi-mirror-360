from liblaf.grapes import deps

with deps.optional_imports(extra="duration"):
    import about_time


def human_throughout(value: float, unit: str = "", prec: int | None = None) -> str:
    """Convert a numeric value representing throughput into a human-readable string.

    Args:
        value: The numeric value of the throughput.
        unit: The unit of the throughput (e.g., "it/s", "B/s").
        prec: The precision of the human-readable output. If `None`, default precision is used.

    Returns:
        A human-readable string representing the throughput.
    """
    # TODO: remove dependency on `about-time`
    ht = about_time.HumanThroughput(value, unit)
    return ht.as_human(prec)
