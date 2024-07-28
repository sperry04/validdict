## Validation Results

# TODO: add "PARENT" outcome that would inherit the parent's outcome for nested validators
#       not sure how to handle that since the parent/child relationship is not explicit,
#       but maybe during the generation of a ResultSet, as Results are chained together there
#       could be some sort of hand-off of valid/invalid Outcomes?
# IDEA: since ResultSets are flat without a parent/child relationship, the path in each
#       Result would be the only way to find parents.  Instead of building/maintaining a 
#       tree, we could just index each path into a dict of path->outcome and scan the
#       dict by removing breadcrumbs until there's a non-Outcome.PARENT value, or we hit the
#       root with defaults of PASS/FAIL for valid/invalid.
# BUT:  how to handle that the path->outcome mapping should be per-ResultSet (maybe?) but the
#       paths/outcomes are in the Result, and the Result has no relationship to one or more
#       ResultSets that might contain it?  I don't want to add in some weird reference to each
#       Result... and it can't be a global lookup because there could be two schemas with 
#       matching key names that would cause path collisions.

from __future__ import annotations
from enum import Enum
from .helpers import format_path


class Outcome(Enum):
    """
    Enumeration of possible validation outcomes
    """
    NONE = 'NONE'
    PASS = 'PASS'
    FAIL = 'FAIL'
    WARN = 'WARN'
    INFO = 'INFO'


class OutcomeProvider(object):
    """
    Base class for objects that encapsulate valid and invalid outcomes
    """
    valid_outcome:Outcome
    invalid_outcome:Outcome
    comment:str

    def __init__(self, *,valid_outcome:Outcome=Outcome.PASS, invalid_outcome:Outcome=Outcome.FAIL, comment: str = "") -> None:
        """
        constructor
        :param valid_outcome:       the outcome to apply to the result when the value is valid, default: PASS
        :param invalid_outcome:     the outcome to apply to the result when the value is invalid, default: FAIL
        :param comment:             comment associated with the possible outcomes
        """
        if not isinstance(valid_outcome, Outcome):
            raise TypeError("valid_outcome must be an Outcome")
        if not isinstance(invalid_outcome, Outcome):
            raise TypeError("invalid_outcome must be an Outcome")
        self.valid_outcome = valid_outcome
        self.invalid_outcome = invalid_outcome
        self.comment = comment


class FixedOutcome(OutcomeProvider):
    """
    Represents a fixed outcome without any validation  
    """
    def __init__(self, outcome:Outcome=Outcome.NONE, is_valid:bool=True, message:str="", comment:str="") -> None:
        """
        constructor
        :param outcome:     the fixed outcome to apply to the result
        :param comment:     comment associated with the outcome
        """
        super().__init__(valid_outcome=outcome if is_valid else Outcome.NONE, invalid_outcome=Outcome.NONE if is_valid else outcome, comment=comment)
        self.message = message

    def __repr__(self) -> str:
        """
        string representation of the outcome
        :return:    indented path/key prefix, the validated value, the validator description, and the outcome
        """
        return self.message


class Result(object):
    """
    Encapsulates results of a scalar validation
    """
    _outcome:Outcome
    value:object
    path:list[str]
    validator:OutcomeProvider|str
    message:str
    comment:str

    def __init__(self, outcome:Outcome, value:object, path:list[str], validator:OutcomeProvider=None) -> None:
        """
        constructor
        :param outcome:     the outcome of the validation: PASS, FAIL, etc.
        :param value:       the value that was was validated
        :param path:        list of parent keys for nested/compound structures
        :param validator:   the validator that validated the value and generated this result
        """
        if not isinstance(outcome, Outcome):
            raise TypeError("outcome must be an Outcome")
        if not (validator is None or isinstance(validator, OutcomeProvider)):
            raise TypeError("validator must be an OutcomeProvider")
        self._outcome = outcome
        self.value = value
        self.path = path
        self.validator = FixedOutcome(message="no validator") if validator is None else validator
        self.message = repr(self.validator)
        self.comment = "" if self.validator.comment is None or len(self.validator.comment) == 0 else f" # {self.validator.comment}"

    def __repr__(self) -> str:
        """
        string representation of the result
        :return:    indented path/key prefix, the validated value, the validator description, and the outcome
        """
        printable = self.value
        if isinstance(self.value, (dict, list)):
            printable = "<" + type(self.value).__name__ + ">"
        path = format_path(self.path, suffix=':').replace("(<value>)", f"('{printable}')")    
        return f"{path}'{printable}' {self.message} = '{self.outcome.name}'{self.comment}"

    def __or__(self, other:Result|ResultSet) -> ResultSet:
        """
        logical or operator
        :param other:       another validation result or result set to join together
        :return:            validation result set encapsulating both results        
        """
        return ResultSet(self, other)
    
    def __bool__(self) -> bool:
        """
        bool representation of the result
        :return:            True if the outcome matches the validator's valid_outcome AND doesn't match the validator's invalid_outcome, False otherwise
        """
        # check both valid and invalid outcomes to handle a situation where valid == invalid in the validator
        return (
            (self.outcome == self.validator.valid_outcome or self.validator.valid_outcome == Outcome.NONE)
            and 
            (self.outcome != self.validator.invalid_outcome or self.validator.invalid_outcome == Outcome.NONE)
        )
        
    @property
    def outcome(self) -> Outcome:
        """
        :return:    the outcome this result represents
        """
        # TODO: can this lookup an outcome from a parent based on the validator's path?
        return self._outcome


