# countonlyonechar

Package for counting unique characters in the string occurring only once.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install countonlyonechar.

```bash
pip install countonlyonechar
```

## Usage

```python
import countonlyonechar

# returns 4
countonlyonechar.count_only_one_char('word')

# returns <string in file>
countonlyonechar.read_txt_file(path_to_text_file)
```

```commandline
countonlyonechar --string 'word'
# returns 4

countonlyonechar --file <file_path>
# returns the number of characters in the file occurring only once
```
## License

[MIT](https://choosealicense.com/licenses/mit/)