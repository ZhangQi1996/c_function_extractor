from utils.content_handler import NotesRemover, ZoneCompressor
from conf import ROOT_PATH
import os

if __name__ == '__main__':
    handler = ZoneCompressor(NotesRemover())

    with open(os.path.join(ROOT_PATH, 'inputs/badblocks.c'), 'r') as rf:
        content = rf.read()
        content = handler.handle(content)
        with open(os.path.join(ROOT_PATH, 'outputs/badblocks.c'), 'w') as wf:
            wf.write(content)

