import pytest
from validdict.results import Outcome, OutcomeProvider, FixedOutcome, Result, ResultSet # objects under test


class TestOutcomeProvider:

    def test_outcome_provider_constructor_defaults(self):
        op = OutcomeProvider()
        assert op.valid_outcome == Outcome.PASS
        assert op.invalid_outcome == Outcome.FAIL
        assert op.comment == ""

    def test_outcome_provider_constructor_params(self):
        op = OutcomeProvider(valid_outcome=Outcome.INFO, invalid_outcome=Outcome.WARN, comment="a comment")
        assert op.valid_outcome == Outcome.INFO
        assert op.invalid_outcome == Outcome.WARN
        assert op.comment == "a comment"


class TestFixedOutcome:

    def test_fixed_outcome_constructor_defaults(self):
        op = FixedOutcome()
        assert op.valid_outcome == Outcome.NONE
        assert op.invalid_outcome == Outcome.NONE
        assert op.comment == ""
        assert op.message == ""

    def test_fixed_outcome_constructor_params(self):
        op = FixedOutcome(outcome=Outcome.INFO, comment="a comment", message="a message")
        assert op.valid_outcome == Outcome.INFO
        assert op.invalid_outcome == Outcome.NONE
        assert op.comment == "a comment"
        assert op.message == "a message"

        op = FixedOutcome(outcome=Outcome.WARN, is_valid=False, comment="a comment", message="a message")
        assert op.valid_outcome == Outcome.NONE
        assert op.invalid_outcome == Outcome.WARN
        assert op.comment == "a comment"
        assert op.message == "a message"


class TestResult:

    def test_result_constructor(self):
        result = Result(Outcome.NONE, { "key": "value "}, [])
        assert isinstance(result, Result)
        assert repr(result) == "'<dict>' no validator = 'NONE'"
        assert result.outcome == Outcome.NONE
        assert result.comment == ""
        assert result.message == "no validator"
        with pytest.raises(TypeError):
            Result(None, "value", [])
        with pytest.raises(TypeError):
            Result(Outcome.NONE, "value", [], "not a validator")

    def test_result_or(self):
        fo = FixedOutcome(Outcome.PASS)
        results = Result(Outcome.PASS, "value1", [], fo) | Result(Outcome.PASS, "value2", [], fo)
        assert isinstance(results, ResultSet)
        assert results

    def test_result_bool(self):
        fo = FixedOutcome(Outcome.PASS)
        result = Result(Outcome.PASS, "value", [], fo)
        assert result
        result = Result(Outcome.FAIL, "value", [], fo)
        assert not result
        result = Result(Outcome.NONE, "value", [], None)
        assert result

    def test_result_outcome(self):
        fo = FixedOutcome(Outcome.PASS)
        result = Result(Outcome.PASS, "value", [], fo)
        assert result.outcome == Outcome.PASS
        result = Result(Outcome.FAIL, "value", [], fo)
        assert result.outcome == Outcome.FAIL


