from configparser import ConfigParser


def get_config_section_and_key(config: ConfigParser, full_name: str):
    """
    Given a config and a full name like 'REAPER.ui_img', determine the section and the
    key. In this case, 'REAPER.ui_img' will return ('REAPER', 'ui_img').
    """
    try:
        section, name = full_name.rsplit(".", maxsplit=1)
    except ValueError:
        raise ValueError(f"Invalid section name: {full_name}")

    if section not in config:
        raise ValueError(f"Constant section not found: {section}")

    if name not in config[section]:
        raise ValueError(f"Constant name not found in section {section!r}: {name}")

    return section, name
