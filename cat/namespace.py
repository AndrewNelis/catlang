

class _NameSpace:
    def __init__(self):
        self._ns = {}

    def set(self, word, value):
        if word in self._ns:
            print 'warn: redefinition of', word, 'from', value
        self._ns[word] = value

    def get(self, word):
        return self._ns[word]

    def as_dict(self):
        return self._ns


def define(word):
    """Decorator that inserts the wrapped function into NameSpace as <word>"""
    def _decorator(func):
        NameSpace.set(word, (func, func.__doc__))
        return func

    return _decorator


NameSpace = _NameSpace()
