"""Manage the interaction with the configuration"""
from pathlib import Path
import yaml


def config_file() -> Path:
    """Try to find the config file"""
    current_dir_conf = Path(".").resolve() / "config.yml"
    if current_dir_conf.exists():
        return current_dir_conf
    lib_default_conf = Path(__file__).parent.parent.resolve() / "config.yml"
    if lib_default_conf.exists():
        return lib_default_conf
    raise FileNotFoundError("Cannot find the configuration file")


class Config:
    """Singleton to access the config file"""
    __instance = None

    def __init__(self, config_path: Path):
        """ Virtually private constructor.

        :param config_path: Path to the config file
        """
        self.__file = config_path
        if Config.__instance is not None:
            raise RuntimeError("Config service can be initialized only once!")
        Config.__instance = ConfigData(config_path)

    @property
    def file(self) -> Path:
        """Get the config file path

        :return: The file path
        """
        return self.__file

    @staticmethod
    def service(config_path: Path = None):
        """Static access method to the Config.

        :param config_path: YAML file containing the config data
        """
        if Config.__instance is None:
            Config.__instance = ConfigData(config_path)
        return Config.__instance


def config(config_path: Path = None):
    """Shortcut function to call the configuration

    :param config_path: YAML file containing the config data
    """
    return Config.service(config_path)


class ConfigData:
    """Container for config data

    :param file: Config file path
    """
    def __init__(self, file: Path):
        self.__file = file
        with open(str(file), 'r', encoding="utf-8") as fil:
            self.__data = yaml.safe_load(fil)

    @property
    def file(self) -> Path:
        """Get the config file path"""
        return self.__file

    @property
    def data(self) -> dict[str, dict[str, str]]:
        """Get the config file content"""
        return self.__data

    def section(self, key: str) -> dict[str, str]:
        """Get the config data for on category

        :param key: ID key of the category
        :return: the config dictionary or None
        """
        if key not in self.data:
            raise ValueError(f"Cannot find the section {key} in the config")
        return self.data[key]

    def filtered_section(self, key: str) -> dict[str, str]:
        """Get the section content without the name key

        :param key: ID key of the category
        :return: the config dictionary or None
        """
        if key not in self.data:
            raise ValueError(f"Cannot find the section {key} in the config")
        values = self.data[key]
        values.pop("name")
        return values

    def value(self, section_name: str, key: str) -> str:
        """Get the config data for on category

        :param section_name: Section name in the config file
        :param key: ID key of the category
        :return: the config dictionary or None
        """
        data = self.section(section_name)
        if key not in data:
            raise ValueError(f"Cannot find the key {key} in the config "
                             f"section {section_name}")
        return data[key]
