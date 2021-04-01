import os
from abc import ABC, abstractmethod

from utils import Stack, VALID_FILE_SUFFIX, _check_func_header_valid
from utils.file_helper import filepath_ends_in
from .content_handler import Handler, DoNothing, AbstractHandler


class FuncExtractor(ABC):
    @abstractmethod
    def extract(self, filepath: str) -> list:
        pass


class ClangFuncExtractor(FuncExtractor):
    """A function extractor supporting c language."""

    class __SimpleIncludeDefineRemover(AbstractHandler):

        def _process(self, pre_handled_content: str) -> str:
            linesep = os.linesep
            ret = []
            for line in pre_handled_content.split(linesep):
                line_striped = line.strip()
                if not line_striped.startswith('#'):
                    ret.append(line)
            return linesep.join(ret)

    def __init__(self, handler: Handler = DoNothing(), encoding: str = 'utf-8'):
        self._handler = self.__SimpleIncludeDefineRemover(handler)
        self._encoding = encoding
        self.__st = Stack()

    def _get_content(self, filepath: str) -> str:
        with open(filepath, 'r', encoding=self._encoding, newline=os.linesep) as f:
            return f.read()

    def set_encoding(self, encoding: str):
        self._encoding = encoding

    def extract(self, filepath: str) -> list:
        if not filepath_ends_in(filepath, VALID_FILE_SUFFIX):
            raise RuntimeError('The file path %s is not a valid path, it should end with one of %s' %
                               (filepath, VALID_FILE_SUFFIX))

        content = self._get_content(filepath)
        handled_content = self._handler.handle(content)
        mutable_content = handled_content
        ret = []
        st = self.__st

        while True:
            left_brace_pos = mutable_content.find('{')
            if left_brace_pos < 0:
                break

            header = mutable_content[:left_brace_pos]
            body = mutable_content[left_brace_pos:]
            st.clear()
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
            if _check_func_header_valid(header):
                pos = header.rfind(';')
                func_header = header[(pos + 1):] if pos >= 0 else header
                func_body = body[start_idx: (end_idx + 1)]
                func = func_header + func_body
                ret.append(func.strip())
            mutable_content = mutable_content[left_brace_pos + end_idx + 1:]
        return ret
