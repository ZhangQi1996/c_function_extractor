from utils.content_handler import ClangFuncAbstractHandler
from conf import ROOT_PATH, ENCODING
import os
import re
from utils import FUNC_HEADER_PATTERN, _check_func_header_valid

if __name__ == '__main__':
    filepath = os.path.join(ROOT_PATH, 'outputs/dwm.c_func40.c')
    with open(filepath, 'r', encoding=ENCODING) as f:
        content = f.read()
    print(ClangFuncAbstractHandler(0).handle(content))

    print("========")

    print(ClangFuncAbstractHandler(3).handle(content))