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
