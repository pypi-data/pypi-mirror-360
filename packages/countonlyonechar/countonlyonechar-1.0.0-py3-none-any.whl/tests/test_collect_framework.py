import pytest
from countonlyonechar.collect_framework import count_only_one_char_cli


def test_output_string(capsys):
    """Test output when using --string."""
    count_only_one_char_cli(['--string', 'test1245'])
    out, err = capsys.readouterr()
    assert '6\n' == out


def test_output_file(capsys, tmp_path):
    """Test output when using --file."""
    test_file = tmp_path / 'test_file.txt'
    test_file.write_text('string')
    count_only_one_char_cli(['--file', str(test_file)])
    out, err = capsys.readouterr()
    assert '6\n' == out


def test_output_file_and_string(capsys, tmp_path):
    """Test output when using --file and --string."""
    test_file = tmp_path / 'test_file.txt'
    test_file.write_text('str')
    count_only_one_char_cli(['--string', 'test1245', "--file", str(test_file)])
    out, err = capsys.readouterr()
    assert '3\n' == out


def test_output_error(capsys):
    """Test CLI error with no arguments."""
    with pytest.raises(SystemExit):
        count_only_one_char_cli([])
    out, err = capsys.readouterr()
    assert '' == out
    assert 'To count single characters from text, enter --string, from file --file' in err
