import os.path
import zipfile
from configparser import ConfigParser
from io import StringIO
from pathlib import Path
from typing import NamedTuple


class DuplicateResourceError(Exception):
    pass


class InvalidThemeNameError(Exception):
    pass


class Resource(NamedTuple):
    # The local path to the resource file you want to include
    src: Path
    # The virtual ZIP path to write the resource to
    dst: Path


def create_theme(
    path,
    *,
    rtconfig: str | None = None,
    rptheme: ConfigParser | None = None,
    resources: list[Resource] | None = None,
):
    if rtconfig is None:
        rtconfig = ""
    if rptheme is None:
        rptheme = ConfigParser()
    if resources is None:
        resources = []

    # resolve the real path to the outpu
    # abspath also calls normpath
    path = Path(os.path.abspath(path))

    # validate the output path
    if not path.name.lower().endswith(".reaperthemezip"):
        raise ValueError("Output extension must be .ReaperThemeZip")
    if len(path.stem) == 0:
        raise InvalidThemeNameError("The theme name cannot be empty.")

    # validation for the list of resources
    seen_dst_paths = set()
    for src_path, dst_path in resources:
        if dst_path in seen_dst_paths:
            raise DuplicateResourceError(
                f"The destination {dst_path!r} has already been assigned to a different resource: {src_path}"
            )

        seen_dst_paths.add(dst_path)

    # serialise the rptheme ConfigParser into string
    with StringIO() as f:
        rptheme.write(f, space_around_delimiters=False)
        rptheme_serialized = f.getvalue()

    # create the zip and write resources into it
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for src_path, dst_path in resources:
            z.write(src_path, arcname=os.path.join(path.stem, dst_path))

        z.writestr(f"{path.stem}.ReaperTheme", rptheme_serialized)
        z.writestr(f"{path.stem}/rtconfig.txt", rtconfig)
