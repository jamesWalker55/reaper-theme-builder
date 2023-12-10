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
