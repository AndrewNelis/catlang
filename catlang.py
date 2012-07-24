#!/usr/bin/python
#
# catlang.py - Andrew Nelis <andrew.nelis@gmail.com>
#
# A basic interpreter for the cat language.
#
# Usage:
#
# ./catlang.py --test   - Run tests (that this thing works!)
# ./catlang.py --eval "code" - Evaluate the given source
# ./catlang.py - (no arguments) Start an interactive session.
#
# If you add a new function, be sure to add a test (or two) to the runtest
# function.
#
# TODO:
# - Lists and types properly.
# - Catch programming errors e.g. 1 0 /
# - Implement the rest of the standard functions.

__version__ = '0.5'

import cmd
import re
import sys

# For getting the name and definition text of a function.
define_re = re.compile('define\s*(?P<name>\S+)\s*{(?P<definition>[^}]*)}\s*')


class Functions:
    """Return a function for a given symbol. Also maintains
    a list of user defined functions."""
    def __init__(self, userfunctions={}):
        """Constructor"""
        # Initial map of symbols to functions
        # (as well as the methods defined on this class)
        self.fnmap = {
            '+': '_add',
            '-': '_sub',
            '*': '_mul',
            '/': '_div',
            '=': '_equ',
            '!=': '_nequ',
            '<': '_lt',
            '>': '_gt',
            '<=': '_lte',
            '>=': '_gte',
            'str_cat': '_add',  # Go python!
            'if': '_if',
            '%': '_mod',
            '%/': '_divmod',
        }
        self.fnmap.update(userfunctions)

    def getFunction(self, what):
        """Called by the interpreter to get a function named <what>.
        As a name may be none we return a flag stating whether <what>
        was defined, followed by it's definition.
        """
        if not isinstance(what, str):
            return False, None
        elif what in self.fnmap:
            # Look in the function map...
            function = self.fnmap[what]
            if isinstance(function, list):
                # For either a user defined function
                return True, function
            else:
                # Or a method alias.
                return True, getattr(self, function)
        elif hasattr(self, what):
            # Might be a named method.
            return True, getattr(self, what)

        return (False, None)

    def setFunction(self, name, definition):
        """Called to *define* new functions"""
        self.fnmap[name] = definition

    # Methods defining functions with invalid python names.
    # They're prefixed with underscores so people don't unintentionally
    # re-define them and so we can identify these when
    # we call 'defs'

    def _add(self, stack):
        """Defines +"""
        a, b = stack.pop2()
        stack.push(b + a)

    def _sub(self, stack):
        """Defines -"""
        a, b = stack.pop2()
        stack.push(b - a)

    def _mul(self, stack):
        """Defines *"""
        a, b = stack.pop2()
        stack.push(a * b)

    def _div(self, stack):
        """Defines /"""
        a, b = stack.pop2()
        stack.push(b / a)

    def _equ(self, stack):
        """Defines ="""
        a, b = stack.pop2()
        stack.push(a == b)

    def _nequ(self, stack):
        """Defines !="""
        a, b = stack.pop2()
        stack.push(a != b)

    def _gt(self, stack):
        """Defines >"""
        a, b = stack.pop2()
        stack.push(b > a)

    def _lt(self, stack):
        """Defines <"""
        a, b = stack.pop2()
        stack.push(b < a)

    def _gte(self, stack):
        """Defines >="""
        a, b = stack.pop2()
        stack.push(b >= a)

    def _lte(self, stack):
        """Defines <="""
        a, b = stack.pop2()
        stack.push(b <= a)

    def _if(self, stack):
        """Defines if"""
        ffalse, ftrue, truth = stack.popn(3)
        if truth:
            stack.push(ftrue)
        else:
            stack.push(ffalse)
        self.eval(stack)

    def _mod(self, stack):
        """Defines %"""
        a, b = stack.pop2()
        stack.push(b % a)

    def _divmod(self, stack):
        """Defines %/"""
        a, b = stack.pop2()
        stack.push(divmod(b, a), multi=True)

    # Now begins methods implementing functions of the same name.
    # @@ Could write docstrings and tie in with the interpreter to
    # get help from 'em.

    def clear(self, stack):
        stack.clear()

    def pop(self, stack):
        stack.pop()

    def dup(self, stack):
        val = stack.pop()
        stack.push((val, val), multi=True)

    def swap(self, stack):
        a, b = stack.pop2()
        stack.push((a, b), multi=True)

    def swapd(self, stack):
        a, b, c = stack.popn(3)
        stack.push((b, c, a), multi=True)

    def dupd(self, stack):
        a, b = stack.pop2()
        stack.push((b, b, a), multi=True)

    def eval(self, stack):
        stack.eval(stack.pop())

    def n(self, stack):
        stack.push(range(stack.pop()))

    def count(self, stack):
        stack.push(len(stack.pop()))

    def head(self, stack):
        stack.push(stack.pop()[0])

    def tail(self, stack):
        stack.push(stack.pop()[1:])

    def rev(self, stack):
        val = stack.pop()
        val.reverse()
        stack.push(val)

    def map(self, stack):
        func, elements = stack.pop2()
        # Evaluate the function with each of the elements.
        results = []
        # Push the value onto the stack and evaluate the function.
        # in a new interpreter.
        for element in elements:
            # Create a new
            newstack = CatStack([element], self.fnmap)
            newstack.eval(func)
            results.extend(newstack.popall())
        stack.push(results)

    def even(self, stack):
        stack.push((stack.pop() % 2) == 0)

    def reduce(self, stack):
        func, elements = stack.pop2()
        results = []
        for element in elements:
            newstack = CatStack([element])
            newstack.eval(func)
            if newstack.pop():
                results.append(element)
        stack.push(results)

    def defs(self, stack):
        functions = self.fnmap.keys()
        for method in dir(self):
            if method not in functions and not method.startswith('_'):
                functions.append(method)
        functions.remove('setFunction')
        functions.remove('getFunction')
        functions.sort()
        print ' '.join(functions)


