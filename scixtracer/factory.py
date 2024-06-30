"""Plugin loader factory"""
import importlib
import pkgutil


class Factory:
    """Factory to instantiate an interface implementation

    :param module_prefix: Prefix of the module containing implementation,
    :param submodule_name: Name of the submodule containing the API export
    """
    def __init__(self, module_prefix: str, submodule_name: str):
        self.__module_prefix = module_prefix
        self.__submodule_name = submodule_name
        self.__models = self.__register_plugins()

    @property
    def models(self) -> dict:
        """Get the available models

        :return: dict of models classes
        """
        return self.__models

    def __register_plugins(self):
        """Register compatible plugins to the factory"""
        discovered_plugins = {
            name: name
            for finder, name, is_pkg
            in pkgutil.iter_modules()
            if name.startswith(self.__module_prefix)
        }
        modules_info = {}
        for name in discovered_plugins:
            mod = importlib.import_module(f'{name}.{self.__submodule_name}')
            service_id = name.replace(self.__module_prefix, '')
            if isinstance(mod.export, list):
                modules_info[service_id] = mod.export[0]
            else:
                modules_info[service_id] = mod.export
        return modules_info

    def get(self, name: str) -> any:
        """Get an interface implementation

        :param name: Name of the implementation,
        :return: The found implementation
        """
        if name not in self.__models:
            raise ValueError(
                f'Cannot find implementation of {name}')
        return self.__models[name]
