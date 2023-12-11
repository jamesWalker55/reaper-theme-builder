from typing import Callable

FUNCTIONS = {}


def register_func(func: Callable):
    FUNCTIONS[func.__name__] = func
    return func


@register_func
def rgb(r, g, b):
    return (b << 16) + (g << 8) + r


@register_func
def hex(*args: int):
    result = 0
    for i in args:
        assert isinstance(i, int)
        assert 0x00 <= i <= 0xFF
        result = (result << 8) + i
    return result


@register_func
def arr(val: int):
    """
    Given a hex number like 0x112233, split it into bytes, then
    return a space-separated string of those numbers in decimal.

    i.e. The above number will return "17 34 51"
    """
    result = []
    while val > 0:
        # split the number into the last 8 bits and the rest
        remainder = val & 0xFF
        val = val >> 8

        result.append(remainder)

    result.reverse()

    return " ".join(str(i) for i in result)


@register_func
def set(
    target: str,
    x: str | None = None,
    y: str | None = None,
    w: str | None = None,
    h: str | None = None,
    ls: str | None = None,
    ts: str | None = None,
    rs: str | None = None,
    bs: str | None = None,
    condition: str | None = None,
    add: str | None = None,
    sub: str | None = None,
    _else: str | None = None,
):
    """
    This generates `set ...` code for rtconfig.txt. This is to overcome WALTER's
    terrible syntax and provide better coding comfort.
    """
    temp_variables: dict[str, str] = {}

    def resolve(temp_var_name: str, value: str | None):
        """
        This resolves any arbitrary expression to a single value, by creating temporary
        variables with `temp_variables`.

        - Simple values like numbers are returned as-is
        - Empty values are assumed to be left alone so we return '.'
        - Complex values cannot be used in a coordinate list, so we assign a temporary
          variable and return that instead
        """
        if value is None:
            # use existing value syntax "."
            return "."

        value = value.strip()
        if len(value.split()) > 1:
            # this is an expression with multiple terms
            # must assign to external variable before setting target
            temp_var_name = f"__{temp_var_name}"
            temp_variables[temp_var_name] = value
            return temp_var_name
        else:
            # this is a simple scalar or value
            # no need to assign to external variable, return as-is
            return value

    # resolve all values such that they are all simple values
    x = resolve("x", x)
    y = resolve("y", y)
    w = resolve("w", w)
    h = resolve("h", h)
    ls = resolve("ls", ls)
    ts = resolve("ts", ts)
    rs = resolve("rs", rs)
    bs = resolve("bs", bs)
    _else = resolve("else", _else)

    if add is not None:
        add = resolve("add", add)
    if sub is not None:
        sub = resolve("sub", sub)

    result_list = [x, y, w, h, ls, ts, rs, bs]

    # store all lines to output
    lines = []

    # assign temporary variables (if any)
    for temp_var_name, expression in temp_variables.items():
        lines.append(f"set {temp_var_name} {expression}")

    # build the final expression to set the target
    expr = f"[{' '.join(result_list)}]"

    if add is not None:
        expr = f"+ {expr} {add}"

    if sub is not None:
        expr = f"- {expr} {sub}"

    if condition is not None:
        # we need to count the number of conditions
        # i'm assuming that conditions are space-separated, so just split and count
        condition = condition.strip()
        condition_count = len(condition.split())
        expr = f"{condition} {expr} {' '.join(_else for _ in range(condition_count))}"

    # create the final assignment line
    lines.append(f"set {target} {expr}")

    return "\n".join(lines)


# @register_func
# def rgba(r, g, b, a):
#     return (r << 24) + (g << 16) + (b << 8) + a


NRGB_CONST = 0x1000000


# @register_func
# def nrgb(r, g, b):
#     return rgb(r, g, b) - NRGB_CONST


# fmt: off
BLEND_MODES = {
    "normal":   0b00000000,
    "add":      0b00000001,
    "overlay":  0b00000100,
    "multiply": 0b00000011,
    "dodge":    0b00000010,
    "hsv":      0b11111110,
}
# fmt: on


@register_func
def blend(mode: str, frac: float):
    # the blend mode is a 18-bit value, split into multiple parts:
    #
    #     0b1 frac_____ mode____
    #     0b1 100000000 11111110

    # reaper's frac value is represented as a fraction: x / 256
    # we need to find the nearest x value
    if not 0 <= frac <= 1:
        raise ValueError(f"Unknown blend fraction must be between 0 and 1: {frac}")

    rp_frac = round(frac * 256)

    # the mode value is just an enum
    if not mode in BLEND_MODES:
        raise ValueError(f"Unknown blend mode: {mode}")

    rp_mode = BLEND_MODES[mode]

    return 0b100000000000000000 + (rp_frac << 8) + rp_mode


@register_func
def rev(val: int):
    """
    Given a hex number like 0x112233, reverse every 2 bytes to
    follow Reaper's number format.

    i.e. The above number will return 0x332211
    """
    result = 0
    while val > 0:
        # split the number into the last 8 bits and the rest
        remainder = val & 0xFF
        val = val >> 8

        # move the result 8 bits to the left, then add the remainder
        # to the rightmost 8 bits
        result = (result << 8) + remainder

    return result