class CatStack:

    def __init__(self, stack=[], funcs={}):
        self.stack = stack
        self.funcs = Functions(funcs)

    def define(self, line):
        """If a line starts with 'define', then it's a function declaration"""
        match = define_re.match(line)
        if not match:
            print 'error: expect functions of the form "define name {definition}"'
        else:
            name, definition = match.groups()
            # define works differently. In an easier fashion than
            # waiting for the function to arrive.
            self.funcs.setFunction(name, list(self.gobble(definition)))

    def norm(self, value):
        """Normalise the given value. So if it's an integer, cast it"""
        if value.isdigit():
            return int(value)
        elif value.startswith('-') and value[1:].isdigit():
            return int(value)
        else:
            return value

    def gobble(self, expr):
        """Return the given expression a bit at a time allowing for string
        quoting and anonymous functions"""

        instring = False
        buff = ''
        while expr:
            char = expr[0]
            if char == '[' and not instring:
                end = expr.find(']')
                function = expr[1:end]
                expr = expr[end + 1:]
                yield list(self.gobble(function))
            elif char == '"':
                if instring:
                    yield buff
                    buff = ''
                    instring = False
                else:
                    instring = True
            elif char == ' ':
                if instring:
                    # Quoted strings can contain spaces.
                    buff += char
                elif buff.strip():
                    # Given character may be a number.
                    yield self.norm(buff)
                    buff = ''
            elif char not in ' []':
                buff += char
            expr = expr[1:]
        if buff:
            yield self.norm(buff)

    def eval(self, expression):
        """Evaluate the given expression"""

        # What have we been given?
        if isinstance(expression, str):
            if expression.startswith('define '):
                self.define(expression)
                return self.stack
            # A string containing instructions
            atoms = self.gobble(expression)
        else:
            # A list of instructions - internally a function.
            atoms = expression

        getFunction = self.funcs.getFunction

        for atom in atoms:
            # Try to get the atom as a named function first.
            try:
                defined, func = getFunction(atom)
            except:
                raise Exception("Error fetching %s" % atom)
            if defined:
                if callable(func):
                    # It's a function i.e. built in.
                    func(self)
                else:
                    # Otherwise it's a pre-defined list.
                    self.eval(func)
            else:
                # At the moment, undefined elements are pushed onto the stack
                # Is this a good idea?
                self.push(atom)

        return self.stack

    # Functions for manipulating the stack.

    def push(self, value, multi=False):
        if multi:
            map(self.stack.append, value)
        else:
            self.stack.append(value)

    def pop(self):
        return self.stack.pop()

    def pop2(self):
        return self.stack.pop(), self.stack.pop()

    def popn(self, n):
        return [self.stack.pop() for x in range(n)]

    def popall(self):
        all = self.stack
        all.reverse()
        self.stack = []
        return all

    def clear(self):
        self.stack = []

    def __str__(self):
        """Return a string representation of the stack"""
        if not self.stack:
            state = '_empty_'
        else:
            state = ' '.join(map(repr, self.stack))
        return 'main stack: %s' % state


