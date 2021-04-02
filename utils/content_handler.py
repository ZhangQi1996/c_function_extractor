import os
import re
from abc import ABC, abstractmethod

from utils import FUNC_HEADER_PATTERN, DEFINED_NAME_PATTERN


class Handler(ABC):
    @abstractmethod
    def handle(self, content: str) -> str:
        pass


class DoNothing(Handler):

    def handle(self, content: str) -> str:
        return content


class AbstractHandler(Handler, ABC):

    def __init__(self, handler: Handler = DoNothing()):
        self._handler = handler

    @abstractmethod
    def _process(self, pre_handled_content: str) -> str:
        pass

    def handle(self, content: str) -> str:
        pre_handled_content = self._handler.handle(content)
        return self._process(pre_handled_content)


class NotesRemover(AbstractHandler):

    @staticmethod
    def _remove0(s: str):
        """remove all note structures like /*...*/"""
        while True:
            start_pos = s.find('/*')
            if start_pos != -1:
                s_l = s[:start_pos]
                s_r = s[(start_pos + 2):]
                end_pos = s_r.find('*/')
                if end_pos == -1:
                    raise RuntimeError('the notes format is illegal.')
                s_r = s_r[(end_pos + 2):]
                s = s_l + s_r
            else:
                break
        return s

    @staticmethod
    def _remove1(s: str):
        """remove all note structures like //..."""
        line_sep = os.linesep
        li = []
        for line in s.split(line_sep):
            pos = line.find('//')
            li.append(line if pos < 0 else line[:pos])
        return line_sep.join(li)

    def _process(self, pre_handled_content: str) -> str:
        # removes all /* ... */
        _ = self._remove0(pre_handled_content)
        # removes all //...
        return self._remove1(_)


class ZoneCompressor(AbstractHandler):
    """Just remove all whitespaces around per line."""

    def _process(self, pre_handled_content: str) -> str:
        line_sep = os.linesep
        li = []
        for line in pre_handled_content.split(line_sep):
            line = line.strip()
            if line:
                li.append(line)
        return line_sep.join(li)


class _Level0(AbstractHandler):
    """do nothing"""

    def _process(self, pre_handled_content: str) -> str:
        return pre_handled_content


def replace(content: str, pattern_str: str, replace_str: str) -> str:
    def replace_(group_):
        header = group_.group(1)
        rear = group_.group(2)
        return group_.group(0) if header.strip() == '->' else header + replace_str + rear

    pattern = re.compile('(.[^a-zA-Z0-9_$\\.]\\s*)%s([^a-zA-Z0-9_$])' % pattern_str, re.RegexFlag.MULTILINE | re.DOTALL)
    # exec two replacements at least
    content_a = pattern.sub(replace_, content)
    content_b = pattern.sub(replace_, content_a)
    while content_a != content_b:
        content_a = pattern.sub(replace_, content_b)
        content_b = pattern.sub(replace_, content_a)
    return content_a


def get_func_body_without_brace(func_content: str) -> str:
    func_content = func_content.strip()
    if not func_content.endswith('}'):
        raise RuntimeError('The format of the function content is invalid.')
    pos = func_content.find('{')
    if pos < 0:
        raise RuntimeError('The format of the function content is invalid.')
    return func_content[(pos + 1): -1].strip()


class _Level1(AbstractHandler):
    """Formal parameter abstraction"""
    TAG = 'FPARAM'

    def __init__(self):
        super().__init__(handler=_Level0())

    def _process(self, pre_handled_content: str) -> str:
        # get all params in func header
        func_header = pre_handled_content[:pre_handled_content.find('{')].strip()
        matcher = FUNC_HEADER_PATTERN.search(func_header)
        # e.g. static long utf8decodebyte(const char c, size_t *i) -> const char c, size_t *i
        params_content = matcher.group(1).strip()
        for param_content in params_content.split(','):
            param_content_reversed = param_content.strip()[::-1]
            if len(param_content_reversed) == 0:
                continue
            matcher = DEFINED_NAME_PATTERN.search(param_content_reversed)
            candidate = matcher.group(1)[::-1]
            pre_handled_content = replace(pre_handled_content, candidate, self.TAG)
        return pre_handled_content


