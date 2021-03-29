import argparse


def generate_args():
    parser = argparse.ArgumentParser(
        description='A parser used to extract all clang functions in specified c/cpp file.')
    parser.add_argument('input_file_names', metavar='INPUT_FILE', nargs='+',
                        help='Specifies which files will be used as input files.')
    parser.add_argument('output_file_name', metavar='OUTPUT_FILE', nargs=1,
                        help='Specifies the file at which all extracted results would be stored.')

    return parser.parse_args()


if __name__ == '__main__':
    args = generate_args()
    input_file_names = args.input_file_names
    output_file_name = args.output_file_name
