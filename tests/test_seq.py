import pytest
from validdict import Schema, Any, Str, Num
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
        assert results.fail_count == 0
        assert results

        results = schema.validate({"key": [1, 2, 3]})
        assert results.fail_count == 0
        assert results

        results = schema.validate({"key": 1})
        assert results.fail_count == 1
        assert not results

    def test_type_seq_validation(self):
        schema = Schema(
            {
                "key": Seq(Str(), Num())
            }
        )
        results = schema.validate({"key": []})
        assert results.fail_count == 0
        assert results

        results = schema.validate({"key": [1, 2, 3]})
        assert results.fail_count == 0
        assert results

        results = schema.validate({"key": ["aaa", "bbb", "ccc"]})
        assert results.fail_count == 0
        assert results

        results = schema.validate({"key": ["aaa", 1, "bbb", 2]})
        assert results.fail_count == 0
        assert results

        results = schema.validate({"key": 1})
        assert results.fail_count == 1
        assert not results

        results = schema.validate({"key": [True, True, False]})
        assert results.fail_count == 9
        assert not results

        results = schema.validate({"key": ["aaa", 1, "bbb", 2, False]})
        assert results.fail_count == 3
        assert not results
