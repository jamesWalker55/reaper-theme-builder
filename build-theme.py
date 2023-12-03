import argparse
import os

from lib.scanner import DirInfo
from lib.theme import Theme

parser = argparse.ArgumentParser()
parser.add_argument("input")
parser.add_argument("output")
parser.add_argument(
    "-c",
    "--config",
    nargs=2,
    metavar=("key", "value"),
    help="override a value from the .ReaperTheme config",
    default=[],
    action="append",
)
parser.add_argument(
    "-d",
    "--debug",
    help="create extra ReaperTheme and rtconfig files alongside the output Zip file",
    default=[],
    action="store_true",
)
parser.add_argument(
    "-m",
    "--minify",
    help="strip comments and whitespace from the output rtconfig file",
    default=[],
    action="store_true",
)


def parse_extra_reapertheme_configs(args: list[list[str]]):
    result = {}
    for k, v in args:
        if "." not in k:
            raise ValueError(
                f"key must contain a period ('.') to delimit the section: {k!r}"
            )
        section, k = k.split(".", 1)
        if section not in result:
            result[section] = {}
        result[section][k] = v
    return result


def main():
    args = parser.parse_args()

    args.input = os.path.abspath(args.input)
    output_dir, output_name = os.path.split(args.output)
    output_stem, output_ext = os.path.splitext(output_name)
    theme_name = output_stem

    if output_ext.lower() != ".reaperthemezip":
        raise ValueError("Output extension must be .ReaperThemeZip")

    print(f"Using {theme_name!r} as the theme name.")
    print(f"Scanning folder: {args.input}")

    info = DirInfo.scan(args.input)

    theme = Theme(parse_extra_reapertheme_configs(args.config))

    print("Merging *.rtconfig files:")
    for p in info.rtconfig_paths():
        print(f"  {p}")
        theme.add_rtconfig(p)

    print("Merging *.ReaperTheme files:")
    for p in info.rptheme_paths():
        print(f"  {p}")
        theme.add_rptheme(p)

    print("Adding resources:")
    for path, arcpath in info.filemap():
        print(f"  [{arcpath}]: {path}")
        theme.add_resource(arcpath, path)

    print(f"Writing ZIP file to {args.output}")

    theme.write_zip(args.output, theme_name=theme_name, minify=args.minify)

    if args.debug:
        print(f"Writing debug files to same directory")
        debug_rptheme_path = os.path.join(output_dir, f"{theme_name}.ReaperTheme")
        debug_rtconfig_path = os.path.join(output_dir, f"{theme_name}.rtconfig.txt")
        print(f"  [ReaperTheme] {debug_rptheme_path}")
        with open(debug_rptheme_path, "w", encoding="utf8") as f:
            f.write(theme.build_rptheme())
        print(f"  [rtconfig] {debug_rtconfig_path}")
        with open(debug_rtconfig_path, "w", encoding="utf8") as f:
            f.write(theme.build_rtconfig(minify=args.minify))

    print("Success!")


if __name__ == "__main__":
    main()
