from collections.abc import Generator


def strip_comments(
    text: str,
    comments: str = "#",
    *,
    strip: bool = True,
    strip_empty_lines: bool = True,
) -> Generator[str]:
    """Remove comments and optionally strip whitespace and empty lines from the given text.

    Args:
        text: The input text from which to remove comments.
        comments: The comment delimiter.
        strip: Whether to strip leading and trailing whitespace from each line.
        strip_empty_lines: Whether to remove empty lines from the output.

    Yields:
        Lines of text with comments removed and optionally stripped of whitespace and empty lines.
    """
    for raw_line in text.splitlines():
        line: str = raw_line.split(comments, 1)[0]
        if strip:
            line = line.strip()
        if strip_empty_lines and not line:
            continue
        yield line
