import re
from string import Formatter

from . import macros
from .presetcolors import ColorPresetConfig

fmt = Formatter()


def split(text):
    # For a string like "hello{foo}bye", this will iterate as follows:
    #   ("hello", "foo")
    #   ("bye", None)
    # The first element is actual literal text.
    # The second element is the format '{...}' that comes after the literal text
    # If the end of string is reached, the second element is None
    for prefix, key, _, _ in fmt.parse(text):
        yield prefix, key


def parse(string, presetcolors: ColorPresetConfig = None):
    result = []
    for prefix, key in split(string):
        result.append(prefix)
        if key is None:
            continue

        if presetcolors is not None:
            if match := re.fullmatch(r"p\(([^)]+)\)", key):
                presetname = match.group(1).strip()
                key = presetcolors.get_color(presetname)

        key = str(parse_single(key))
        result.append(key)
    return "".join(result)


def parse_single(string):
    string = string.strip()
    if re.fullmatch(r"0x[a-fA-F\d]+", string):
        return macros.hexcolor(string)
    elif match := re.fullmatch(r"rgb\(([ \d]+),([ \d]+),([ \d]+)\)", string):
        return macros.rgb(
            int(match.group(1)),
            int(match.group(2)),
            int(match.group(3)),
        )
    elif match := re.fullmatch(r"nrgb\(([ \d]+),([ \d]+),([ \d]+)\)", string):
        return macros.nrgb(
            int(match.group(1)),
            int(match.group(2)),
            int(match.group(3)),
        )
    elif match := re.fullmatch(r"blend\(([ \w]+),([ \d\.]+)\)", string):
        return macros.blend(
            match.group(1).strip(),
            float(match.group(2)),
        )
    # elif match := re.fullmatch(r"rgba\(([ \d]+),([ \d]+),([ \d]+),([ \d]+)\)", string):
    #     return macros.rgba(
    #         int(match.group(1)),
    #         int(match.group(2)),
    #         int(match.group(3)),
    #         int(match.group(4)),
    #     )
    else:
        raise ValueError(f"Unable to parse format string: {string!r}")
