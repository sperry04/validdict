## Contextual Validators

from __future__ import annotations
from .results import Outcome, Result, ResultSet
from .validator import Validator
from .key import KeyValidator


class ContextualValidator(Validator):
    """
    Base class for validators that accept a context dict during validation
    """

    def validate(
        self, value: object, path: list[str] = None, context: object = None
    ) -> Result | ResultSet:
        """
        abstract validation method
        :param value:       the value to validate
        :param path:        list of parent keys for nested/compound structures
        :param context:     the dict the validation is occurring against
        :return:            Result or ResultSet of the validation
        """
        raise NotImplementedError(self)

    @staticmethod
    def validate_with_context(
        validator: Validator | ContextualValidator,
        value: object,
        path: list[str] = None,
        context: object = None,
    ) -> Result | ResultSet:
        """
        Helper method that wraps a validator and properly validates with context if possible
        """
        assert isinstance(validator, Validator), "Attempt to validate_with_context a non-Validator"
        if isinstance(validator, ContextualValidator):
            return validator.validate(value=value, path=path, context=context)
        return validator.validate(value=value, path=path)


class CallbackValidator(ContextualValidator, KeyValidator):
    """
    Validates a value by executing a callback/lambda that returns the actual Validator to use at validation time
    - the callback is provided the current context in order to allow referencing other values within the dict
    - use caution when using this as a KeyValidator as callback implementations MUST resolve to a KeyValidator
      that does not collide with another key!  Keys MUST be unique in a map or document validation will be inconsistent!
    """

    class CallbackContext:
        """
        Inner class that represents the full context data passed to the callback
        """

        def __init__(
            self,
            value: object,
            context: object,
            path: list[str],
            valid_outcome: Outcome,
            invalid_outcome: Outcome,
            comment: str,
        ) -> None:
            self.value = value
            self.context = context
            self.path = path
            self.valid_outcome = valid_outcome
            self.invalid_outcome = invalid_outcome
            self.comment = comment

    def __init__(
        self,
        callback: callable[[CallbackContext], Validator],
        *,
        valid_outcome: Outcome = Outcome.PASS,
        invalid_outcome: Outcome = Outcome.FAIL,
        comment: str = "",
    ) -> None:
        """
        Creates a Validator that will use a callback to decide how to validate a value
        """
        super().__init__(
            valid_outcome=valid_outcome, invalid_outcome=invalid_outcome, comment=comment
        )
        self.callback = callback

    def __repr__(self) -> str:
        """
        String representation of this validator
        """
        return f"must pass callback '{self.callback.__name__}'"

    def validate(
        self, value: object, path: list[str] = None, context: object = None
    ) -> Result | ResultSet:
        """
        Validates a value by allowing user code to decide how to validate it at runtime
        :param value:       the value to validate
        :param path:        list of parent keys for nested/compound structures
        :param context:     the dict the validation is occurring against
        :return:            Result or ResultSet of the validation
        """
        if callable(self.callback):  # if the callback is usable
            # capture the full context for the callback
            cc = CallbackValidator.CallbackContext(
                value, context, path, self.valid_outcome, self.invalid_outcome, self.comment
            )
            # call the callback and get the user's selection of a validator
            validator = self.callback(cc)
            if isinstance(validator, ContextualValidator):
                # if it's also a ContextualValidator, make sure to pass along the context
                return validator.validate(value=value, path=path, context=context)
            if isinstance(validator, Validator):
                return validator.validate(value=value, path=path)  # otherwise just validate
        # in the case that there was no callback or a non-Validator was returned, return invalid Result
        return Result(outcome=self.invalid_outcome, value=value, path=path, validator=self)
