"""
    Words defined in python register themselves like so:

    user = Definitions('user')  # 'user' being the

    define = user.define

    @define('+')
    def plus(stack):
        stack.push(stack.pop() + stack.pop())
"""


class Definitions:

    def __init__(self, ns_name):
        self.ns_name = ns_name
        self.definitions = {}

    def define(self, name):
        def _decorator(function):
            self.definitions[name] = (function, function.__doc__)
            return function
        return _decorator

    def populate(self, ns_dict):
        """
            Update the namespace with what we've defined for this namespace.
        """
        if self.ns_name not in ns_dict:
            ns_dict[self.ns_name] = {}

        ns_dict[self.ns_name].update(self.definitions)
