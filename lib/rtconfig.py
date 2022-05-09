def _trim_line(line: str):
    split = line.split(";", 1)
    return split[0].strip()


def trim(text: str):
    lines = (_trim_line(l) for l in text.splitlines())
    lines = (l for l in lines if len(l) != 0)
    return "\n".join(lines)


def from_path(path: str):
    with open(path, "r", encoding="utf8") as f:
        return trim(f.read())


def from_paths(paths):
    contents = []
    for p in paths:
        text = from_path(p)
        # some rtconfig files may be empty, only append if text is non-empty
        if len(text) != 0:
            contents.append(text)
    return "\n".join(contents)
