import pytest
from validdict.helpers import format_sequence, path_padding, format_path, extend_path # objects under test


class TestHelpers:

    def test_format_sequence(self):
        # Test with an empty sequence
        seq = []
        expected_result = ""
        assert format_sequence(seq) == expected_result

        # Test with a plain string
        seq = "hello"
        expected_result = "'hello'"
        assert format_sequence(seq) == expected_result

        # Test with an object
        class TestObject:
            __name__ = "test object"
        seq = TestObject()
        expected_result = "'test object'"
        assert format_sequence(seq) == expected_result

        # Test with a single item
        seq = [1]
        expected_result = "'1'"
        assert format_sequence(seq) == expected_result

        # Test with a tuple
        seq = (1, 2, 3)
        expected_result = "'1', '2', '3'"
        assert format_sequence(seq) == expected_result

        # Test with a list and custom separator
        seq = [4, 5, 6]
        expected_result = "'4' | '5' | '6'"
        assert format_sequence(seq, separator=" | ") == expected_result

        # Test with a list and custom quote
        seq = [7, 8, 9]
        expected_result = "*7*, *8*, *9*"
        assert format_sequence(seq, quote="*") == expected_result

        # Test with a list and custom prefix and suffix
        seq = [10, 11, 12]
        expected_result = "['10', '11', '12']"
        assert format_sequence(seq, prefix="[", suffix="]") == expected_result

    def test_path_padding(self):
        # Test with a path and default padding
        path = [ "home", "sperry", "code" ]
        expected_result = "      " # 2 spaces * 3 items = 6 spaces
        assert path_padding(path) == expected_result

        # Test with a path and custom padding
        path = [ "home", "sperry", "code" ]
        expected_result = "------------" # 4 dashes * 3 items = 12 dashes
        assert path_padding(path, padding="----") == expected_result

        # Test with a path and custom offset
        path = [ "home", "sperry", "code" ]
        expected_result = "          " # (2 spaces * 3 items) + 2 (spaces * 2 offset) = 8 spaces
        assert path_padding(path, offset=2) == expected_result

    def test_format_path(self):
        # Test with no path
        expected_result = ""
        assert format_path() == expected_result

        # Test with a path and default parameters
        path = ["home", "sperry", "code"]
        expected_result = "      home.sperry.code"
        assert format_path(path) == expected_result

        # Test with a path and custom prefix, suffix, and padding
        path = ["home", "sperry", "code"]
        expected_result = "-------------------->>>home.sperry.code<<<"
        assert format_path(path, prefix=">>>", suffix="<<<", padding="----", padding_offset=2) == expected_result

    def test_extend_path(self):
        # Test with no params
        assert extend_path() == None

        # Test with no path
        assert extend_path(key="home") == ["home"]

        # Test with a path and a key
        path = ["home", "sperry"]
        key = "code"
        expected_result = ["home", "sperry", "code"]
        assert extend_path(path, key) == expected_result

        # Test with an empty path and a key
        path = []
        key = "home"
        expected_result = ["home"]
        assert extend_path(path, key) == expected_result

        # Test with a path and no key
        path = ["home", "sperry"]
        expected_result = ["home", "sperry"]
        assert extend_path(path) == expected_result

        # Test with an empty path and no key
        path = []
        expected_result = []
        assert extend_path(path) == expected_result
