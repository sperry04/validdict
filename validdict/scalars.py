# Scalar Validators

from re import Pattern, compile as compile_pattern
from .results import Outcome, Result
from .validator import Validator
from .helpers import format_sequence


class ScalarValidator(Validator):
    """
    Base class for validating scalar values
    - validates against specific types
    - validates against specific values
    """
    accepted_types:tuple
    accepted_values:tuple

    def __init__(self, accepted_types:tuple, accepted_values:tuple, *, valid_outcome:Outcome=Outcome.PASS, invalid_outcome:Outcome=Outcome.FAIL, comment:str="") -> None:
        """
        constructor
        :param accepted_types:      tuple of types that will be accepted by the validator
        :param accepted_values:     tuple of exact values that will be accepted by the validator
        :param valid_outcome:       the outcome to apply to the result when the value is valid, default: PASS
        :param invalid_outcome:     the outcome to apply to the result when the value is invalid, default: FAIL
        """
        super().__init__(valid_outcome=valid_outcome, invalid_outcome=invalid_outcome, comment=comment)
        assert isinstance(accepted_types, tuple) and all(type(t) == type for t in accepted_types), "accepted_types must be a tuple of types"
        assert isinstance(accepted_values, tuple) and all(type(accepted_value) in accepted_types for accepted_value in accepted_values), "accepted_values must be a tuple of values of accepted_types"
        self.accepted_types:tuple = accepted_types
        self.accepted_values:tuple = accepted_values

    def __repr__(self) -> str:
        """
        string representation of the validator
        :return:            accepted type(s) and (optional) accepted value(s) for the validator
        """
        return f"must be type {format_sequence(self.accepted_types, prefix="in (", suffix=")")}" + (f" with value {format_sequence(self.accepted_values, prefix="one of (", suffix=")")}" if len(self.accepted_values) > 0 else '')

    def validate(self, value:object, path:list[str]=None) -> Result:
        """
        validates a scalar value
        :param value:       the value to validate
        :param path:        list of parent keys for nested/compound structures
        :return:            validation result with the validation outcome
        """
        if (type(value) in self.accepted_types                                                      # can't use isinstance() because booleans are ints
            and (self.accepted_values == () or value in self.accepted_values)
        ):
            outcome = self.valid_outcome
        else:
            outcome = self.invalid_outcome
        return Result(outcome=outcome, value=value, path=path, validator=self)


class Str(ScalarValidator):
    """
    Validates a string value
    """
    
    def __init__(self, *accepted_values:str, case_sensitive:bool=True, valid_outcome:Outcome=Outcome.PASS, invalid_outcome:Outcome=Outcome.FAIL, comment:str="") -> None:
        self.case_sensitive:bool = case_sensitive
        if self.case_sensitive:
            super().__init__((str,), accepted_values, valid_outcome=valid_outcome, invalid_outcome=invalid_outcome, comment=comment)
        else:
            # we're going to convert all the accepted_values to lowercase for later validation calls
            assert isinstance(accepted_values, tuple) and all(isinstance(accepted_value, str) for accepted_value in accepted_values), "accepted_values must be a tuple strings"
            super().__init__((str,), tuple(av.lower() for av in accepted_values), valid_outcome=valid_outcome, invalid_outcome=invalid_outcome, comment=comment)

    def validate(self, value: object, path:list[str]=None) -> Result:
        if self.case_sensitive:                                                                     # if we're case_sensitive...
            return super().validate(value=value, path=path)                                         # validate normally
        return super().validate(value.lower() if "lower" in dir(value) else value, path=path)       # otherwise, validate a lowercase value against the lowercase accepted_values saved earlier


class Num(ScalarValidator):
    """
    Validates a numerical (int or float) value
    """

    def __init__(self, *accepted_values:object, valid_outcome:Outcome=Outcome.PASS, invalid_outcome:Outcome=Outcome.FAIL, comment:str="") -> None:
        super().__init__((int, float), accepted_values, valid_outcome=valid_outcome, invalid_outcome=invalid_outcome, comment=comment)


class Bool(ScalarValidator):
    """
    Validates a boolean value
    """

    def __init__(self, *accepted_values:bool, valid_outcome:Outcome=Outcome.PASS, invalid_outcome:Outcome=Outcome.FAIL, comment:str="") -> None:
        super().__init__((bool,), accepted_values, valid_outcome=valid_outcome, invalid_outcome=invalid_outcome, comment=comment)


class Regex(ScalarValidator):
    """
    Validates a string value via a regular expression
    """
    patterns:Pattern

    def __init__(self, *accepted_values:Pattern|str, valid_outcome:Outcome=Outcome.PASS, invalid_outcome:Outcome=Outcome.FAIL, comment:str="") -> None:
        super().__init__((str,), (), valid_outcome=valid_outcome, invalid_outcome=invalid_outcome, comment=comment)
        self.patterns:Pattern = tuple((p if isinstance(p, Pattern) else compile_pattern(p) for p in accepted_values))
        assert all(type(pattern) in (str, Pattern) for pattern in self.patterns)

    def __repr__(self) -> str:
        return f"must be type {format_sequence(self.accepted_types, prefix="in (", suffix=")")}" + (f" with value matching {format_sequence([ pattern.pattern for pattern in self.patterns ], prefix="one of (", suffix=")")}" if len(self.patterns) > 0 else '')

    def validate(self, value: object, path:list[str]=None) -> Result:
        rval = Result(outcome=self.invalid_outcome, value=value, path=path, validator=self)
        if super().validate(value):
            for pattern in self.patterns:
                match = pattern.fullmatch(value) is not None
                if match:
                    rval = Result(outcome=self.valid_outcome, value=value, path=path, validator=self)
                    break # out of for each pattern
        return rval
