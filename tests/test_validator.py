import pytest
from validdict import Str, Num, Bool
from validdict.validator import ResultSet, Result
from validdict.validator import Validator, Or, Any # objects under test


class TestValidator:

    def test_validator_constructor(self):
        validator = Validator()
        assert isinstance(validator, Validator)
        assert repr(validator) == "Validator()"

    def test_validator_or_operator(self):
        v1 = Validator()
        v2 = Validator()
        or_validator = v1 | v2
        assert isinstance(or_validator, Or)

    def test_validator_validate(self):
        v = Validator()
        with pytest.raises(NotImplementedError):
            v.validate(None)

    def test_for_value(self):
        v = Validator.for_value("A")
        assert isinstance(v, Str)
        v = Validator.for_value(1234)
        assert isinstance(v, Num)
        v = Validator.for_value(True)
        assert isinstance(v, Bool)
        v = Validator.for_value(Any())
        assert isinstance(v, Any)
        with pytest.raises(TypeError):
            Validator.for_value(None)


class TestOr:

    def test_or_constructor(self):
        or_validator = Or(Str(), Num())
        assert isinstance(or_validator, Or)
        assert repr(or_validator) == "must be Str() | Num()"
        results = or_validator.validate("A")
        assert isinstance(results, ResultSet)

        or_validator = Str() | Num()
        assert isinstance(or_validator, Or)
        assert repr(or_validator) == "must be Str() | Num()"
        results = or_validator.validate("A")
        assert isinstance(results, ResultSet)

        or_validator = Str() | Num() | Bool()
        assert isinstance(or_validator, Or)
        assert repr(or_validator) == "must be Str() | Num() | Bool()"
        results = or_validator.validate("A")
        assert isinstance(results, ResultSet)

        or_validator = Str() | Num() | Or(Bool(), Str())
        assert isinstance(or_validator, Or)
        assert repr(or_validator) == "must be Str() | Num() | Bool() | Str()"
        results = or_validator.validate("A")
        assert isinstance(results, ResultSet)

        with pytest.raises(TypeError):
            Or()

        with pytest.raises(TypeError):
            Or(Num())

        with pytest.raises(TypeError):
            Or(Num(), "string")

    def test_or_validation(self):
        assert (Str() | Num()).validate("A")
        assert (Str("A") | Num(1234) | Bool(False)).validate("A")
        assert (Str("A") | Num(1234) | Bool(False)).validate(1234)
        assert not (Str("A") | Num(1234) | Bool(False)).validate(True)


class TestAny:

    def test_any_constructor(self):
        any_validator = Any()
        assert repr(any_validator) == "may be anything"
        result = any_validator.validate(None)
        assert isinstance(result, Result)

    def test_any_validation(self):
        assert Any().validate(None)
        assert Any().validate("A")
        assert Any().validate(1234)
        assert Any().validate(1234.5678)
        assert Any().validate(True)
        assert Any().validate({})
        assert Any().validate([])
