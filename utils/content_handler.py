from abc import ABC, abstractmethod
import os


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
    def process(self, pre_handled_content: str) -> str:
        pass

    def handle(self, content: str) -> str:
        pre_handled_content = self._handler.handle(content)
        return self.process(pre_handled_content)


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

    def process(self, pre_handled_content: str) -> str:
        # removes all /* ... */
        _ = self._remove0(pre_handled_content)
        # removes all //...
        return self._remove1(_)


class ZoneCompressor(AbstractHandler):
    def process(self, pre_handled_content: str) -> str:
        line_sep = os.linesep
        li = []
        for line in pre_handled_content.split(line_sep):
            line = line.strip()
            if line:
                li.append(line)
        return line_sep.join(li)
