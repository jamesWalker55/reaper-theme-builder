from io import StringIO
import formatter
from configparser import ConfigParser


def from_paths(paths: list[str]):
    config = ConfigParser()

    for p in paths:
        config.read(p)

    # apply macros
    for section in config:
        for key in config[section]:
            config[section][key] = formatter.parse(config[section][key])

    with StringIO() as f:
        config.write(f, space_around_delimiters=False)
        f.seek(0)
        content = f.read()

    return content
