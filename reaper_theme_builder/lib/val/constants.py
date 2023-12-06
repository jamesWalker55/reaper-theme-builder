from configparser import ConfigParser

from ..utils import get_config_section_and_key


class ConstantsConfig:
    def __init__(self, path: str | None = None) -> None:
        self._config = ConfigParser()
        if path:
            self._config.read(path)

    def get_constant(self, full_name: str):
        section, name = get_config_section_and_key(self._config, full_name)
        return self._config[section][name]

    def __len__(self):
        return sum(len(self._config[section]) for section in self._config)
