import os
import functools


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
                if is_rtconfig(entry.path) or is_rptheme(entry.path):
                    info._datafiles.append(entry.name)
                else:
                    info._files.append(entry.name)

        for path in dirpaths:
            subinfo = cls.scan(path)
            info._subdirs.append(subinfo)

        return info

    def is_datadir(self):
        return len(self._datafiles) > 0

    @functools.cache
    def datadirs(self):
        """all directories that have at least 1 datafile"""
        datadirs: list["DirInfo"] = []
        to_check = [self]

        while len(to_check) > 0:
            info = to_check.pop(0)
            to_check.extend(info._subdirs)
            if info.is_datadir():
                datadirs.append(info)

        return datadirs

    def partial_filemap(self):
        """
        generate a partial filemap for a datadir
        when creating the filemap, this method excludes any subfolders that are datadirs:

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

    @functools.cache
    def filemap(self):
        """find all datadirs within this folder, and combine the filemaps from all of them"""
        allmap = []
        for info in self.datadirs():
            allmap.extend(info.partial_filemap())
        return allmap

    @functools.cache
    def datafiles(self):
        files = []
        for info in self.datadirs():
            files.extend(os.path.join(info._path, n) for n in info._datafiles)
        return files

    @functools.cache
    def rtconfig_paths(self):
        return [p for p in self.datafiles() if is_rtconfig(p)]

    @functools.cache
    def rptheme_paths(self):
        return [p for p in self.datafiles() if is_rptheme(p)]
