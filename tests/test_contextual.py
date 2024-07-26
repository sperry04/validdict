import pytest
from validdict import Any
from validdict.contextual import ContextualValidator, CallbackValidator # objects under test


class TestContextualValidator:

    def test_contextual_validator_constructor(self):
        validator = ContextualValidator()
        assert isinstance(validator, ContextualValidator)
        assert repr(validator) == "ContextualValidator()"
        with pytest.raises(NotImplementedError):
            validator.validate("value")

    def test_contextual_validator_validation(self):
        assert ContextualValidator.validate_with_context(Any(), "value")
        with pytest.raises(TypeError):
            ContextualValidator.validate_with_context(None, "value")


class TestCallbackValidator:

    def test_callback_validator_constructor(self):
        callback = lambda context: Any()
        validator = CallbackValidator(callback)
        assert isinstance(validator, CallbackValidator)
        assert repr(validator) == "must pass callback '<lambda>'"

    test_context = {
        "key": "value"
    }

    def callback(self, cc:CallbackValidator.CallbackContext) -> Any:
        assert cc.context is self.test_context
        assert cc.comment == "test"
        return Any()

    def test_callback_validator_validation(self):
        validator = CallbackValidator(self.callback, comment="test")
        results = validator.validate({ "key": "value" }, context=self.test_context)
        assert results

    def test_nested_callback_validator_validation(self):
        validator = CallbackValidator(lambda context: CallbackValidator(self.callback, comment="test"))
        results = validator.validate({ "key": "value" }, context=self.test_context)
        assert results

    def test_broken_callback_validator_validation(self):
        validator = CallbackValidator(lambda context: None)
        results = validator.validate({ "key": "value" }, context=self.test_context)
        assert not results

