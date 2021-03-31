import os
import logging


def get_all_file_paths(dir_path: str) -> list:
    """get all file paths under the specified dir path"""
    if not os.path.isdir(dir_path):
        logging.warning('The path %s is not a dir.' % dir_path)
        return []

    ret = []
    logging.info('Starts to extract all files under the dir %s' % dir_path)
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            filepath = os.path.join(root, file)
            if os.path.isfile(filepath):
                ret.append(filepath)
    logging.info('Done, %s files in total.' % len(ret))
    return ret


def filepath_ends_in(filepath: str, suffixes: list) -> bool:
    for suffix in suffixes:
        if filepath.endswith(suffix):
            return True
    else:
        return False


def del_dir_tree(path):
    if os.path.isfile(path):
        try:
            os.remove(path)
        except Exception as e:
            logging.exception(e)
    elif os.path.isdir(path):
        for item in os.listdir(path):
            itempath = os.path.join(path, item)
            del_dir_tree(itempath)
        try:
            os.rmdir(path)
        except Exception as e:
            logging.exception(e)