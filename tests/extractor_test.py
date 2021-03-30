import os
from conf import ROOT_PATH
from utils.content_handler import NotesRemover
from utils.func_extractor import ClangFuncExtractor

if __name__ == '__main__':
    extractor = ClangFuncExtractor(NotesRemover())
    ret = extractor.extract(os.path.join(ROOT_PATH, 'inputs/bfq-iosched.h'))
    for i, _ in enumerate(ret):
        with open(os.path.join(ROOT_PATH, 'outputs/%s.c' % i), 'w') as f:
            f.write(_)

