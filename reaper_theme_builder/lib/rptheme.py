from configparser import ConfigParser
from io import StringIO

from . import formatter
from .presetcolors import ColorPresetConfig


def from_paths(
    paths: list[str],
    extra_configs: dict[str, dict[str, str]] = None,
    presetcolors: ColorPresetConfig = None,
):
    if extra_configs is None:
        extra_configs = {}

    config = ConfigParser()

    for p in paths:
        config.read(p)

    # add extra configs
    for section in extra_configs:
        if section not in config:
            config[section] = {}
        for key in extra_configs[section]:
            config[section][key] = extra_configs[section][key]

    # apply macros
    for section in config:
        for key in config[section]:
            config[section][key] = formatter.parse(
                config[section][key], presetcolors=presetcolors
            )

    with StringIO() as f:
        config.write(f, space_around_delimiters=False)
        f.seek(0)
        content = f.read()

    return content
