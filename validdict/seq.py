# Sequence Validator

from .results import Outcome, Result, ResultSet
from .scalars import Num
from .validator import Validator, Or
from .helpers import extend_path
from .locator import Locator


class Seq(Validator):
    """
    Validates that a sequence of items are of the required type(s)
    """

    def __init__(self, *validators:Validator, min_len:int=None, max_len:int=None, valid_outcome:Outcome=Outcome.PASS, invalid_outcome:Outcome=Outcome.FAIL, comment:str="") -> None:
        """
        constructor
        :param validators:      args list of validators that validate items in the list
        """
        if not all(isinstance(v, Validator) for v in validators):
            raise TypeError(f"validator(s) must be of type Validator")
        super().__init__(valid_outcome=valid_outcome, invalid_outcome=invalid_outcome, comment=comment)
        if len(validators) == 0:
            self.validator = None
        elif len(validators) == 1:
            self.validator = validators[0]
        else:
            self.validator = Or(*validators)
        self.min_len = Num(gte=min_len) if min_len is not None else None
        self.max_len = Num(lte=max_len) if max_len is not None else None

    def __repr__(self) -> str:
        """
        string representation of the validator
        :return:            includes optional list of the encapsulated validators
        """
        return "must be a sequence" + ("" if self.validator is None else f" like: [ {self.validator} ]")

    def validate(self, value:object, path:list[str]=None) -> ResultSet:
        """
        validates a sequence, makes sure value is a sequence and that each item in the sequence matches the sub-validators
        :param value:       the sequence to validate
        :param path:        list of parent keys for nested/compound structures
        :return:            validation result set containing the first passing result, or all the failing results
        """
        rval = ResultSet()
        if isinstance(value, (tuple, list)):
            rval.add_results(Result(outcome=self.valid_outcome, value=value, path=path, validator=self))
            if self.min_len is not None:
                rval.add_results(self.min_len.validate(len(value), path=extend_path(path, "min_len")))
            if self.max_len is not None:
                rval.add_results(self.max_len.validate(len(value), path=extend_path(path, "max_len")))
            if self.validator:
                item_index = 0
                for item in value:
                    rval.add_results(self.validator.validate(item, path=extend_path(path, "item_"+str(item_index))))
                    item_index += 1
        else:
            rval.add_results(Result(outcome=self.invalid_outcome, value=value, path=path, validator=self))
        return rval
    
# register the Seq validator with the Locator to validate list objects
Locator.register(list, Seq)
