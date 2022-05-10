from string import Formatter
import re

from lib import macros

fmt = Formatter()


def split(text):
    for prefix, key, _, _ in fmt.parse(text):
        yield prefix, key


def parse(string):
    result = []
    for prefix, key in split(string):
        result.append(prefix)
        if key is not None:
            result.append(str(parse_single(key)))
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
