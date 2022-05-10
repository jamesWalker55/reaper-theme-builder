import argparse
import os

from lib.scanner import DirInfo
from lib.theme import Theme

parser = argparse.ArgumentParser()
parser.add_argument("input")
parser.add_argument("output")


def main():
    args = parser.parse_args()

    args.input = os.path.abspath(args.input)
    output_name = os.path.split(args.output)[1]
    output_stem, output_ext = os.path.splitext(output_name)
    theme_name = output_stem

    if output_ext.lower() != ".reaperthemezip":
        raise ValueError("Output extension must be .ReaperThemeZip")

    print(f"Using {theme_name!r} as the theme name.")
    print(f"Scanning folder: {args.input}")

    info = DirInfo.scan(args.input)

    theme = Theme()

    for p in info.rtconfig_paths():
        theme.add_rtconfig(p)

    for p in info.rptheme_paths():
        theme.add_rptheme(p)

    for path, arcpath in info.filemap():
        print("Add resource:", arcpath, path)
        theme.add_resource(arcpath, path)

    print(f"Writing ZIP file to {args.output}")

    theme.write_zip(args.output, theme_name=theme_name)

    print("Success!")


if __name__ == "__main__":
    main()
