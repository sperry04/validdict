import pytest, re
from validdict import Schema
from validdict.scalars import ScalarValidator, Str, Num, Bool, Regex # objects under test

class TestScalar:

    def test_scalar_constructor(self):
        scalar = ScalarValidator((str,), ("aaa",))
        assert scalar is not None
        assert isinstance(scalar, ScalarValidator)
        assert repr(scalar) == "must be type 'str' with value 'aaa'"
        with pytest.raises(TypeError):
            ScalarValidator(("string",), (1234,))
        with pytest.raises(TypeError):
            ScalarValidator((str,), (1234,))

class TestStr:

    def test_str_constructor(self):
        scalar = Str()
        assert scalar is not None
        assert isinstance(scalar, Str)
        assert repr(scalar) == "must be type 'str'"

        scalar = Str("a")
        assert scalar is not None
        assert isinstance(scalar, Str)
        assert repr(scalar) == "must be type 'str' with value 'a'"

        scalar = Str("a", "b")
        assert scalar is not None
        assert isinstance(scalar, Str)
        assert repr(scalar) == "must be type 'str' with value one of ('a', 'b')"

        with pytest.raises(TypeError):
            Str(1, 2, 3)

        with pytest.raises(TypeError):
            Str(1, 2, 3, case_sensitive=False)

    def test_direct_str_validation(self):
        assert Str().validate("A")
        assert not Str().validate(None)
        assert not Str().validate(1234)
        assert not Str().validate(True)
        assert Str("A").validate("A")
        assert not Str("A").validate(1234)
        assert Str("A", "B").validate("A")
        assert Str("A", "B").validate("B")
        assert not Str("A", "B").validate("C")

    def test_str_validation(self):

        schema = Schema(
            {
                "key": Str()
            }
        )
        
        results = schema.validate({})
        assert not results

        results = schema.validate({"key": "value"})
        assert results

        results = schema.validate({"key": "other value"})
        assert results

    def test_literal_str_validation(self):
        schema = Schema(
            {
                "key": Str("value")
            }
        )
        
        results = schema.validate({})
        assert not results

        results = schema.validate({"key": "value"})
        assert results

        results = schema.validate({"key": "wrong"})
        assert not results

    def test_list_str_validation(self):
        schema = Schema(
            {
                "key": Str("a", "b", "c")
            }
        )
        
        results = schema.validate({})
        assert not results

        results = schema.validate({"key": "a"})
        assert results

        results = schema.validate({"key": "b"})
        assert results

        results = schema.validate({"key": "c"})
        assert results

        results = schema.validate({"key": "C"})
        assert not results

    def test_case_insensitive_str_validation(self):
        schema = Schema(
            {
                "key": Str("a", "b", "c", case_sensitive=False)
            }
        )
        
        results = schema.validate({})
        assert not results

        results = schema.validate({"key": "A"})
        assert results

        results = schema.validate({"key": "b"})
        assert results

        results = schema.validate({"key": "C"})
        assert results

        results = schema.validate({"key": "wrong"})
        assert not results


class TestNum:

    def test_num_constructor(self):
        scalar = Num()
        assert scalar is not None
        assert isinstance(scalar, Num)
        assert repr(scalar) == "must be type in ('int', 'float')"

        scalar = Num(1)
        assert scalar is not None
        assert isinstance(scalar, Num)
        assert repr(scalar) == "must be type in ('int', 'float') with value '1'"

        scalar = Num(1, 2)
        assert scalar is not None
        assert isinstance(scalar, Num)
        assert repr(scalar) == "must be type in ('int', 'float') with value one of ('1', '2')"

        scalar = Num(lt=10)
        assert scalar is not None
        assert isinstance(scalar, Num)
        assert repr(scalar) == "must be type in ('int', 'float') with value '< 10'"

        scalar = Num(gte=10, lt=20)
        assert scalar is not None
        assert isinstance(scalar, Num)
        assert repr(scalar) == "must be type in ('int', 'float') with value '>= 10' and '< 20'"

        scalar = Num(5, 6, 7, gte=0.0, lt=10.0)
        assert scalar is not None
        assert isinstance(scalar, Num)
        assert repr(scalar) == "must be type in ('int', 'float') with value one of ('5', '6', '7') and '>= 0.0' and '< 10.0'"

    def test_direct_num_validation(self):
        assert Num().validate(1234)
        assert Num().validate(1234.5678)
        assert not Num().validate(None)
        assert not Num().validate("A")
        assert not Num().validate(True)
        assert Num(1234).validate(1234)
        assert Num(1234.5678).validate(1234.5678)
        assert not Num(1234).validate(1234.5678)
        assert not Num(1234.5678).validate(1234)
        assert Num(1234, 1234.5678).validate(1234)
        assert Num(1234, 1234.5678).validate(1234.5678)

    def test_num_validation(self):
        schema = Schema(
            {
                "key": Num()
            }
        )
        
        results = schema.validate({})
        assert not results

        results = schema.validate({"key": 10})
        assert results

        results = schema.validate({"key": 3.14})
        assert results

    def test_literal_num_validation(self):
        schema = Schema(
            {
                "key": Num(4, 5, 4.5)
            }
        )
        
        results = schema.validate({})
        assert not results

        results = schema.validate({"key": 5})
        assert results

        results = schema.validate({"key": 4.5})
        assert results

        results = schema.validate({"key": 10})
        assert not results

    def test_range_num_validation(self):
        schema = Schema(
            {
                "key": Num(1, 2, 3, range(5, 10))
            }
        )
        
        results = schema.validate({})
        assert not results

        results = schema.validate({"key": 2})
        assert results

        results = schema.validate({"key": 5})
        assert results

        results = schema.validate({"key": 7})
        assert results

        results = schema.validate({"key": 4})
        assert not results

        results = schema.validate({"key": 10})
        assert not results

        results = schema.validate({"key": 15})
        assert not results

    def test_relational_num_validation(self):
        schema = Schema(
            {
                "key": Num(gt=0, lte=10)
            }
        )
        
        results = schema.validate({})
        assert not results

        results = schema.validate({"key": 1})
        assert results

        results = schema.validate({"key": 10})
        assert results

        results = schema.validate({"key": 5.5})
        assert results

        results = schema.validate({"key": 0})
        assert not results

        results = schema.validate({"key": 11})
        assert not results

    def test_weird_num_validation(self):
        schema = Schema(
            {
                "key": Num(4, 5, 6, gt=4.5, lt=5.5, gte=5.0, lte=5.0)
            }
        )
        
        results = schema.validate({})
        assert not results

        results = schema.validate({"key": 4})
        assert not results

        results = schema.validate({"key": 5})
        assert results

        results = schema.validate({"key": 6})
        assert not results



