# This module is responsible for taking a string, then finding
# format braces "{abc}" or "{{abc}}" in them.

import re
from string import Formatter

fmt = Formatter()


def split_single(text: str):
    """
    Parser for single brace formatting, i.e.:
    ```plain
    The value of 1 + 2 is {1 + 2}
    ```
    """
    # For a string like "hello{foo}bye", this will iterate as follows:
    #   ("hello", "foo")
    #   ("bye", None)
    # The first element is actual literal text.
    # The second element is the format '{...}' that comes after the literal text
    # If the end of string is reached, the second element is None
    for prefix, key, _, _ in fmt.parse(text):
        yield prefix, key


def split_double(text: str):
    """
    Parser for double brace formatting, i.e.:
    ```plain
    The value of 1 + 2 is {{1 + 2}}
    ```
    """
    last_match_end = 0
    for match in re.finditer(r"{{([^{}]+)}}", text):
        prefix = text[last_match_end : match.start()]
        yield prefix, match.group(1)
        last_match_end = match.end()

    yield text[last_match_end:], None
