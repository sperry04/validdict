# Validator base class tests

import pytest
from validdict import Validator, Outcome

def test_constructor_defaults():
    v = Validator()
    assert v.valid_outcome == Outcome.PASS
    assert v.invalid_outcome == Outcome.FAIL
    assert v.comment == ""
    with pytest.raises(NotImplementedError):
        v.validate(None)


# # Dictionary Validator
# # Allows the definition of a schema for validating a dictionary object

# from __future__ import annotations                                                                  # for forward references in type hints
# from enum import Enum                                                                               # for validation result enumeration
# import re                                                                                           # for regular expression validators

# import logging
# logger = logging.getLogger(__name__)



# # entry point for in-line testing
# if __name__ == '__main__':
#     from logformat import *
#     logger = setupMultilineLogging(
#         __name__,
#         level=logging.DEBUG,
#         timestamps=False,
#         filename=None,
#         additional_modules=[ "utils" ]
#     )

#     def print_and_assert(result):
#         logger.debug(result)
#         assert result

#     def print_and_assert_not(result):
#         logger.debug(result)
#         assert not result

#     def execute_and_catch(f, expected_exception):
#         try:
#             f()
#         except Exception as ex:
#             assert isinstance(ex, expected_exception)
#             logger.debug(f"Caught expected exception: '{ex}'")
#         else:
#             assert False, f"Function did not throw expected '{expected_exception.__name__}' exception"

#     # type formatter
#     assert format_sequence(["a", "b", "c"], "-", "*") == "*a*-*b*-*c*"
#     assert format_sequence(int) == "'int'"
#     assert format_sequence((int, float, (str, Validator))) == "'int', 'float', 'str', 'Validator'"

#     # validation results
#     result_none = Result(Outcome.NONE, None, None, None)
#     result_pass = Result(Outcome.PASS, None, None, None)
#     result_fail = Result(Outcome.FAIL, None, None, None)
#     result_warn = Result(Outcome.WARN, None, None, None)
#     result_info = Result(Outcome.INFO, None, None, None)
#     assert not result_fail
#     assert result_pass

#     results = ResultSet(result_none, result_pass, result_fail, result_warn, result_info)
#     assert results.get_results() == [ result_none, result_pass, result_fail, result_warn, result_info ]
#     assert results.get_results(Outcome.PASS, Outcome.INFO) == [ result_pass, result_info ]
#     assert (result_pass | result_fail).get_results() == [ result_pass, result_fail ]
#     assert (result_pass | results).get_results() == [ result_pass, result_none, result_pass, result_fail, result_warn, result_info ]

#     # scalar validators
#     print_and_assert(Str().validate("A"))
#     print_and_assert_not(Str().validate(None))
#     print_and_assert_not(Str().validate(1234))
#     print_and_assert_not(Str().validate(True))
#     print_and_assert(Str("A").validate("A"))
#     print_and_assert_not(Str("A").validate(1234))
#     print_and_assert(Str("A", "B").validate("A"))
#     print_and_assert(Str("A", "B").validate("B"))
#     print_and_assert_not(Str("A", "B").validate("C"))

#     print_and_assert(Num().validate(1234))
#     print_and_assert(Num().validate(1234.5678))
#     print_and_assert_not(Num().validate(None))
#     print_and_assert_not(Num().validate("A"))
#     print_and_assert_not(Num().validate(True))
#     print_and_assert(Num(1234).validate(1234))
#     print_and_assert(Num(1234.5678).validate(1234.5678))
#     print_and_assert_not(Num(1234).validate(1234.5678))
#     print_and_assert_not(Num(1234.5678).validate(1234))
#     print_and_assert(Num(1234, 1234.5678).validate(1234))
#     print_and_assert(Num(1234, 1234.5678).validate(1234.5678))

#     print_and_assert(Bool().validate(False))
#     print_and_assert_not(Bool().validate(None))
#     print_and_assert_not(Bool().validate("True"))
#     print_and_assert_not(Bool().validate(1234))
#     print_and_assert(Bool(True).validate(True))
#     print_and_assert(Bool(True, False).validate(True))
#     print_and_assert(Bool(True, False).validate(False))
#     print_and_assert_not(Bool(True).validate(False))
#     print_and_assert_not(Bool(False).validate(True))

