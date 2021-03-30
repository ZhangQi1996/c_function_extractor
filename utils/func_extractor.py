from abc import ABC, abstractmethod
from .content_handler import Handler, DoNothing, AbstractHandler
import os
import re


class FuncExtractor(ABC):
    @abstractmethod
    def extract(self, filepath: str) -> list:
        pass


class ClangFuncExtractor(FuncExtractor):
    class __Stack(object):
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

    def __init__(self, handler: Handler = DoNothing(), encoding: str = 'utf-8'):
        self._handler = self.__SimpleIncludeDefineRemover(handler)
        self._encoding = encoding

    def _get_content(self, filepath: str) -> str:
        with open(filepath, 'r', encoding=self._encoding) as f:
            return f.read()

    def set_encoding(self, encoding: str):
        self._encoding = encoding

    def _check_func_header_valid(self, s: str):
        matcher = self.FUNC_HEADER_PATTERN.findall(s)
        return len(matcher) > 0

    def extract(self, filepath: str) -> list:
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
            st = self.__Stack()
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