def runtests():
    cs = CatStack()
    e = cs.eval

    tests = (
        # List of ('input expression', [expected stack])
        ('3 5 +', [8]),
        ('10 9 -', [8, 1]),
        ('2 3 *', [8, 1, 6]),
        ('20 10 /', [8, 1, 6, 2]),
        ('+ + +', [17]),
        ('1 2 3 4 clear', []),
        ('clear 2 2 =', [True]),
        ('clear 2 2 !=', [False]),
        ('clear 2 1 >', [True]),
        ('clear 2 1 <', [False]),
        ('clear 2 1 >=', [True]),
        ('clear 2 1 <=', [False]),
        ('clear "able" "baker"', ['able', 'baker']),
        ('clear "charlie" "dog" str_cat', ['charliedog']),
        ('clear "a" " " "b" str_cat str_cat', ['a b']),
        ('clear 1 2 pop', [1]),
        ('clear 1 2 3 dup', [1, 2, 3, 3]),
        ('clear 1 2 swap', [2, 1]),
        ('clear 5 6 7 swapd', [6, 5, 7]),
        ('clear 9 8 7 dupd', [9, 8, 8, 7]),
        ('clear 9 [1 2 3] 9', [9, [1, 2, 3], 9]),
        ('clear 1 [2 +] eval', [3]),
        ('clear 1 ["t"] ["f"] if', ["t"]),
        ('clear 0 ["t"] ["f"] if', ["f"]),
        ('clear 1 2 > ["t"] ["f"] if', ["f"]),
        ('clear 9 5 n 9', [9, [0, 1, 2, 3, 4], 9]),
        ('clear 3 n dup count', [[0, 1, 2], 3]),
        ('clear 3 n head', [0]),
        ('clear 3 n tail', [[1, 2]]),
        ('clear 3 n rev', [[2, 1, 0]]),
        ('clear 3 n [] map', [[0, 1, 2]]),
        ('clear 3 n [1 +] map', [[1, 2, 3]]),
        ('clear 5 even 0 even 1 even 8 even', [False, True, False, True]),
        ('clear 6 n [even] reduce', [[0, 2, 4]]),
        ('clear 10 9 %', [1]),
        ('clear 10 5 %/', [2, 0]),
        ('clear', []),
        ('define ++ {1 +}', []),
        ('define -- {1 -}', []),
        ('1 ++ 2 --', [2, 1]),
    )

    for expression, result in tests:
        value = e(expression)
        assert value == result, (expression, result, value)


class CatInteractive(cmd.Cmd):
    """Command line interpreter."""
    prompt = '>> '
    intro = """Python Cat Programming Language interpreter (v%s).
Type "quit" to exit.""" % __version__

    def __init__(self):
        self.cat = CatStack()
        # Flag, whether we're writing a definition or not.
        cmd.Cmd.__init__(self)

    def do_quit(self, line):
        """Exits the interpreter"""
        # Annoying after the second time.
        # print "Bye!"
        sys.exit(0)

    def default(self, line):
        self.cat.eval(line.strip())
        print self.cat

    def emptyline(self):
        # Don't do anything if the line is blank.
        # (by default, cmd.Cmd will execute the last command again. Naughty!)
        pass

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # @@ There's a module for this ;-)
        if sys.argv[1] in ('-t', '--test'):
            runtests()
        elif sys.argv[1] in ('-e', '--eval'):
            cat = CatStack()
            cat.eval(' '.join(sys.argv[2:]))
            print cat
    else:
        cint = CatInteractive()
        cint.cmdloop()
