# Schema validation wrapper

from __future__ import annotations
from .results import Outcome, Result, ResultSet
from .validator import Validator
from .contextual import ContextualValidator

import logging
logger = logging.getLogger(__name__)

class Schema:
    """
    Validation Schema
    - encapsulates the root of the validation tree
    """
    def __init__(self, schema: object) -> None:
        self.validator = Validator.for_value(schema)

    def __repr__(self) -> str:
        return repr(self.validator)

    def validate(self, document:object, context:object=None) -> ResultSet:
        """
        Validate a document against the schema
        :param document:            the document to validate
        :param context:             context object to pass to any contextual validators
        """
        # validate the document with context; if there's no explicit context, use the document itself
        return ContextualValidator.validate_with_context(self.validator, document, context=(document if context is None else context))

    @staticmethod
    def log_results(results:Result|ResultSet, *outcome_filters:Outcome, logging_config:dict=None):
        """
        Static helper method to log the results of a schema validation
        :param results:             the result/resultset to log
        :param outcome_filters:     args list of outcomes to include in the log output
        :param logging_config:      dict that maps outcomes to logging level functions
        """
        # init a logging_config if none was provided
        if logging_config is None:
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
            for result in ResultSet(results).filter(*outcome_filters)
        ]

        min_indent_depth = 1000  # sys.maxint is more accurate, but this is good enough without having to import sys
        for result in (t[1] for t in results_to_print):
            min_indent_depth = min(min_indent_depth, len(result) - len(result.lstrip()))

        for log, result in results_to_print:
            # log the result with the configured logger, dropping the unnecessary leading whitespace
            log(result[min_indent_depth:])
