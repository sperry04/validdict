import pytest
from validdict import RequiredKey, OptionalKey, Str, StartsWith, OtherKeys, Any
from validdict.map import Map # object under test


class TestMap:

    def test_map_constructor(self):
        validator = Map()
        assert isinstance(validator, Map)
        assert repr(validator) == "must be a map like: { OtherKeys(): Any() }"

    def test_illegal_map_definitions(self):
        with pytest.raises(TypeError):
            Map("string")

        with pytest.raises(TypeError):
            Map(Str())

        with pytest.raises(TypeError):
            Map({
                Str(): "value"
            })

        with pytest.raises(TypeError):
            Map({
                "key": RequiredKey("value")
            })

        with pytest.raises(TypeError):
            Map({ 
                "key": "value",
                OptionalKey("key"): "value"
            })

        with pytest.raises(TypeError):
            Map({ 
                "key": "value",
                StartsWith("k"): "value"
            })

        with pytest.raises(TypeError):
            Map({ 
                "key": "value",
                StartsWith("KE", case_sensitive=False): "value"
            })

        with pytest.raises(TypeError):
            Map({ 
                StartsWith("key"): "value",
                StartsWith("KEY", case_sensitive=False): "value"
            })

        with pytest.raises(TypeError):
            Map({ 
                StartsWith("key", case_sensitive=False): "value",
                StartsWith("KEY", case_sensitive=False): "value"
            })

        with pytest.raises(TypeError):
            Map({ 
                StartsWith("key"): "value",
                StartsWith("key"): "value"
            })

        with pytest.raises(TypeError):
            Map({ 
                OtherKeys(): Any(),
                OtherKeys(): Any()
            })

    def test_map_validation(self):
        validator = Map()
        assert validator.validate({})
        assert validator.validate({"key": "value"})
        assert validator.validate({"key": "value", "key2": "value2"})

        validator = Map({
            RequiredKey("key"): Str()
        })
        assert not validator.validate({})
        assert validator.validate({"key": "value"})
        assert not validator.validate({"key": 123})
        assert not validator.validate({"wrong-key": "value"})
        assert not validator.validate("string")