class TestResultSet:

    def test_resultset_constructor(self):
        results = ResultSet()
        assert isinstance(results, ResultSet)
        assert repr(results) == "No Results"

        results.add_results(Result(Outcome.PASS, "value1", [], None))
        results.add_results(Result(Outcome.FAIL, "value2", [], None))
        assert repr(results) == "'value1' no validator = 'PASS'\n'value2' no validator = 'FAIL'"

    def test_resultset_or(self):
        fo = FixedOutcome(Outcome.PASS)
        results = ResultSet() | Result(Outcome.PASS, "value1", [], fo) | Result(Outcome.PASS, "value2", [], fo)
        assert isinstance(results, ResultSet)
        assert results

    def test_resultset_bool(self):
        results = ResultSet()
        assert results
        results.add_results(Result(Outcome.PASS, "value1", [], FixedOutcome(Outcome.PASS)))
        assert results
        results.add_results(Result(Outcome.FAIL, "value2", [], FixedOutcome(Outcome.PASS)))
        assert not results

    def test_add_results(self):
        results = ResultSet()
        results.add_results(Result(Outcome.PASS, "value1", [], FixedOutcome(Outcome.PASS)))
        results.add_results(Result(Outcome.INFO, "value2", [], FixedOutcome(Outcome.INFO)))
        results.add_results(Result(Outcome.WARN, "value3", [], FixedOutcome(Outcome.WARN)))
        results.add_results(Result(Outcome.FAIL, "value4", [], FixedOutcome(Outcome.FAIL)))
        assert len(results.get_results()) == 4
        with pytest.raises(TypeError):
            results.add_results("not a result")

    def test_get_results(self):
        results = ResultSet()
        results.add_results(Result(Outcome.PASS, "value1", [], FixedOutcome(Outcome.PASS)))
        results.add_results(Result(Outcome.INFO, "value2", [], FixedOutcome(Outcome.INFO)))
        results.add_results(Result(Outcome.WARN, "value3", [], FixedOutcome(Outcome.WARN)))
        results.add_results(Result(Outcome.FAIL, "value4", [], FixedOutcome(Outcome.FAIL)))
        assert len(results.get_results()) == 4
        assert len(results.get_results(Outcome.PASS)) == 1
        assert len(results.get_results(Outcome.INFO)) == 1
        assert len(results.get_results(Outcome.WARN)) == 1
        assert len(results.get_results(Outcome.FAIL)) == 1
        with pytest.raises(TypeError):
            results.get_results("not an outcome enum")

    def test_resultset_counts(self):
        results = ResultSet()
        assert results.result_count == 0
        assert results.pass_count == 0
        assert results.info_count == 0
        assert results.warn_count == 0
        assert results.fail_count == 0
        assert results
        results.add_results(Result(Outcome.PASS, "value1", [], FixedOutcome(Outcome.PASS)))
        assert results.result_count == 1
        assert results.pass_count == 1
        assert results.info_count == 0
        assert results.warn_count == 0
        assert results.fail_count == 0
        assert results
        results.add_results(Result(Outcome.INFO, "value2", [], FixedOutcome(Outcome.INFO)))
        assert results.result_count == 2
        assert results.pass_count == 1
        assert results.info_count == 1
        assert results.warn_count == 0
        assert results.fail_count == 0
        assert results
        results.add_results(Result(Outcome.WARN, "value2", [], FixedOutcome(Outcome.WARN)))
        assert results.result_count == 3
        assert results.pass_count == 1
        assert results.info_count == 1
        assert results.warn_count == 1
        assert results.fail_count == 0
        assert results
        results.add_results(Result(Outcome.FAIL, "value2", [], FixedOutcome(Outcome.PASS)))
        assert results.result_count == 4
        assert results.pass_count == 1
        assert results.info_count == 1
        assert results.warn_count == 1
        assert results.fail_count == 1
        assert not results

    def test_resultset_get_results(self):
        results = ResultSet()
        results.add_results(Result(Outcome.PASS, "value1", [], FixedOutcome(Outcome.PASS)))
        results.add_results(Result(Outcome.INFO, "value2", [], FixedOutcome(Outcome.INFO)))
        results.add_results(Result(Outcome.WARN, "value3", [], FixedOutcome(Outcome.WARN)))
        results.add_results(Result(Outcome.FAIL, "value4", [], FixedOutcome(Outcome.FAIL)))
        assert len(results.get_results()) == 4
        assert len(results.get_results(Outcome.PASS)) == 1
        assert len(results.get_results(Outcome.INFO)) == 1
        assert len(results.get_results(Outcome.WARN)) == 1
        assert len(results.get_results(Outcome.FAIL)) == 1
        assert len(results.get_results(Outcome.NONE)) == 0
        assert len(results.get_results(Outcome.PASS, Outcome.INFO)) == 2
        assert len(results.get_results(Outcome.PASS, Outcome.INFO, Outcome.WARN)) == 3
        assert len(results.get_results(Outcome.PASS, Outcome.INFO, Outcome.WARN, Outcome.FAIL)) == 4
        assert len(results.get_results(Outcome.PASS, Outcome.INFO, Outcome.WARN, Outcome.FAIL, Outcome.NONE)) == 4
        assert len(results.get_results(Outcome.INFO, Outcome.WARN, Outcome.FAIL)) == 3
        assert len(results.get_results(Outcome.WARN, Outcome.FAIL)) == 2

