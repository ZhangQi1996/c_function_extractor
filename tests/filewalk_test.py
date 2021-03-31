from utils import file_helper
from conf import ROOT_PATH

if __name__ == '__main__':
    print(ROOT_PATH)
    print(file_helper.get_all_file_paths(ROOT_PATH))