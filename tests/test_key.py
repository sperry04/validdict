import pytest
from validdict import Schema, Any, Num, Outcome
from validdict import RequiredKey, OptionalKey, OtherKeys, StartsWith # objects under test


class TestKeyValidators:

    def test_key_constructor(self):
        """
        Tests the constructors and __repr__() methods of the key classes
        - Asserts that the instances are of the correct type
        - Asserts that the __repr__() method generates the expected output
        """
        required_key = RequiredKey("name")
        assert isinstance(required_key, RequiredKey)
        assert repr(required_key) == "'name'"

        required_key = RequiredKey(Num(100))
        assert isinstance(required_key, RequiredKey)
        assert repr(required_key) == "must be type in ('int', 'float') with value '100'"

        optional_key = OptionalKey("age")
        assert isinstance(optional_key, OptionalKey)
        assert repr(optional_key) == "'age'"

        other_keys = OtherKeys()
        assert isinstance(other_keys, OtherKeys)
        assert repr(other_keys) == "OtherKeys()"

        starts_with = StartsWith("prefix_")
        assert isinstance(starts_with, StartsWith)
        assert repr(starts_with) == "must start with 'prefix_'"

        starts_with = StartsWith("PREFIX_", case_sensitive=False)
        assert isinstance(starts_with, StartsWith)
        assert repr(starts_with) == "must start with 'prefix_'"

        with pytest.raises(TypeError):
            RequiredKey(100)

        with pytest.raises(TypeError):
            RequiredKey("")

    def test_required_key(self):
        """
        Tests a schema with one required key
        - Asserts that the schema passes when the key is present
        - Asserts that the schema fails when the key is missing
        - Asserts that the schema fails when there are keys with unknown names
        """
        schema = Schema(
            {
                RequiredKey("name"): Any()
            }
        )
        results = schema.validate({"name": "John"})
        assert len(results.filter(Outcome.FAIL)) == 0
        assert results

        results = schema.validate({})
        assert len(results.filter(Outcome.FAIL)) == 1
        assert not results

        results = schema.validate({"age": 25})
        assert len(results.filter(Outcome.FAIL)) == 2
        assert not results

        results = schema.validate({"name": "John", "age": 25})
        assert len(results.filter(Outcome.FAIL)) == 1
        assert not results

    def test_optional_key(self):
        """
        Tests a schema with one optional key
        - Asserts that the schema passes when the key is present
        - Asserts that the schema passes when the key is missing
        - Asserts that the schema fails when there are keys with unknown names
        """
        schema = Schema(
            {
                OptionalKey("name"): Any()
            }
        )

        results = schema.validate({"name": "John"})
        assert len(results.filter(Outcome.FAIL)) == 0
        assert results

        results = schema.validate({})
        assert len(results.filter(Outcome.FAIL)) == 0
        assert results

        results = schema.validate({"age": 25})
        assert len(results.filter(Outcome.FAIL)) == 1
        assert not results

        results = schema.validate({"name": "John", "age": 25})
        assert len(results.filter(Outcome.FAIL)) == 1
        assert not results

    def test_other_keys(self):
        """
        Tests a schema with OtherKeys allowed
        - Asserts that the schema passes when no keys are present
        - Asserts that the schema passes when any keys are present
        """
        schema = Schema({
            OtherKeys(): Any()
        })

        results = schema.validate({})
        assert len(results.filter(Outcome.FAIL)) == 0
        assert results

        results = schema.validate({"name": "John"})
        assert len(results.filter(Outcome.FAIL)) == 0
        assert results

        results = schema.validate({"age": 25})
        assert len(results.filter(Outcome.FAIL)) == 0
        assert results

        results = schema.validate({"name": "John", "age": 25})
        assert len(results.filter(Outcome.FAIL)) == 0
        assert results

    def test_starts_with(self):
        """
        Tests a schema with keys that start with a prefix
        - Asserts that the schema passes when all keys start with the prefix
        - Asserts that the schema fails when any keys do not start with the prefix
        """
        schema = Schema({
            StartsWith("prefix_"): Any()
        })

        results = schema.validate({"prefix_name": "John"})
        assert len(results.filter(Outcome.FAIL)) == 0
        assert results

        results = schema.validate({"name": "John"})
        assert len(results.filter(Outcome.FAIL)) == 1
        assert not results

        results = schema.validate({"prefix_age": 25})
        assert len(results.filter(Outcome.FAIL)) == 0
        assert results

        results = schema.validate({"PREFIX_age": 25})
        assert len(results.filter(Outcome.FAIL)) == 1
        assert not results

        with pytest.raises(TypeError):
            StartsWith(None)

        with pytest.raises(TypeError):
            StartsWith("")

    def test_case_insensitive_starts_with(self):
        """
        Tests a schema with keys that start with a prefix
        - Asserts that the schema passes when all keys start with the prefix
        - Asserts that the schema fails when any keys do not start with the prefix
        """
        schema = Schema({
            StartsWith("prefix_", case_sensitive=False): Any()
        })

        results = schema.validate({"PREFIX_name": "John"})
        assert len(results.filter(Outcome.FAIL)) == 0
        assert results

        results = schema.validate({"name": "John"})
        assert len(results.filter(Outcome.FAIL)) == 1
        assert not results

        results = schema.validate({"prefix_age": 25})
        assert len(results.filter(Outcome.FAIL)) == 0
        assert results