class _Level2(AbstractHandler):
    """Local variable abstraction"""
    TAG = 'LVAR'
    PATTERN = re.compile('([a-zA-Z_$][a-zA-Z0-9_$]*)\\s*([\\[\\]\\+\\-*/=~.|&^,;\\)])')
    STOP_LIST = [
        'char', 'double', 'enum', 'float', 'int', 'long', 'short', 'signed', 'struct', 'union',
        'unsigned', 'void', 'for', 'do', 'while', 'break', 'continue', 'if', 'else', 'goto', 'switch',
        'case', 'default', 'return', 'auto', 'extern', 'register', 'static', 'const', 'sizeof', 'typedef', 'volatile',
        'FPARAM', 'LVAR', 'FUNCCALL'
    ]

    def __init__(self):
        super().__init__(handler=_Level1())

    def _process(self, pre_handled_content: str) -> str:
        func_body = get_func_body_without_brace(pre_handled_content)
        iter_ = self.PATTERN.finditer(func_body)
        set_ = set()
        extra_stop_list = []
        for item in iter_:
            candidate = item.group(1)
            follower_ch = item.group(2)
            if follower_ch == '*':
                last_idx = item.span()[-1]
                follower_str = func_body[last_idx:]
                if re.match('^[\\s\\*]*[a-zA-Z0-9_$]+', follower_str, re.RegexFlag.MULTILINE):
                    extra_stop_list.append(candidate)
                    continue
            set_.add(candidate)
        for candidate in set_:
            if candidate not in self.STOP_LIST and candidate not in extra_stop_list:
                pre_handled_content = replace(pre_handled_content, candidate, self.TAG)
        return pre_handled_content


class _Level3(AbstractHandler):
    """Function call abstraction"""
    TAG = 'FUNCCALL'
    STOP_LIST = [
        'if', 'while', 'for', 'switch'
    ]
    PATTERN = re.compile('([a-zA-Z0-9_$]+)\\s*\\(', re.RegexFlag.MULTILINE)

    def __init__(self):
        super().__init__(handler=_Level2())

    def _process(self, pre_handled_content: str) -> str:
        func_body = get_func_body_without_brace(pre_handled_content)
        candidates = self.PATTERN.findall(func_body)
        set_ = set()
        for candidate in candidates:
            if candidate not in self.STOP_LIST:
                set_.add(candidate)
        for candidate in set_:
            pre_handled_content = replace(pre_handled_content, candidate, self.TAG)
        return pre_handled_content


class ClangFuncAbstractHandler(AbstractHandler):
    LEVEL_MAP = {
        0: _Level0(),
        1: _Level1(),
        2: _Level2(),
        3: _Level3(),
    }

    def __init__(self, level=0, handler=DoNothing()):
        super().__init__(handler=handler)
        if level not in self.LEVEL_MAP.keys():
            raise RuntimeError('An unsupported abstraction level %s.' % level)
        self._abstract_handler = self.LEVEL_MAP[level]

    def _process(self, pre_handled_content: str) -> str:
        return self._abstract_handler.handle(pre_handled_content)


class ClangFuncNormalizer(AbstractHandler):
    # used to reduce redundant whitespaces
    PATTERN = re.compile('\\s+', re.RegexFlag.MULTILINE)
    PLACEHOLDER = ' '

    def _process(self, pre_handled_content: str) -> str:
        func_content = self.PATTERN.sub(self.PLACEHOLDER, pre_handled_content)

        def replace_(group_):
            span = group_.span()
            l = func_content[span[0] - 1]
            r = func_content[span[1]]
            if DEFINED_NAME_PATTERN.match(l) is not None and DEFINED_NAME_PATTERN.match(r) is not None:
                return ClangFuncNormalizer.PLACEHOLDER
            else:
                return ''
        return self.PATTERN.sub(replace_, func_content).lower()
