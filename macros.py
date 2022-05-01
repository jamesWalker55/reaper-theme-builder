def rgb(r, g, b):
    return (b << 16) + (g << 8) + r


# def rgba(r, g, b, a):
#     return (r << 24) + (g << 16) + (b << 8) + a


def nrgb(r, g, b):
    return rgb(r, g, b) - 0x1000000


BLEND_MODES = {
    "normal":   0b00000000,
    "add":      0b00000001,
    "overlay":  0b00000100,
    "multiply": 0b00000011,
    "dodge":    0b00000010,
    "hsv":      0b11111110,
}

def blend(mode, frac):
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


def split_hex(num):
    """
    Split a number into its 2-digit hex components.
    Outputs in reverse order (because reaper uses reverse order).

    >>> split_hex(0x123456)
    [86, 52, 18]  # [0x56, 0x34, 0x12]
    """
    nums = []
    while num > 0:
        nums.append(num & 0xFF)
        num = num >> 8
    return nums


def hexcolor(code):
    # code is like '0xff0055'
    nums = split_hex(int(code, 16))
    result = 0
    for i, n in enumerate(nums):
        result += n << 8 * (len(nums) - i - 1)
    return result
