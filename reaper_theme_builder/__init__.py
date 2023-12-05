import argparse
import os
from pathlib import Path

from .lib import rptheme, rtconfig
from .lib.scanner import DirInfo
from .lib.val.constants import ConstantsConfig
from .lib.val.evaluator import Evaluator

parser = argparse.ArgumentParser()
parser.add_argument("input", type=Path)
parser.add_argument("output", type=Path)
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
    action="store_true",
)
parser.add_argument(
    "-p",
    "--constants-path",
    help='path to an ini file defining constants, use constants with the syntax: c("section.name_of_your_constant")',
    type=Path,
)
parser.add_argument(
    "-all",
    "--all-resources",
    help="add all files found in the source folder to the theme, instead of only adding .png files",
    action="store_true",
)
parser.add_argument(
    "-v",
    "--verbose",
    help="print the files used to build the theme",
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

    # convert to absolute path to ensure we can get the directory name
    input_dir: Path = args.input.absolute().resolve()
    output_file: Path = args.output
    theme_name = input_dir.stem

    # validation
    if output_file.suffix.lower() != ".reaperthemezip":
        raise ValueError("Output extension must be .ReaperThemeZip")

    print(f"Using {theme_name!r} as the theme name.")
    print(f"Scanning folder: {input_dir}")

    # scan and build list of files
    dirinfo = DirInfo.scan(input_dir, png_only=not args.all_resources)

    # construct initial config and stuff
    if args.verbose:
        print(f"Adding {len(dirinfo.filemap())} resources:")
        for src, dst in dirinfo.filemap():
            print(f"  [{dst}]: {src}")
    else:
        print(f"Adding {len(dirinfo.filemap())} resources...")

    if args.verbose:
        print(f"Merging {len(dirinfo.rtconfig_paths())} *.rtconfig files:")
        for path in dirinfo.rtconfig_paths():
            print(f"  {path}")
    else:
        print(f"Merging {len(dirinfo.rtconfig_paths())} *.rtconfig files...")
    rtc = rtconfig.from_paths(dirinfo.rtconfig_paths())

    if args.verbose:
        print(f"Merging {len(dirinfo.rptheme_paths())} *.ReaperTheme files:")
        for path in dirinfo.rptheme_paths():
            print(f"  {path}")
    else:
        print(f"Merging {len(dirinfo.rptheme_paths())} *.ReaperTheme files...")
    rpt = rptheme.from_paths(dirinfo.rptheme_paths())

    # post-process
    print("Post processing rtconfig and ReaperTheme...")
    constants = ConstantsConfig(args.constants_path)
    if args.verbose:
        print(f"  Loaded {len(constants)} constants")
    evaluator = Evaluator(constants=constants)
    rtc = evaluator.parse_double(rtc)
    for section in rpt:
        for key in rpt[section]:
            rpt[section][key] = evaluator.parse_single(rpt[section][key])

    # print(f"Writing ZIP file to {args.output}")

    # theme.write_zip(args.output, theme_name=theme_name, minify=args.minify)

    # if args.debug:
    #     print(f"Writing debug files to same directory")
    #     debug_rptheme_path = os.path.join(output_dir, f"{theme_name}.ReaperTheme")
    #     debug_rtconfig_path = os.path.join(output_dir, f"{theme_name}.rtconfig.txt")
    #     print(f"  [ReaperTheme] {debug_rptheme_path}")
    #     with open(debug_rptheme_path, "w", encoding="utf8") as f:
    #         f.write(theme.build_rptheme())
    #     print(f"  [rtconfig] {debug_rtconfig_path}")
    #     with open(debug_rtconfig_path, "w", encoding="utf8") as f:
    #         f.write(theme.build_rtconfig(minify=args.minify))

    # print("Success!")
