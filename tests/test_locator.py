import pytest
from validdict.locator import Locator # object under test


class TestLocator:

    def test_locator_singleton(self):
        # Ensure that the Locator class is a singleton
        locator1 = Locator()
        locator2 = Locator()
        assert locator1 is locator2

    def test_locator_register_and_lookup(self):
        # Test the register() and lookup() methods of the Locator class
        locator = Locator()

        # Register a component with a single key
        key1 = "key1"
        component1 = "component1"
        locator.register(key1, component1)
        assert locator.lookup(key1) == component1

        # Register a component with multiple keys
        keys2 = ["key2", "key3"]
        component2 = "component2"
        locator.register(keys2, component2)
        assert locator.lookup("key2") == component2
        assert locator.lookup("key3") == component2

        # Lookup a key that doesn't exist
        assert locator.lookup("key4") is None

        # Lookup a key with a default value
        assert locator.lookup("key4", default="default") == "default"
