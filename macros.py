def rgb(r, g, b):
    return (b << 16) + (g << 8) + r


# def rgba(r, g, b, a):
#     return (r << 24) + (g << 16) + (b << 8) + a


def nrgb(r, g, b):
    return rgb(r, g, b) - 0x1000000


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
