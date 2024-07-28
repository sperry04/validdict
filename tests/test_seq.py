import pytest
from validdict import Schema, Any, Str, Num, Outcome
from validdict import Seq # object under test

class TestSeq:

    def test_seq_constructor(self):
        seq = Seq()
        assert isinstance(seq, Seq)
        assert repr(seq) == "must be a sequence"

        seq = Seq(Any())
        assert isinstance(seq, Seq)
        assert repr(seq) == "must be a sequence like: [ may be anything ]"

        seq = Seq(Num())
        assert isinstance(seq, Seq)
        assert repr(seq) == "must be a sequence like: [ must be type in ('int', 'float') ]"

        with pytest.raises(TypeError):
            Seq(Str(), "string", Num(), 100)

    def test_seq_validation(self):
        schema = Schema(
            {
                "key": Seq()
            }
        )

        results = schema.validate({"key": []})
        assert len(results.filter(Outcome.FAIL)) == 0
        assert results

        results = schema.validate({"key": [1, 2, 3]})
        assert len(results.filter(Outcome.FAIL)) == 0
        assert results

        results = schema.validate({"key": 1})
        assert len(results.filter(Outcome.FAIL)) == 1
        assert not results

    def test_seq_min_len(self):
        schema = Schema(
            {
                "key": Seq(min_len=2)
            }
        )

        results = schema.validate({"key": [1, 2, 3]})
        assert len(results.filter(Outcome.FAIL)) == 0
        assert results

        results = schema.validate({"key": [1, 2]})
        assert len(results.filter(Outcome.FAIL)) == 0
        assert results

        results = schema.validate({"key": [1]})
        assert len(results.filter(Outcome.FAIL)) == 1
        assert not results

        results = schema.validate({"key": []})
        assert len(results.filter(Outcome.FAIL)) == 1
        assert not results

    def test_seq_max_len(self):
        schema = Schema(
            {
                "key": Seq(max_len=2)
            }
        )

        results = schema.validate({"key": []})
        assert len(results.filter(Outcome.FAIL)) == 0
        assert results

        results = schema.validate({"key": [1]})
        assert len(results.filter(Outcome.FAIL)) == 0
        assert results

        results = schema.validate({"key": [1, 2]})
        assert len(results.filter(Outcome.FAIL)) == 0
        assert results

        results = schema.validate({"key": [1, 2, 3]})
        assert len(results.filter(Outcome.FAIL)) == 1
        assert not results

    def test_type_seq_validation(self):
        schema = Schema(
            {
                "key": Seq(Str(), Num())
            }
        )

        results = schema.validate({"key": []})
        assert len(results.filter(Outcome.FAIL)) == 0
        assert results

        results = schema.validate({"key": [1, 2, 3]})
        assert len(results.filter(Outcome.FAIL)) == 0
        assert results

        results = schema.validate({"key": ["aaa", "bbb", "ccc"]})
        assert len(results.filter(Outcome.FAIL)) == 0
        assert results

        results = schema.validate({"key": ["aaa", 1, "bbb", 2]})
        assert len(results.filter(Outcome.FAIL)) == 0
        assert results

        results = schema.validate({"key": 1})
        assert len(results.filter(Outcome.FAIL)) == 1
        assert not results

        results = schema.validate({"key": [True, True, False]})
        assert len(results.filter(Outcome.FAIL)) == 9
        assert not results

        results = schema.validate({"key": ["aaa", 1, "bbb", 2, False]})
        assert len(results.filter(Outcome.FAIL)) == 3
        assert not results
