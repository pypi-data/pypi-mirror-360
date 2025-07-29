from collections import Counter
from functools import lru_cache


def check_str_type(text: str):
    """
    Checks if parameter is of type str.

    Args:
        text (any): The parameter to check.

    Raises:
        TypeError: If the parameter is not a str.
    """
    if not isinstance(text, str):
        raise TypeError(f'The value {text} must be a string')


@lru_cache(maxsize=128)
def count_only_one_char(text: str) -> int:
    """The function counts the sum of the number of single characters in a string.

    Function takes a string and returns the number of characters in the
    string occurring only once. The function caches the result.

    Args:
        text (str): The input str.

    Returns:
        int: Number of characters in the string occurring only once.

    Raises:
        TypeError: If the parameter is not a str.
    """
    check_str_type(text)
    return sum(1 for count in Counter(text).values() if count == 1)


def read_txt_file(path_to_text_file: str) -> str:
    """Reads a text file and returns it as a string.

    Args:
        path_to_text_file (str): Path to the file.

    Returns:
        str: String from file.

    Raises:
        FileNotFoundError: If the file is not found.
        Exception: If any other error except FileNotFoundError.
    """
    check_str_type(path_to_text_file)
    try:
        with open(path_to_text_file) as file:
            read_text = file.read()
            return read_text
    except FileNotFoundError:
        raise FileNotFoundError(f'File at {path_to_text_file} not found')
    except Exception as e:
        raise Exception(f'Error: {e}')

if __name__ == '__main__':
    assert count_only_one_char('abbbccdf') == 3
