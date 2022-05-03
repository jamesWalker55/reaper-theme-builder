from configparser import ConfigParser
from dataclasses import dataclass, field
from io import StringIO
import os
import zipfile
import argparse
import formatter, rtconfig


parser = argparse.ArgumentParser()
parser.add_argument("input")
parser.add_argument("output")


@dataclass
class DirInfo:
    # the location of this directory
    path: str
    # files in this directory, excluding data files like rtconfig.txt
    files: list[str] = field(default_factory=list)
    # data files this directory
    datafiles: list[str] = field(default_factory=list)
    # subdirectories in this directory
    subdirs: list["DirInfo"] = field(default_factory=list)
    _datadirs: list["DirInfo"] = None

    @staticmethod
    def is_rtconfig(path):
        return path.lower().endswith("rtconfig.txt")

    @staticmethod
    def is_rptheme(path):
        return path.lower().endswith(".reapertheme")

    @classmethod
    def scan(cls, path):
        # path = os.path.normpath(path)
        info = cls(path)

        dirpaths = []

        for entry in os.scandir(path):
            if entry.is_dir():
                dirpaths.append(entry.path)
            else:
                if cls.is_rtconfig(entry.path) or cls.is_rptheme(entry.path):
                    info.datafiles.append(entry.name)
                else:
                    info.files.append(entry.name)

        for path in dirpaths:
            subinfo = cls.scan(path)
            info.subdirs.append(subinfo)

        return info

    def is_datadir(self):
        return len(self.datafiles) > 0

    def datadirs(self: "DirInfo", reload=False):
        """all directories that have at least 1 datafile"""
        if self._datadirs is None or reload:
            self._reload_datadirs()

        return self._datadirs

    def _reload_datadirs(self):
        """all directories that have at least 1 datafile"""
        dirs: list["DirInfo"] = []
        to_check = [self]

        while len(to_check) > 0:
            info = to_check.pop(0)
            to_check.extend(info.subdirs)
            if info.is_datadir():
                dirs.append(info)

        self._datadirs = dirs

        return dirs

    def _datadir_filemap(self):
        """
        generate a partial filemap for a datadir
        when creating the filemap, we exclude any subfolders that are datadirs:

        - 150/
            - a.png
        - 200/
            - a.png
        - test/
            # this folder contains a rtconfig.txt, so this folder will be excluded
            # please scan this folder separately then add to results
            - c.png
            - rtconfig.txt
        - a.png
        - b.png
        """
        assert self.is_datadir()

        # list of files, using their actual path
        files = [os.path.join(self.path, f) for f in self.files]
        # list of directories to check for more files
        checkdirs = [d for d in self.subdirs if not d.is_datadir()]

        while len(checkdirs) > 0:
            subdir = checkdirs.pop(0)
            files.extend([os.path.join(subdir.path, f) for f in subdir.files])
            checkdirs.extend([d for d in subdir.subdirs if not d.is_datadir()])

        # we now have a list of files this data folder provides
        # convert them to paths relative to the archive
        filemap = [(f, os.path.relpath(f, self.path)) for f in files]

        return filemap

    def filemap(self):
        allmap = []
        for info in self.datadirs():
            allmap.extend(info._datadir_filemap())
        return allmap

    def build_rtconfig(self):
        paths = []

        for info in self.datadirs():
            paths.extend([os.path.join(info.path, f) for f in info.datafiles if self.is_rtconfig(f)])

        return rtconfig.from_paths(paths)

    def build_rptheme(self):
        config = ConfigParser()

        for info in self.datadirs():
            files = [f for f in info.datafiles if self.is_rptheme(f)]
            for f in files:
                path = os.path.join(info.path, f)
                config.read(path)

        # apply macros
        for section in config:
            for key in config[section]:
                config[section][key] = formatter.parse(config[section][key])

        with StringIO() as f:
            config.write(f, space_around_delimiters=False)
            f.seek(0)
            return f.read()


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

    print(f"Writing ZIP file to {args.output}")

    with zipfile.ZipFile(args.output, "w", zipfile.ZIP_DEFLATED) as z:
        for path, arcpath in info.filemap():
            z.write(path, arcname=os.path.join(theme_name, arcpath))

        z.writestr(f"{theme_name}.ReaperTheme", info.build_rptheme())
        z.writestr(f"{theme_name}/rtconfig.txt", info.build_rtconfig())

    print("Success!")


if __name__ == "__main__":
    main()