#     print_and_assert(Regex(re.compile(r"A")).validate("A"))
#     print_and_assert(Regex(re.compile(r".*")).validate("A"))
#     print_and_assert_not(Regex(re.compile(r"B")).validate("A"))
#     print_and_assert(Regex(r"A").validate("A"))
#     print_and_assert(Regex(r".*").validate("A"))
#     print_and_assert_not(Regex(r"B").validate("A"))
#     print_and_assert(Regex(r"A", r"B").validate("A"))
#     print_and_assert(Regex(r"A", r"B", re.compile(r".*")).validate("Anything"))
#     print_and_assert_not(Regex(r"B", r"C").validate("A"))

#     # compound validators
#     print_and_assert(Any().validate(None))
#     print_and_assert(Any().validate("A"))
#     print_and_assert(Any().validate(1234))
#     print_and_assert(Any().validate(1234.5678))
#     print_and_assert(Any().validate(True))
#     print_and_assert(Any().validate({}))
#     print_and_assert(Any().validate([]))

#     print_and_assert((Str() | Num()).validate("A"))
#     print_and_assert((Str("A") | Num(1234) | Bool(False)).validate("A"))
#     print_and_assert((Str("A") | Num(1234) | Bool(False)).validate(1234))
#     print_and_assert_not((Str("A") | Num(1234) | Bool(False)).validate(True))

#     print_and_assert(Seq(Any()).validate([]))
#     print_and_assert(Seq(Num(), Bool()).validate([]))
#     print_and_assert(Seq(Num(), Bool()).validate([1234, True]))
#     print_and_assert_not(Seq(Num(), Bool()).validate([1234, True, "A"]))
#     print_and_assert(Seq(Num(1,2,3)).validate([1, 3, 2]))
#     print_and_assert_not(Seq(Num(1,2,3)).validate([1, 3, 2, 4]))
#     print_and_assert_not(Seq(Seq(Num())).validate([1, 2, 3]))
#     print_and_assert(Seq(Seq(Num())).validate([[1, 2, 3], [4, 5, 6]]))

#     d = {
#         "a": "aaa",
#         "b": 123,
#         "c": 1234.5678,
#         "d": "BAD",
#         "_ignore": "thing to ignore"
#     }

#     print_and_assert(Map(d).validate(d))

#     print_and_assert_not(Map({
#         "a": Str(),
#         "b": Num(),
#         OptionalKey("c"): Num()
#     }).validate(d))

#     print_and_assert(Map({
#         "a": Str(),
#         "b": Num(),
#         OptionalKey("c"): Num(),
#         OtherKeys(): Any()
#     }).validate(d))

#     print_and_assert(Map({
#         "a": Str(),
#         "b": Num(),
#         OptionalKey("c"): Num(),
#         "d": Any(),
#         StartsWith("_"): Any(comment="Keys starting with underscore will be ignored")
#     }).validate(d))

#     print_and_assert(Map({
#         "a": Str("aaa" if d["b"] == 123 else "bbb", comment="must be 'aaa' if key(b) is 123 else 'bbb'"),
#         "b": Num(123 if d["a"] == "aaa" else 321, comment="must be 123 if key(a) is 'aaa' else 321"),
#         OtherKeys(): Any()
#     }).validate(d))

#     print_and_assert_not(Map({
#         "a": Str("bbb" if d["b"] == 123 else "aaa", comment="must be 'bbb' if key(b) is 123 else 'aaa'"),
#         "b": Num(123 if d["a"] == "aaa" else 321, comment="must be 123 if key(a) is 'aaa' else 321"),
#         OtherKeys(): Any()
#     }).validate(d))

#     print_and_assert_not(Map({
#         "a": Str(),
#         "b": Num(),
#         OptionalKey("c"): Num(),
#         "e": Bool(),
#         "f": Bool(),
#         OtherKeys(): Any()
#     }).validate(d))

#     execute_and_catch(lambda: Map({
#         "a": Str(),
#         "b": Num(),
#         OptionalKey("c"): Num(),
#         OtherKeys(): Any(),
#         OtherKeys(): Any()
#     }), AssertionError)

#     execute_and_catch(lambda: Map({
#         "a": StartsWith(),
#         "b": OtherKeys(),
#         OptionalKey("c"): Num(),
#         OtherKeys(): Any(),
#         OtherKeys(): Any()
#     }), AssertionError)

# # TODO: could use some tests for the ContextualValidator and CallbackValidator
