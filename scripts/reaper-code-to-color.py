from pyperclip import copy as pcopy, paste as ppaste


def convert_color(code):
    if code >= 0:
        method = "rgb"
    else:
        method = "nrgb"
        code = code + 0x1000000

    r = code & 0xFF
    g = (code >> 8) & 0xFF
    b = (code >> 16) & 0xFF

    return f"{method}({r}, {g}, {b})"


BLEND_MODES = {
    0b00000000: "normal",
    0b00000001: "add",
    0b00000100: "overlay",
    0b00000011: "multiply",
    0b00000010: "dodge",
    0b11111110: "hsv",
}


def convert_blend_mode(code):
    assert code & 0b100000000000000000

    rp_frac = (code & 0b111111111_00000000) >> 8
    rp_mode = code & 0b11111111

    assert rp_mode in BLEND_MODES
    mode = BLEND_MODES[rp_mode]

    frac = rp_frac / 256

    return f"blend({mode}, {frac:0.3f})"


def conv_line(line: str):
    if line.startswith(";"):
        return line

    if "=" not in line:
        return line

    key, val = line.split("=", 1)
    try:
        val = int(val)
    except ValueError:
        return line

    # val = convert_color(val)
    val = convert_blend_mode(val)
    return f"{key}={{{val}}}"


def conv_text(text: str):
    lines = text.splitlines()
    lines = [conv_line(l) for l in lines]
    return "\n".join(lines)


def conv_clipboard():
    text = ppaste()
    text = conv_text(text)
    pcopy(text)