class ResultSet(object):
    """
    Encapsulates results of a compound validation
    """
    _results:list[Result]

    def __init__(self, *results:object) -> None:
        """
        constructor
        :param results:     args list of results or result sets to include in this set
        """
        self._results = []
        self.add_results(*results)

    def __repr__(self) -> str:
        """
        string representation of the result set
        :return:            newline-delimited list of the results in the set
        """
        if len(self._results) == 0:
            return "No Results"
        return '\n'.join([ repr(result) for result in self._results ] )

    def __or__(self, other:Result|ResultSet) -> ResultSet:
        """
        logical or operator
        :param other:       another validation result or result set to join together
        :return:            validation result set encapsulating both results        
        """
        return ResultSet(self, other)
    
    def __bool__(self) -> bool:
        """
        bool representation of the result
        :return:        True if all the results in the set are also __bool__ True, False otherwise
        """
        return all(self._results)
    
    def __len__(self) -> int:
        """
        :return:            the total count of results in the set
        """
        return len(self._results)
    
    def __iter__(self) -> Result:     
        """
        :return:            iterator for the results in the set
        """
        return iter(self._results)
    
    def add_results(self, *results:object) -> None:
        """
        add results to the set
        :param results:     args list of results or result sets to add to the set
        """
        if not all(isinstance(result, (Result, ResultSet)) for result in results):
            raise TypeError("added results must be either a Result or a ResultSet")
        for result in results:
            if isinstance(result, ResultSet):
                self._results.extend(result._results)
            else:
                self._results.append(result)

    # def get_results(self, *filters:Outcome) -> list[Result]:
    #     """
    #     Gets a list of results from the set that match the provided filters
    #     :param filters:     args list of outcomes to filter the results, use no filters for all results
    #     :return:            list of the results with the matching filters
    #     """
    #     if not all(isinstance(filter, Outcome) for filter in filters):
    #         raise TypeError("filter(s) must be Outcome enums")
    #     if len(filters) == 0:
    #         return self._results
    #     return [ result for result in self._results if result.outcome in filters ]
    
    def filter(self, *filters:Outcome) -> ResultSet:
        """
        Filters the results in the set by the provided filters
        :param filters:     args list of outcomes to filter the results, use no filters for all results
        :return:            new result set containing only the results with the matching filters
        """
        if not all(isinstance(filter, Outcome) for filter in filters):
            raise TypeError("filter(s) must be Outcome enums")
        if len(filters) == 0:
            return self
        return ResultSet(*(result for result in self._results if result.outcome in filters))

    # @property
    # def result_count(self) -> int:
    #     """
    #     :return:            the total count of results in the set
    #     """
    #     return len(self.get_results(Outcome.PASS, Outcome.INFO, Outcome.WARN, Outcome.FAIL))

    # @property
    # def pass_count(self) -> int:
    #     """
    #     :return:            the total count of PASS results in the set
    #     """
    #     return len(self.get_results(Outcome.PASS))
    
    # @property
    # def fail_count(self) -> int:
    #     """
    #     :return:            the total count of FAIL results in the set
    #     """
    #     return len(self.get_results(Outcome.FAIL))
    
    # @property
    # def warn_count(self) -> int:
    #     """
    #     :return:            the total count of WARN results in the set
    #     """
    #     return len(self.get_results(Outcome.WARN))
    
    # @property
    # def info_count(self) -> int:
    #     """
    #     :return:            the total count of INFO results in the set
    #     """
    #     return len(self.get_results(Outcome.INFO))
