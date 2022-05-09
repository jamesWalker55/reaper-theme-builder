import os

def is_rtconfig(path):
    return path.lower().endswith("rtconfig.txt")


def is_rptheme(path):
    return path.lower().endswith(".reapertheme")


class DirInfo:
    def __init__(self, path, files=None, datafiles=None, subdirs=None) -> None:
        # the location of this directory
        self._path = os.path.abspath(path)

        # files in this directory, excluding data files like rtconfig.txt
        self._files = [] if files is None else files

        # data files this directory
        self._datafiles = [] if datafiles is None else datafiles

        # subdirectories in this directory
        self._subdirs = [] if subdirs is None else subdirs

        self._datadirs = None

    @classmethod
    def scan(cls, path):
        info = cls(path)

        dirpaths = []

        for entry in os.scandir(path):
            if entry.is_dir():
                dirpaths.append(entry.path)
            else:
                if cls.is_rtconfig(entry.path) or cls.is_rptheme(entry.path):
                    info._datafiles.append(entry.name)
                else:
                    info._files.append(entry.name)

        for path in dirpaths:
            subinfo = cls.scan(path)
            info._subdirs.append(subinfo)

        return info

    def is_datadir(self):
        return len(self._datafiles) > 0

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
            to_check.extend(info._subdirs)
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
        files = [os.path.join(self._path, f) for f in self._files]
        # list of directories to check for more files
        checkdirs = [d for d in self._subdirs if not d.is_datadir()]

        while len(checkdirs) > 0:
            subdir = checkdirs.pop(0)
            files.extend([os.path.join(subdir.path, f) for f in subdir.files])
            checkdirs.extend([d for d in subdir.subdirs if not d.is_datadir()])

        # we now have a list of files this data folder provides
        # convert them to paths relative to the archive
        filemap = [(f, os.path.relpath(f, self._path)) for f in files]

        return filemap

    def filemap(self):
        allmap = []
        for info in self.datadirs():
            allmap.extend(info._datadir_filemap())
        return allmap

    def build_rtconfig(self):
        paths = []

        for info in self.datadirs():
            paths.extend(
                [
                    os.path.join(info._path, f)
                    for f in info._datafiles
                    if self.is_rtconfig(f)
                ]
            )

        return rtconfig.from_paths(paths)

    def build_rptheme(self):
        files = []

        for info in self.datadirs():
            files.extend(
                [
                    os.path.join(info._path, f)
                    for f in info._datafiles
                    if self.is_rptheme(f)
                ]
            )

        return rptheme.from_paths(files)
