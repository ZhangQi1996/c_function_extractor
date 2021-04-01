import re

SINGLE_CHAR_DEFINED_NAME_PATTERN = re.compile(
    '[a-zA-Z0-9_$]',
    re.RegexFlag.MULTILINE
)

DEFINED_NAME_PATTERN = re.compile(
    '([a-zA-Z0-9_$]+)',
    re.RegexFlag.MULTILINE
)

FUNC_HEADER_PATTERN = re.compile(
    '[a-zA-Z0-9_$,\\*&\\[\\]]+\\s+[a-zA-Z0-9_$]+\\s*\\(([a-zA-Z0-9_$,\\*&\\[\\]\\s]*)\\)\\s*$',
    re.RegexFlag.MULTILINE | re.RegexFlag.DOTALL
)


def _check_func_header_valid(s: str):
    matcher = FUNC_HEADER_PATTERN.search(s)
    return matcher is not None


VALID_FILE_SUFFIX = ['.c', '.h']


class Stack(object):
    def __init__(self):
        self.li = []

    def empty(self):
        return len(self.li) == 0

    def push(self, o):
        self.li.append(o)

    def pop(self):
        return self.li.pop(-1)

    def peek(self):
        return self.li[-1]

    def clear(self):
        self.li.clear()
