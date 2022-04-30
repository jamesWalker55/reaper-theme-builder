from dataclasses import dataclass, field
import os
from pprint import pprint
import zipfile
import glob
from pathlib import Path


# def scantree(path):
#     folders = [path]

#     while len(folders) > 0:
#         path = folders.pop(0)

#         for entry in os.scandir(path):
#             if entry.is_dir(follow_symlinks=False):
#                 folders.append(entry.path)
#             else:
#                 yield entry


# def scantree(path):
#     for entry in os.scandir(path):
#         if entry.is_dir(follow_symlinks=False):
#             yield from scantree(entry.path)
#         else:
#             yield entry


# for x in scantree(os.path.abspath(os.path.normpath('Neptune VI'))):
#     print(x.path)


# def ass(path):
#     subdirs = []
#     for entry in os.scandir(path):
#         if entry.is_dir(follow_symlinks=False):
#             sub_rtconfig_path = os.path.join(entry.path, 'rtconfig.txt')
#             if not os.path.isfile(sub_rtconfig_path):
#                 subdirs.append(entry.path)

#             continue

#         if entry.name == 'rtconfig.txt':


def is_rtconfig(path):
    return path.lower().endswith("rtconfig.txt")


def is_rptheme(path):
    return path.lower().endswith(".reapertheme")


def has_data_file(path):
    for entry in os.scandir(path):
        if is_rtconfig(entry.path) or is_rptheme(entry.path):
            return entry.path

    return False


def scan_data_files(path):
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scan_data_files(entry.path)
            continue

        if not (is_rtconfig(entry.path) or is_rptheme(entry.path)):
            continue

        yield Path(entry.path)


def find_root_dirs(path):
    return set(x.parent for x in scan_data_files(path))


# for x in find_root_dirs("."):
#     print(x)


@dataclass
class DirInfo:
    # the path of this folder
    path: str
    # list of subdirectories in this folder, to be further scanned
    subdirs: list[str] = field(default_factory=list)
    # whether this folder should be treated as the root folder
    # a root folder's files will be placed in the root of the resource folder
    is_root_folder: bool = False
    # all of the files to be put in the resource folder
    # data files are excluded from this list (rtconfig and ReaperTheme files)
    files: list[str] = field(default_factory=list)
    # list of rtconfig.ini contents
    rtconfigs: list[str] = field(default_factory=list)
    # list of .ReaperTheme contents
    rpconfigs: list[str] = field(default_factory=list)
    # keep going up parent directories, the first parent directory which is also a data directoy will be here
    # if this is the first folder you scanned, then this is None
    last_archive_root: str = None

    def filemap(self):
        """generate a map from real files to paths in the resource folder"""

        if self.is_root_folder:
            archive_root = self.path

            return [(f, os.path.split(f)[1]) for f in self.files]
        else:
            if self.last_archive_root is None:
                archive_root = self.path
            else:
                archive_root = self.last_archive_root

            return [(f, os.path.relpath(f, archive_root)) for f in self.files]

    @classmethod
    def scan(cls, path, archive_root=None):
        info = cls(path, last_archive_root=archive_root)

        for entry in os.scandir(path):
            if entry.is_dir():
                info.subdirs.append(entry.path)
            else:  # is file
                info.files.append(entry.path)

                if is_rtconfig(entry.path):
                    info.is_root_folder = True
                    with open(entry.path, "r", encoding="utf8") as f:
                        info.rtconfigs.append(f.read())
                elif is_rptheme(entry.path):
                    info.is_root_folder = True
                    with open(entry.path, "r", encoding="utf8") as f:
                        info.rpconfigs.append(f.read())

        return info

# (input, output)
# concat rtconfig
# concat ReaperTheme
# theme name

# for x in fuck("theme"):
x = DirInfo.scan("theme", archive_root='aa')
pprint(x.__dict__)
pprint(x.filemap())

# def zip_write_folder(zipf, path):
#     # ziph is zipfile handle
#     path = os.path.abspath(os.path.normpath(path))

#     root_path = path
#     folders = [path]
#     while len(folders) > 0:
#         path = folders.pop()

#         for entry in os.scandir(path):
#             if entry.is_file():
#                 zipf.write(entry.path, os.path.relpath(entry.path, root_path))
#             else:  # is a folder
#                 folders.append(entry.path)

#     for root, dirs, files in os.walk(path):
#         for file in files:
#             ziph.write(
#                 os.path.join(root, file),
#                 os.path.relpath(os.path.join(root, file), os.path.join(path, "..")),
#             )

# def zipdir(path, ziph):
#     # ziph is zipfile handle
#     for root, dirs, files in os.walk(path):
#         for file in files:
#             ziph.write(
#                 os.path.join(root, file),
#                 os.path.relpath(os.path.join(root, file), os.path.join(path, "..")),
#             )


# with zipfile.ZipFile("Python.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
#     zipdir("tmp/", zipf)

# with zipfile.ZipFile("test.ReaperThemeZip", "w", zipfile.ZIP_DEFLATED) as z:
#     zip_write_folder(z, R"D:\Projects (Misc)\reaper-theme\Neptune VI")
#     z.writestr("a.txt", 'text A, a for apple')
#     z.writestr("b.txt", 'text B, b for bee')
#     z.writestr("b.txt", 'text BBBBBB')
#     z.writestr("sub\\fuck.txt", 'text FUCK, fuck for fuck')
