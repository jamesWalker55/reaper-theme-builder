def _trim_line(line: str):
    split = line.split(";", 1)
    return split[0].strip()


def trim(text: str):
    """
    Given the contents of a rtconfig.txt file, trim all comments, whitespaces and empty
    newlines.
    """
    lines = (_trim_line(l) for l in text.splitlines())
    lines = (l for l in lines if len(l) != 0)
    return "\n".join(lines)


def from_path(path: str, *, minify=False):
    """Load a rtconfig.txt file"""
    with open(path, "r", encoding="utf8") as f:
        if minify:
            return trim(f.read())
        else:
            return f.read()


def from_paths(paths, *, minify=False):
    """Load multiple rtconfig.txt files and combine them into a single file"""
    contents = []
    for p in paths:
        text = from_path(p, minify=minify)
        # some rtconfig files may be empty, only append if text is non-empty
        if len(text) != 0:
            contents.append(text)
    return "\n".join(contents)
