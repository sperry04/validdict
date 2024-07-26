# Scalar Validators

from __future__ import annotations
from re import Pattern, compile as compile_pattern
from .results import Outcome, Result
from .validator import Validator
from .helpers import format_sequence
from .locator import Locator


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
        :param accepted_values:     tuple of exact values or range() of values that will be accepted by the validator
        :param valid_outcome:       the outcome to apply to the result when the value is valid, default: PASS
        :param invalid_outcome:     the outcome to apply to the result when the value is invalid, default: FAIL
        """
        if not isinstance(accepted_types, tuple) or not all(type(t) == type for t in accepted_types):
            raise TypeError("accepted_types must be a tuple of types")
        if not isinstance(accepted_values, tuple) or not all(type(accepted_value) in accepted_types or isinstance(accepted_value, range) for accepted_value in accepted_values):
            raise TypeError("accepted_values must be a tuple of values of accepted_types")
        super().__init__(valid_outcome=valid_outcome, invalid_outcome=invalid_outcome, comment=comment)
        self.accepted_types:tuple = accepted_types
        self.accepted_values:tuple = accepted_values
        self.repr = f"must be type {format_sequence(self.accepted_types, prefix='in (', suffix=')')}" + (f" with value {format_sequence(self.accepted_values, prefix='one of (', suffix=')')}" if len(self.accepted_values) > 0 else '')

    def validate(self, value:object, path:list[str]=None) -> Result:
        """
        validates a scalar value
        :param value:       the value to validate
        :param path:        list of parent keys for nested/compound structures
        :return:            validation result with the validation outcome
        """
        if (type(value) in self.accepted_types                                                      # can't use isinstance() because booleans are ints
            and (self.accepted_values == () 
                 or value in [ accepted_value for accepted_value in self.accepted_values if not isinstance(accepted_value, range) ] 
                 or any(value in accepted_range for accepted_range in self.accepted_values if isinstance(accepted_range, range))
            )
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
            if not isinstance(accepted_values, tuple) or not all(isinstance(accepted_value, str) for accepted_value in accepted_values):
                raise TypeError("accepted_values must be a tuple strings")
            super().__init__((str,), tuple(av.lower() for av in accepted_values), valid_outcome=valid_outcome, invalid_outcome=invalid_outcome, comment=comment)

    def validate(self, value: object, path:list[str]=None) -> Result:
        if self.case_sensitive:                                                                     # if we're case_sensitive...
            return super().validate(value=value, path=path)                                         # validate normally
        return super().validate(value.lower() if "lower" in dir(value) else value, path=path)       # otherwise, validate a lowercase value against the lowercase accepted_values saved earlier

# register the Str validator with the Locator to validate str objects
Locator.register(str, Str)


class Num(ScalarValidator):
    """
    Validates a numerical (int or float) value
    """

    def __init__(self, *accepted_values:object, gt:object=None, gte:object=None, lt:object=None, lte:object=None, valid_outcome:Outcome=Outcome.PASS, invalid_outcome:Outcome=Outcome.FAIL, comment:str="") -> None:
        """
        constructor
        :param accepted_values:     tuple of exact values or range() of values that will be accepted by the validator
        :param gt:                  the value must be greater than this value
        :param gte:                 the value must be greater than or equal to this value
        :param lt:                  the value must be less than this value
        :param lte:                 the value must be less than or equal to this value
        :param valid_outcome:       the outcome to apply to the result when the value is valid, default: PASS
        :param invalid_outcome:     the outcome to apply to the result when the value is invalid, default: FAIL
        """
        super().__init__((int, float), accepted_values, valid_outcome=valid_outcome, invalid_outcome=invalid_outcome, comment=comment)
        self.gt:object = gt 
        self.gte:object = gte
        self.lt:object = lt
        self.lte:object = lte

        # build the repr string
        self.repr = f"must be type {format_sequence(self.accepted_types, prefix='in (', suffix=')')}"
        relational = any(operator is not None for operator in (gt, gte, lt, lte))                   # true if any of the relational operators have a target value
        if len(accepted_values) > 0 or relational:                                                  # if there are accepted_values or relational operators...
            self.repr += " with value "                                                             # add the value clause
            if len(accepted_values) > 0:                                                            # if there are accepted_values...
                self.repr += f"{format_sequence(self.accepted_values, prefix='one of (', suffix=')')}" # add the accepted_values
                if relational:                                                                      # if there are relational operators...
                    self.repr += " and "                                                            # add an 'and' separator
            if relational:                                                                          # if there are relational operators...
                operators = []
                if gt is not None: operators.append(f'> {gt}')
                if gte is not None: operators.append(f'>= {gte}')
                if lt is not None: operators.append(f'< {lt}')
                if lte is not None: operators.append(f'<= {lte}')
                self.repr += f"{format_sequence(operators, separator=' and ')}"                     # add the relational operators

    def validate(self, value: object, path:list[str]=None) -> Result:
        rval = Result(outcome=self.invalid_outcome, value=value, path=path, validator=self)
        if super().validate(value).outcome == self.valid_outcome:
            if (self.lt is None or value < self.lt) and (self.lte is None or value <= self.lte) and (self.gt is None or value > self.gt) and (self.gte is None or value >= self.gte):
                rval = Result(outcome=self.valid_outcome, value=value, path=path, validator=self)
        return rval


# register the Num validator with the Locator to validate int and float objects
Locator.register([int, float], Num)


class Bool(ScalarValidator):
    """
    Validates a boolean value
    """

    def __init__(self, *accepted_values:bool, valid_outcome:Outcome=Outcome.PASS, invalid_outcome:Outcome=Outcome.FAIL, comment:str="") -> None:
        super().__init__((bool,), accepted_values, valid_outcome=valid_outcome, invalid_outcome=invalid_outcome, comment=comment)

# register the Bool validator with the Locator to validate bool objects
Locator.register(bool, Bool)


class Regex(ScalarValidator):
    """
    Validates a string value via a regular expression
    """
    patterns:Pattern

    def __init__(self, *accepted_values:Pattern|str, valid_outcome:Outcome=Outcome.PASS, invalid_outcome:Outcome=Outcome.FAIL, comment:str="") -> None:
        if not all(type(accepted_value) in (str, Pattern) for accepted_value in accepted_values):
            raise TypeError("accepted_values must be strings or compiled regex patterns")
        super().__init__((str,), (), valid_outcome=valid_outcome, invalid_outcome=invalid_outcome, comment=comment)
        self.patterns:Pattern = tuple((p if isinstance(p, Pattern) else compile_pattern(p) for p in accepted_values))
        self.repr = f"must be type {format_sequence(self.accepted_types, prefix='in (', suffix=')')}" + (f" with value matching {format_sequence([ pattern.pattern for pattern in self.patterns ], prefix='one of (', suffix=')')}" if len(self.patterns) > 0 else '')

    def validate(self, value: object, path:list[str]=None) -> Result:
        rval = Result(outcome=self.invalid_outcome, value=value, path=path, validator=self)
        if super().validate(value):
            for pattern in self.patterns:
                match = pattern.fullmatch(value) is not None
                if match:
                    rval = Result(outcome=self.valid_outcome, value=value, path=path, validator=self)
                    break # out of for each pattern
        return rval
