from configparser import ConfigParser
from io import StringIO


def from_paths(paths: list[str]):
    """Load multiple *.ReaperTheme files and combine them into a single file"""
    config = ConfigParser()

    for p in paths:
        config.read(p)

    with StringIO() as f:
        config.write(f, space_around_delimiters=False)
        f.seek(0)
        content = f.read()

    return content
