from configparser import ConfigParser


class ConstantsConfig:
    def __init__(self, path: str | None = None) -> None:
        self._config = ConfigParser()
        if path:
            self._config.read(path)

    def get_constant(self, full_name: str):
        try:
            section, name = full_name.rsplit(".", maxsplit=1)
        except ValueError:
            raise ValueError(f"Invalid section name: {full_name}")

        if section not in self._config:
            raise ValueError(f"Constant section not found: {section}")

        if name not in self._config[section]:
            raise ValueError(f"Constant name not found in section {section!r}: {name}")

        return self._config[section][name]

    def __len__(self):
        return sum(len(self._config[section]) for section in self._config)
