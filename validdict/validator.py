# Validator Base Class

from __future__ import annotations
from .results import Outcome, OutcomeProvider, Result, ResultSet
from .helpers import extend_path
from .locator import Locator


class Validator(OutcomeProvider):
    """
    Base class for all validators
    """

    def __init__(self, *, valid_outcome:Outcome=Outcome.PASS, invalid_outcome:Outcome=Outcome.FAIL, comment:str="") -> None:
        """
        constructor
        :param valid_outcome:       the outcome to apply to the result when the value is valid, default: PASS
        :param invalid_outcome:     the outcome to apply to the result when the value is invalid, default: FAIL
        """
        if valid_outcome == Outcome.NONE or invalid_outcome == Outcome.NONE:
            raise ValueError("valid_outcome and invalid_outcome cannot be Outcome.NONE")
        super().__init__(valid_outcome=valid_outcome, invalid_outcome=invalid_outcome, comment=comment)
        self.repr = self.__class__.__name__ + "()"

    def __repr__(self) -> str:
        """
        string representation of the validator
        :return:            the string representation of the validator
        """
        return self.repr

    def __or__(self, other:Validator) -> Or:
        """
        logical or operator
        :param other:       the other validator to join with
        :return:            Or validator that encapsulates this and the other validator
        """
        return Or(self, other)

    def validate(self, value:object, path:list[str]=None) -> Result|ResultSet:
        """
        abstract validation method
        :param value:       the value to validate
        :param path:        list of parent keys for nested/compound structures
        :return:            Result or ResultSet of the validation
        """
        raise NotImplementedError(self)

    @staticmethod
    def for_value(value:object, *, valid_outcome:Outcome=Outcome.PASS, invalid_outcome:Outcome=Outcome.FAIL, comment:str="") -> Validator:
        """
        Creates a validator matching the type of the value found in the Locator
        :param value:           the value to base the new validator on
        :return:                Validator that will exclusively validate the provided value
        """
        if isinstance(value, Validator):
            return value      
        
        validator_type = Locator.lookup(type(value)) # lookup the validator by the type of the value
        if isinstance(validator_type, type) and issubclass(validator_type, Validator):
            return validator_type(value, valid_outcome=valid_outcome, invalid_outcome=invalid_outcome, comment=comment)
        raise TypeError(f"No known Validator for type '{type(value).__name__}'")


class Or(Validator):
    """
    Represents a logical OR group of validators that can be applied to a value
    - Created when other validators are |'d together
    """

    def __init__(self, *validators:Validator, valid_outcome:Outcome=Outcome.PASS, invalid_outcome:Outcome=Outcome.FAIL, comment:str="") -> None:
        """
        constructor
        :param validators:  args list of validators to add to the set
        """
        if len(validators) < 2:
            raise TypeError("Or must encapsulate at least 2 validators")
        if not all(isinstance(validator, Validator) for validator in validators):
            raise TypeError("validators must be of type Validator")
        super().__init__(
            valid_outcome=valid_outcome, invalid_outcome=invalid_outcome, comment=comment
        )
        self.validators: list[Validator] = []
        for validator in validators:
            if isinstance(validator, Or):
                self.validators.extend(validator.validators)
            else:
                self.validators.append(validator)

    def _get_sub_validator_repr(self, validator: Validator) -> str:
        """
        private helper method that returns a consistent shortened name for an Or'd validator
        """
        return validator.__class__.__name__ + "(...)"

    def __repr__(self) -> str:
        """
        string representation of the validator
        :return:            list of the encapsulated validators
        """
        validators_string = " | ".join(
            self._get_sub_validator_repr(validator) for validator in self.validators
        )
        return f"must be {validators_string}"

    def validate(self, value: object, path: list[str] = None) -> ResultSet:
        """
        validates a value against two or more validators
        :param value:       the value to validate
        :param path:        list of parent keys for nested/compound structures
        :return:            validation result set, when invalid it contains all the failing results
        """
        results = ResultSet()
        for validator in self.validators:
            # validate the value with the sub-validator
            result = validator.validate(value, path=extend_path(path, f"Or({self._get_sub_validator_repr(validator)})"))
            if result:
                # if any sub-validator passes, the overall result is valid
                return ResultSet(Result(outcome=self.valid_outcome, value=value, path=path, validator=self), result)
            results.add_results(result)
        return ResultSet(Result(self.invalid_outcome, value=value, path=path, validator=self), results)


class Any(Validator):
    """
    Validates any value
    """

    def __repr__(self) -> str:
        """
        string representation of the validator
        :return:            "may be anything"
        """
        return "may be anything"

    def validate(self, value: object, path: list[str] = None) -> Result:
        """
        validates anything
        :param value:       the value to validate
        :param key:         the key associated with the value
        :param path:        list of parent keys for nested/compound structures
        :return:            validation result with the validation outcome
        """
        return Result(outcome=self.valid_outcome, value=value, path=path, validator=self)
