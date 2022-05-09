import os.path
import zipfile
import rtconfig, rptheme


class DuplicateResourceError(Exception):
    pass


class InvalidThemeNameError(Exception):
    pass


class Theme:
    def __init__(self) -> None:
        self.rtconfigs = []
        self.rpthemes = []

        # a map from archive paths to filesystem paths
        self.res_map = {}

    def add_resource(self, res_path, fs_path):
        if res_path in self.res_map:
            raise DuplicateResourceError(
                f"Resource {res_path!r} already exists with source: {self.res_map[res_path]!r}"
            )

        self.res_map[res_path] = fs_path

    def add_rtconfig(self, path):
        self.rtconfigs.append(path)

    def add_rptheme(self, path):
        self.rpthemes.append(path)

    def build_rtconfig(self):
        return rtconfig.from_paths(self.rtconfigs)

    def build_rptheme(self):
        return rptheme.from_paths(self.rpthemes)

    def write_zip(self, path, theme_name=None):
        path = os.path.abspath(path)  # abspath also calls normpath

        output_name = os.path.split(path)[1]
        output_stem, output_ext = os.path.splitext(output_name)

        if output_ext.lower() != ".reaperthemezip":
            raise ValueError("Output extension must be .ReaperThemeZip")

        if theme_name is None:
            theme_name = output_stem

        if len(theme_name) == 0:
            raise InvalidThemeNameError("The theme name cannot be empty.")

        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            for res_path, fs_path in self.res_map.items():
                z.write(fs_path, arcname=os.path.join(theme_name, res_path))

            z.writestr(f"{theme_name}.ReaperTheme", self.build_rptheme())
            z.writestr(f"{theme_name}/rtconfig.txt", self.build_rtconfig())
