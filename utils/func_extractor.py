from abc import ABC, abstractmethod
from .content_handler import Handler, DoNothing, AbstractHandler
import os
import re
from utils.file_helper import filepath_ends_in
from utils import Stack


class FuncExtractor(ABC):
    @abstractmethod
    def extract(self, filepath: str) -> list:
        pass


class ClangFuncExtractor(FuncExtractor):
    """A function extractor supporting c language."""
    class __SimpleIncludeDefineRemover(AbstractHandler):

        def process(self, pre_handled_content: str) -> str:
            linesep = os.linesep
            ret = []
            for line in pre_handled_content.split(linesep):
                line_striped = line.strip()
                if not line_striped.startswith('#'):
                    ret.append(line)
            return linesep.join(ret)

    FUNC_HEADER_PATTERN = re.compile(
        '[a-zA-Z0-9_$,\\*&\\[\\]]+\\s+[a-zA-Z0-9_$,\\*&\\[\\]]+\\s*\\([a-zA-Z0-9_$,\\*&\\[\\]\\s]*\\)\\s+$',
        re.RegexFlag.MULTILINE | re.RegexFlag.DOTALL
    )

    VALID_FILE_SUFFIX = ['.c', '.h']

    def __init__(self, handler: Handler = DoNothing(), encoding: str = 'utf-8'):
        self._handler = self.__SimpleIncludeDefineRemover(handler)
        self._encoding = encoding

    def _get_content(self, filepath: str) -> str:
        with open(filepath, 'r', encoding=self._encoding, newline=os.linesep) as f:
            return f.read()

    def set_encoding(self, encoding: str):
        self._encoding = encoding

    def _check_func_header_valid(self, s: str):
        matcher = self.FUNC_HEADER_PATTERN.findall(s)
        return len(matcher) > 0

    def extract(self, filepath: str) -> list:
        if not filepath_ends_in(filepath, self.VALID_FILE_SUFFIX):
            raise RuntimeError('The file path %s is not a valid path, it should end with one of %s' %
                               (filepath, self.VALID_FILE_SUFFIX))

        content = self._get_content(filepath)
        handled_content = self._handler.handle(content)
        mutable_content = handled_content
        ret = []

        while True:
            left_brace_pos = mutable_content.find('{')
            if left_brace_pos < 0:
                break

            header = mutable_content[:left_brace_pos]
            body = mutable_content[left_brace_pos:]
            st = Stack()
            start_idx, end_idx = 0, 0
            for i, c in enumerate(body):
                if c == '{':
                    st.push(c)
                elif c == '}':
                    if st.peek() != '{':
                        raise RuntimeError('error.')
                    st.pop()
                    if st.empty():
                        end_idx = i
                        break
            if self._check_func_header_valid(header):
                pos = header.rfind(';')
                func_header = header[(pos + 1):] if pos >= 0 else header
                func_body = body[start_idx: (end_idx + 1)]
                func = func_header + func_body
                ret.append(func.strip())
            mutable_content = mutable_content[left_brace_pos + end_idx + 1:]
        return ret
