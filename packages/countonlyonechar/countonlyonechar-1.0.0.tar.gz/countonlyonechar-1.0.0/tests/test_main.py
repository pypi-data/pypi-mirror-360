import pytest
import pytest_mock
from countonlyonechar.main import check_str_type, count_only_one_char, read_txt_file

LIST_NOT_STR = [451278, None, ['abc', 'def'], {1: 'test'}, 4.5, True, {1, 2}, (1, 2)]

DICT_STRING_AND_COUNT_ONLY_ONE_CHAR = {
    'abbbccdf': 3,
    'aaa': 0,
    ' ': 1,
    'qwerty': 6,
    'qwerty123': 9,
    'qwerty123 ': 10,
    ' qwerty123 ': 9
}


class TestCheckStrType:
    """Tests for check_str_type() function."""

    def test_not_str_input(self):
        """Should raise TypeError for non-string input."""
        for not_str_type in LIST_NOT_STR:
            with pytest.raises(TypeError):
                check_str_type(not_str_type)


class TestCountOnlyOneChar:
    """Tests for count_only_one_char() function."""

    def test_count_only_one_char_str(self):
        """
        Tests that the function returns the correct count of
        characters in the string occurring only once.
        """
        for string, count_one_char in DICT_STRING_AND_COUNT_ONLY_ONE_CHAR.items():
            assert count_only_one_char(string) == count_one_char

    def test_not_str_input(self):
        """Should raise TypeError for non-string input."""
        for not_str_type in LIST_NOT_STR:
            with pytest.raises(TypeError):
                count_only_one_char(not_str_type)


class TestReadTxtFile:
    """Tests for read_txt_file() function."""

    class TestReadTxtFile:
        def test_read_txt_file(self, mocker):
            """Test of opening and reading a mock file and returns it as a string"""
            mock_open = mocker.mock_open(read_data='string')
            mocker.patch("builtins.open", mock_open)
            result = read_txt_file("test_file.txt")
            assert result == 'string'
            mock_open.assert_called_once_with("test_file.txt")

    def test_not_str_input(self):
        """Should raise TypeError for non-string input."""
        for not_str_type in LIST_NOT_STR:
            with pytest.raises(TypeError):
                read_txt_file(not_str_type)

    def test_file_not_found(self):
        """Should raise FileNotFoundError for incorrect address or missing file."""
        with pytest.raises(FileNotFoundError):
            read_txt_file(r' ')
