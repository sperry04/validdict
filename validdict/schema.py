# Schema validation wrapper

from .results import Outcome, Result, ResultSet
from .validator import Validator
from .scalars import Str, Bool, Num
from .seq import Seq
from .map import Map
from .contextual import ContextualValidator

import logging

logger = logging.getLogger(__name__)

class Schema:
    """
    Validation Schema    
    """
    def __init__(self, schema: object) -> None:
        self.schema = Validator.for_value(schema)

    def validate(
        self,
        document: object,
        *outcome_filters: Outcome,
        suppress_logging: bool = False,
        logging_config: dict = None,
        context: object = None
    ) -> ResultSet:
        # if there's no explicit context, use the document itself
        if context is None:
            context = document
        # validate the document with context
        rval = ContextualValidator.validate_with_context(self.schema, document, context=context)
        if not suppress_logging:
            Schema.log_results(rval, *outcome_filters, logging_config=logging_config)
        return rval  # return the results

    @staticmethod
    def validator_for_value(
        value: object,
        *,
        valid_outcome: Outcome = Outcome.PASS,
        invalid_outcome: Outcome = Outcome.FAIL,
        comment: str = "",
    ) -> Validator:
        """
        Creates a validator matching the type of the value
        :param value:           the value to base the new validator on
        :return:                Validator that will exclusively validate the provided value
        """
        if isinstance(value, Validator):
            return value
        if isinstance(value, dict):
            return Map(
                value,
                valid_outcome=valid_outcome,
                invalid_outcome=invalid_outcome,
                comment=comment,
            )
        if isinstance(value, list):
            return Seq(
                value,
                valid_outcome=valid_outcome,
                invalid_outcome=invalid_outcome,
                comment=comment,
            )
        if isinstance(value, str):
            return Str(
                value,
                valid_outcome=valid_outcome,
                invalid_outcome=invalid_outcome,
                comment=comment,
            )
        if isinstance(value, bool):  # must be checked before int because bools are ints
            return Bool(
                value,
                valid_outcome=valid_outcome,
                invalid_outcome=invalid_outcome,
                comment=comment,
            )
        if isinstance(value, (int, float)):
            return Num(
                value,
                valid_outcome=valid_outcome,
                invalid_outcome=invalid_outcome,
                comment=comment,
            )
        assert False, f"could not create Validator for '{value}'"


    @staticmethod
    def log_results(
        results: Result | ResultSet, *outcome_filters: Outcome, logging_config: dict = None
    ):
        # init a logging_config if none was provided
        if not logging_config:
            logging_config = {}

        # add in any missing loggers
        logging_config = {
            Outcome.PASS: logging_config.get(Outcome.PASS, logger.info),
            Outcome.FAIL: logging_config.get(Outcome.FAIL, logger.error),
            Outcome.WARN: logging_config.get(Outcome.WARN, logger.warning),
            Outcome.INFO: logging_config.get(Outcome.INFO, logger.info),
            Outcome.NONE: logging_config.get(Outcome.NONE, logger.debug),
        }

        # to avoid double conversion of each result into a string, convert and map to the logger we'll use later
        results_to_print = [
            (logging_config[result.outcome], repr(result))
            for result in ResultSet(results).get_results(*outcome_filters)
        ]

        min_indent_depth = 1000  # sys.maxint is more accurate, but this is good enough without having to import sys
        for result in (t[1] for t in results_to_print):
            min_indent_depth = min(min_indent_depth, len(result) - len(result.lstrip()))

        for log, result in results_to_print:
            # log the result with the configured logger, dropping the unnecessary leading whitespace
            log(result[min_indent_depth:])
