import pytest
from validdict.validator import Outcome
from validdict.results import Result, ResultSet, FixedOutcome
from validdict import Schema # object under test


class TestSchema:

    def test_schema_constructor(self):
        schema = Schema({})
        assert schema is not None
        assert isinstance(schema, Schema)
        assert repr(schema) == "must be a map like: {  }"

    def test_schema_validation(self):
        schema = Schema({})
        assert schema.validate({})

    def test_schema_logging(self):

        def assert_outcome(message, expected_outcome):
            assert expected_outcome.value in message

        logging_config = {
            Outcome.PASS: lambda message: assert_outcome(message, Outcome.PASS),
            Outcome.FAIL: lambda message: assert_outcome(message, Outcome.FAIL),
            Outcome.WARN: lambda message: assert_outcome(message, Outcome.WARN),
            Outcome.INFO: lambda message: assert_outcome(message, Outcome.INFO),
            Outcome.NONE: lambda message: assert_outcome(message, Outcome.NONE),
        }

        results = ResultSet()
        results.add_results(Result(Outcome.NONE, "value0", [], FixedOutcome(Outcome.NONE)))
        results.add_results(Result(Outcome.PASS, "value1", [], FixedOutcome(Outcome.PASS)))
        results.add_results(Result(Outcome.INFO, "value2", [], FixedOutcome(Outcome.INFO)))
        results.add_results(Result(Outcome.WARN, "value3", [], FixedOutcome(Outcome.WARN)))
        results.add_results(Result(Outcome.FAIL, "value4", [], FixedOutcome(Outcome.FAIL)))

        Schema.log_results(results)
        Schema.log_results(results, logging_config=logging_config)
    