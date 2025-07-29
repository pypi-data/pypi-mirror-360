import argparse
from countonlyonechar.main import count_only_one_char, read_txt_file

def count_only_one_char_cli(argv=None):
    parser = argparse.ArgumentParser(description="Counts the sum of the number of single characters in a string")
    parser.add_argument("--string", type=str, help="Enter text to calculate")
    parser.add_argument("--file", type=str, help="Path to text file")

    args = parser.parse_args(argv)

    if args.file:
        file_path = args.file
        content = read_txt_file(str(file_path))
        print(count_only_one_char(content))

    elif args.string:
        print(count_only_one_char(args.string))

    else:
        parser.error('To count single characters from text, enter --string, from file --file')

if __name__ == '__main__':
    count_only_one_char_cli()
