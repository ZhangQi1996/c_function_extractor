import argparse
import logging
from utils.content_handler import NotesRemover
from utils.func_extractor import ClangFuncExtractor
from utils.file_helper import get_all_file_paths, filepath_ends_in, del_dir_tree
from conf import ENCODING
import os


def generate_args():
    parser = argparse.ArgumentParser(
        description='A extractor used to extract all clang functions in specified file dir or c/cpp files.')
    parser.add_argument('-f', '--input_files', dest='input_files', metavar='INPUT_FILE', nargs='*',
                        help='Specifies which files will be used to extract.')
    parser.add_argument('-d', '--input_dir', dest='input_dir', metavar='INPUT_DIR', nargs='?',
                        help='Specifies which dir will be used to extract.')
    parser.add_argument('-D', '--output_dir', dest='output_dir',
                        help='Specifies the dir at which all extracted results would be stored.')
    parser.add_argument('--clear_output_dir', dest='clear_output_dir', action='store_true',
                        help='Means if clear all files under output dir before extract.')
    return parser.parse_args()


def conf_log():
    from conf import LOG_STREAM, LOG_LEVEL, LOG_DATE_FMT, LOG_FMT
    logging.basicConfig(stream=LOG_STREAM, level=LOG_LEVEL, datefmt=LOG_DATE_FMT, format=LOG_FMT)


def create_dir_if_not_exists(dir: str):
    if os.path.exists(dir) and os.path.isdir(dir):
        return
    os.mkdir(dir)


def generate_func_extracted_filename(original_filepath: str, i: int) -> str:
    return original_filepath.split(os.sep)[-1] + '_func%s' % i + '.c'


def check_args(args):
    input_files = args.input_files
    input_dir = args.input_dir
    output_dir = args.output_dir
    if input_files is None and input_dir is None:
        raise RuntimeError('Plz specify one of the opt -f or -d.')
    if output_dir is None:
        raise RuntimeError('Plz specify the opt -D.')
    if input_files is not None:
        for filepath in input_files:
            if not os.path.isfile(filepath):
                raise RuntimeError('The target under file path %s is not a file.' % filepath)
    if input_dir is not None:
        if not os.path.isdir(input_dir):
            raise RuntimeError('The target under dir path %s is not a dir.' % input_dir)

    logging.info('The opt clear_output_dir is set to %s.' % args.clear_output_dir)
    if args.clear_output_dir:
        del_dir_tree(output_dir)
    # creates output-dir if
    create_dir_if_not_exists(output_dir)


if __name__ == '__main__':
    conf_log()
    args = generate_args()
    check_args(args)
    input_files = args.input_files
    input_dir = args.input_dir
    output_dir = args.output_dir

    func_extractor = ClangFuncExtractor(NotesRemover(), encoding=ENCODING)
    in_files = []
    if input_files is not None:
        in_files = input_files
    elif input_dir is not None:
        in_files = get_all_file_paths(input_dir)

    # removes all file not ending with specified suffix.
    _ = in_files
    in_files = []
    for filepath in _:
        if filepath_ends_in(filepath, ClangFuncExtractor.VALID_FILE_SUFFIX):
            in_files.append(filepath)
    logging.info('After removing all not ending with specified suffix filepath, '
                 '%s clang file in total and removed %s' % (len(in_files), len(_) - len(in_files)))

    logging.info('Starts to extract all clang function from files.')
    for i, filepath in enumerate(in_files):
        funcs_extracted = func_extractor.extract(filepath)
        for j, func_extracted in enumerate(funcs_extracted):
            func_extracted_filename = generate_func_extracted_filename(filepath, j)
            print(output_dir)
            output_file_path = os.path.join(output_dir, func_extracted_filename)
            print(output_file_path)
            with open(file=output_file_path, mode='w', encoding=ENCODING, newline=os.linesep) as f:
                f.write(func_extracted)
        logging.info('Current progress is %s%%', 100.0 * (i + 1) / len(in_files))
    logging.info('Done.')
