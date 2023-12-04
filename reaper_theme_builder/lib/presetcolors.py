from configparser import ConfigParser


class ColorPresetConfig:
    def __init__(self, path) -> None:
        self._config = ConfigParser()
        self._config.read(path)

    def get_color(self, full_name: str):
        try:
            section, name = full_name.rsplit(".", maxsplit=1)
        except ValueError:
            raise ValueError(f"Invalid color preset name: {full_name}")

        if section not in self._config:
            raise ValueError(f"Color preset section not found: {section}")

        if name not in self._config[section]:
            raise ValueError(
                f"Color preset name not found in section {section!r}: {name}"
            )

        return self._config[section][name]