class TestBool:

    def test_bool_constructor(self):
        scalar = Bool()
        assert scalar is not None
        assert isinstance(scalar, Bool)
        assert repr(scalar) == "must be type 'bool'"

        scalar = Bool(True)
        assert scalar is not None
        assert isinstance(scalar, Bool)
        assert repr(scalar) == "must be type 'bool' with value 'True'"        

    def test_direct_bool_validation(self):
        assert Bool().validate(False)
        assert not Bool().validate(None)
        assert not Bool().validate("True")
        assert not Bool().validate(1234)
        assert Bool(True).validate(True)
        assert Bool(True, False).validate(True)
        assert Bool(True, False).validate(False)
        assert not Bool(True).validate(False)
        assert not Bool(False).validate(True)

    def test_bool_validation(self):
        schema = Schema(
            {
                "key": Bool()
            }
        )
        
        results = schema.validate({})
        assert not results

        results = schema.validate({"key": True})
        assert results

        results = schema.validate({"key": False})
        assert results

        results = schema.validate({"key": "True"})
        assert not results

        results = schema.validate({"key": "False"})
        assert not results

        results = schema.validate({"key": 1})
        assert not results

        results = schema.validate({"key": 0})
        assert not results


class TestRegex:

    def test_regex_constructor(self):
        scalar = Regex()
        assert scalar is not None
        assert isinstance(scalar, Regex)
        assert repr(scalar) == "must be type 'str'"

        scalar = Regex("^[a-zA-Z]+$")
        assert scalar is not None
        assert isinstance(scalar, Regex)
        assert repr(scalar) == "must be type 'str' with value matching '^[a-zA-Z]+$'"

        scalar = Regex(re.compile("^[a-zA-Z]+$"))
        assert scalar is not None
        assert isinstance(scalar, Regex)
        assert repr(scalar) == "must be type 'str' with value matching '^[a-zA-Z]+$'"

        with pytest.raises(TypeError):
            Regex(re.compile("^[a-zA-Z]+$"), "^[0-9]+$", 100)

    def test_direct_regex_validation(self):
        assert Regex(re.compile(r"A")).validate("A")
        assert Regex(re.compile(r".*")).validate("A")
        assert not Regex(re.compile(r"B")).validate("A")
        assert Regex(r"A").validate("A")
        assert Regex(r".*").validate("A")
        assert not Regex(r"B").validate("A")
        assert Regex(r"A", r"B").validate("A")
        assert Regex(r"A", r"B", re.compile(r".*")).validate("Anything")
        assert not Regex(r"B", r"C").validate("A")

    def test_regex_validation(self):
        schema = Schema(
            {
                "key": Regex("^[a-zA-Z]+$", re.compile("^[0-9]+$"))
            }
        )
        
        results = schema.validate({})
        assert not results

        results = schema.validate({"key": "abc"})
        assert results

        results = schema.validate({"key": "123"})
        assert results

        results = schema.validate({"key": "abc123"})
        assert not results

        results = schema.validate({"key": "ABC"})
        assert results

        results = schema.validate({"key": "a.b.c"})
        assert not results