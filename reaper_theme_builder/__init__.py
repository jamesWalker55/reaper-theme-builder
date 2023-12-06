import argparse
import os
from pathlib import Path

from .lib import rptheme, rtconfig
from .lib.scanner import DirInfo
from .lib.theme import Resource, create_theme
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

    def log(*x):
        if not args.verbose:
            return

        print(*x)

    # convert to absolute path to ensure we can get the directory name
    input_dir: Path = args.input.absolute().resolve()
    output_file: Path = args.output

    # validation
    if output_file.suffix.lower() != ".reaperthemezip":
        raise ValueError("Output extension must be .ReaperThemeZip")

    print(f"Scanning folder: {input_dir}")

    # scan and build list of files
    dirinfo = DirInfo.scan(input_dir, png_only=not args.all_resources)

    # construct initial config and stuff
    print(f"Adding {len(dirinfo.filemap())} resources...")
    res: list[Resource] = []
    for src, dst in res:
        res.append(Resource(src, dst))
        log(f"  [{dst}]: {src}")

    print(f"Merging {len(dirinfo.rtconfig_paths())} *.rtconfig files...")
    for path in dirinfo.rtconfig_paths():
        log(f"  {path}")
    rtc = rtconfig.from_paths(dirinfo.rtconfig_paths())

    print(f"Merging {len(dirinfo.rptheme_paths())} *.ReaperTheme files...")
    for path in dirinfo.rptheme_paths():
        log(f"  {path}")
    rpt = rptheme.from_paths(dirinfo.rptheme_paths())

    # post-process
    print("Post processing rtconfig and ReaperTheme...")
    constants = ConstantsConfig(args.constants_path)
    log(f"  Loaded {len(constants)} constants")
    evaluator = Evaluator(constants=constants)
    # proces rtconfig
    rtc = evaluator.parse_double(rtc)
    # process ReaperTheme
    for section in rpt:
        for key in rpt[section]:
            rpt[section][key] = evaluator.parse_single(rpt[section][key])

    print(f"Writing ZIP file to {args.output}")

    create_theme(output_file, rtconfig=rtc, rptheme=rpt, resources=res)

    if args.debug:
        rtc_path = output_file.with_suffix(".rtconfig.txt")
        print(f"  [rtconfig] {rtc_path}")
        with open(rtc_path, "w", encoding="utf8") as f:
            f.write(rtc)

        rpt_path = output_file.with_suffix(".ReaperTheme")
        print(f"  [ReaperTheme] {rpt_path}")
        # serialise the rptheme ConfigParser into string
        with open(rpt_path, "w", encoding="utf8") as f:
            rpt.write(f, space_around_delimiters=False)

    print("Success!")
