# Registry for Validators

from __future__ import annotations

import logging
logger = logging.getLogger(__name__)

class Locator:
    """
    Locator
    implements a singleton locator pattern
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._components = {}
        return cls._instance

    @staticmethod
    def register(keys:object|list[object], component:object) -> None:
        """
        Registers a component to one or more locator keys
        - on duplicate keys, the last component registered will be used
        :param keys:            locator key(s) for the validator, 
                                supports list of keys, or single key, 
                                either as a scalar value or object
        :param component:       the component to register
        """
        for key in keys if isinstance(keys, list) else [keys]:
            Locator()._components[key] = component
            component_name = component.__name__ if hasattr(component, "__name__") else type(component).__name__
            key_name = key if isinstance(key, (str, int, float, bool)) else type(key).__name__
            logger.debug(f"Registered component '{component_name}' for key '{key_name}' in locator")

    @staticmethod
    def lookup(key:object, default=None) -> object:
        """
        Looks up the component registered for the specified key
        :param key:             the key to look up
        :return:                the matching component
        """
        return Locator()._components.get(key, default)
