# Key Validators

from __future__ import annotations
from .results import Outcome, Result
from .validator import Validator
from .scalars import ScalarValidator
from .helpers import format_sequence


class KeyValidator(Validator):
    """
    Base class for validating keys in a map
    """

    def __init__(self, accepted_name:str|ScalarValidator=None, *, valid_outcome:Outcome=Outcome.PASS, invalid_outcome:Outcome=Outcome.FAIL, comment:str="") -> None:
        """
        constructor
        :param accepted_name:       the valid key name, use None to accept anything
        :param valid_outcome:       the outcome to apply to the result when the value is valid, default: PASS
        :param invalid_outcome:     the outcome to apply to the result when the value is invalid, default: FAIL
        :param comment:             comment associated with the possible outcomes
        """
        super().__init__(valid_outcome=valid_outcome, invalid_outcome=invalid_outcome, comment=comment)
        if not (accepted_name is None
            or (isinstance(accepted_name, str) and len(accepted_name) > 0)
            or isinstance(accepted_name, ScalarValidator)
        ):
            raise TypeError(f"{self.__class__.__name__} accepted_name must be a non-zero length string, or a ScalarValidator")
        self.accepted_name = accepted_name
        self.repr = super().__repr__() if self.accepted_name is None else repr(self.accepted_name)

    def validate(self, value: object, path: list[str] = None) -> Result:
        """
        validate that the provided key name matches the validator's key name
        :param value:       the key name to validate
        :param path:        list of parent keys for nested/compound structures
        :return:            validation result with validation outcome
        """
        return Validator.for_value(
            value if self.accepted_name is None else self.accepted_name,
            valid_outcome=self.valid_outcome,
            invalid_outcome=self.invalid_outcome,
            comment=self.comment,
        ).validate(value, path=path)


class RequiredKey(KeyValidator):
    """
    Represents a required key in a map
    """
    def __init__(self, accepted_name:str, *, valid_outcome:Outcome=Outcome.PASS, invalid_outcome:Outcome=Outcome.FAIL, comment:str="") -> None:
        """
        constructor
        :param accepted_name:       the valid key name
        :param valid_outcome:       the outcome to apply to the result when the value is valid, default: PASS
        :param invalid_outcome:     the outcome to apply to the result when the value is invalid, default: FAIL
        :param comment:             comment associated with the possible outcomes
        """
        super().__init__(
            accepted_name=accepted_name, valid_outcome=valid_outcome, invalid_outcome=invalid_outcome, comment=comment
        )


class OptionalKey(KeyValidator):
    """
    Represents an optional key in a map
    """
    def __init__(self, accepted_name:str, *, valid_outcome:Outcome=Outcome.PASS, invalid_outcome:Outcome=Outcome.FAIL, comment:str="") -> None:
        """
        constructor
        :param accepted_name:       the valid key name
        :param valid_outcome:       the outcome to apply to the result when the value is valid, default: PASS
        :param invalid_outcome:     the outcome to apply to the result when the value is invalid, default: FAIL
        :param comment:             comment associated with the possible outcomes
        """
        super().__init__(
            accepted_name=accepted_name, valid_outcome=valid_outcome, invalid_outcome=invalid_outcome, comment=comment
        )


class OtherKeys(KeyValidator):
    """
    Represents an allowance for other keys in a map
    """
    def __init__(self, *, valid_outcome:Outcome=Outcome.PASS, invalid_outcome:Outcome=Outcome.FAIL, comment:str="") -> None:
        """
        constructor
        :param valid_outcome:       the outcome to apply to the result when the value is valid, default: PASS
        :param invalid_outcome:     the outcome to apply to the result when the value is invalid, default: FAIL
        :param comment:             comment associated with the possible outcomes
        """
        super().__init__(
            accepted_name=None, valid_outcome=valid_outcome, invalid_outcome=invalid_outcome, comment=comment
        )



class StartsWith(KeyValidator, ScalarValidator):
    """
    Represents an allowance for keys that start with a specific string
    CAUTION: Multiple inheritance!  This is a KeyValidator and ScalarValidator
    """

    def __init__(self, *accepted_prefixes, case_sensitive:bool=True, valid_outcome:Outcome=Outcome.PASS, invalid_outcome:Outcome=Outcome.FAIL, comment:str="") -> None:
        """
        constructor
        :param prefixes:            args list of accepted prefixes
        :param valid_outcome:       the outcome to apply to the result when the value is valid, default: PASS
        :param invalid_outcome:     the outcome to apply to the result when the value is invalid, default: FAIL
        """
        # skip the KeyValidator and ScalarValidator constructors, go straight to Validator's
        Validator.__init__(
            self, valid_outcome=valid_outcome, invalid_outcome=invalid_outcome, comment=comment
        )
        if not all(isinstance(accepted_prefix, str) and len(accepted_prefix) > 0 for accepted_prefix in accepted_prefixes):
            raise TypeError(f"{self.__class__.__name__} accepted_prefixes must be non-zero length strings")
        self.case_sensitive = case_sensitive
        if self.case_sensitive:
            self.accepted_prefixes = tuple(accepted_prefixes)
        else:
            # we're going to convert all the accepted_values to lowercase for later validation calls
            self.accepted_prefixes = tuple(ap.lower() for ap in accepted_prefixes)
        self.repr = f"must start with " + format_sequence(self.accepted_prefixes, prefix="one of (", suffix=")")

    def validate(self, value: object, path: list[str] = None) -> Result:
        """
        validate that the provided key name matches the validator's key name
        :param value:       the key name to validate
        :param path:        list of parent keys for nested/compound structures
        :return:            validation result with validation outcome
        """
        if isinstance(value, str):
            test_value = value if self.case_sensitive else value.lower()
            if any(test_value.startswith(ap) for ap in self.accepted_prefixes):
                return Result(outcome=self.valid_outcome, value=value, path=path, validator=self)
        return Result(outcome=self.invalid_outcome, value=value, path=path, validator=self)
