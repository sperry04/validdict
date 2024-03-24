# Validator Base Class

from __future__ import annotations
from .results import Outcome, OutcomeProvider, Result, ResultSet
from .helpers import extend_path


class Validator(OutcomeProvider):
    """
    Base class for all validators
    """

    def __init__(
        self,
        *,
        valid_outcome: Outcome = Outcome.PASS,
        invalid_outcome: Outcome = Outcome.FAIL,
        comment: str = "",
    ) -> None:
        """
        constructor
        :param valid_outcome:       the outcome to apply to the result when the value is valid, default: PASS
        :param invalid_outcome:     the outcome to apply to the result when the value is invalid, default: FAIL
        """
        super().__init__(valid_outcome=valid_outcome, invalid_outcome=invalid_outcome, comment=comment)

    def __repr__(self) -> str:
        """
        string representation of the validator
        :return:            the class name of the validator
        """
        return self.__class__.__name__ + "()"

    def __or__(self, other:Validator) -> Or:
        """
        logical or operator
        :param other:       the other validator to join with
        :return:            Or validator that encapsulates this and the other validator
        """
        return Or(self, other)

    def validate(self, value:object, path:list[str]=None) -> Result | ResultSet:
        """
        abstract validation method
        :param value:       the value to validate
        :param path:        list of parent keys for nested/compound structures
        :return:            Result or ResultSet of the validation
        """
        raise NotImplementedError(self)


class Or(Validator):
    """
    Represents a logical OR group of validators that can be applied to a value
    - Created when other validators are |'d together
    """

    def __init__(
        self,
        *validators: Validator,
        valid_outcome: Outcome = Outcome.PASS,
        invalid_outcome: Outcome = Outcome.FAIL,
        comment: str = "",
    ) -> None:
        """
        constructor
        :param validators:  args list of validators to add to the set
        """
        assert len(validators) >= 2, "Or must encapsulate at least 2 validators"
        super().__init__(
            valid_outcome=valid_outcome, invalid_outcome=invalid_outcome, comment=comment
        )
        self.validators: list[Validator] = []
        for validator in validators:
            assert isinstance(validator, Validator), "validator(s) must be a Validator"
            if isinstance(validator, Or):
                self.validators.extend(validator.validators)
            else:
                self.validators.append(validator)

    def _get_sub_validator_repr(self, validator: Validator) -> str:
        """
        private helper method that returns a consistent shortened name for an Or'd validator
        """
        return validator.__class__.__name__ + "()"

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
        :return:            validation result set containing the first passing result, or all the failing results
        """
        results = ResultSet()
        outcome = self.invalid_outcome
        for validator in self.validators:
            result = validator.validate(
                value, path=extend_path(path, f"Or({self._get_sub_validator_repr(validator)})")
            )
            if result:
                # overwrite any previous failed results, we only need the one pass!
                results = ResultSet(result)
                outcome = self.valid_outcome
                break  # out of for each validator, we found a passing result
            else:
                results.add_results(result)  # capture the complete list of failures
                pass
        return ResultSet(Result(outcome=outcome, value=value, path=path, validator=self), results)


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
