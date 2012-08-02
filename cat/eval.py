
from contextlib import contextmanager
import pdb
import sys

from cat.parser import Parser
from cat.stack import Stack


# TODO: This should go.
import functions


# These flags should be on the evaluator itself...

_flags = {'pdb': False, 'trace': False}


def toggle_trace():
    _flags['trace'] = not _flags['trace']


def toggle_pdb():
    _flags['pdb'] = not _flags['pdb']


class CatEval:
    '''
        Implements eval function
    '''

    def __init__(self, initial_stack=None, funcs=None, output_fn=None):
        '''
        Initialize the stack and define a bunch of regular expressions

        :param stack: an initial stack (default: [])
        :type stack: list
        :param funcs: an initial collection of user-defined functions (default: {})
        :type funcs: dictionary
        :rtype: none
        '''
        if initial_stack is None:
            initial_stack = []

        if funcs is None:
            funcs = {}

        self.funcs = functions.Functions(funcs)
        self.parser = Parser()
        self.stack = Stack(initial=initial_stack)
        self.output_fn = output_fn

    def define(self, line):
        """If a line starts with 'define', then it's a function declaration"""

        definition = self.parser.parse_definition(line)

        for word in definition.dependencies:
            self.push(word)
            self.funcs.fetch(self)

        doc = " %s %s\n\n%s" % (
                definition.name,
                definition.effect,
                definition.description,
                )

        self.funcs.setFunction(definition.name,
                list(self.parser.gobble(definition.definition)), doc)

    def eval(self, expression):
        """Evaluate the given expression. This is the workhorse."""

        if _flags['pdb']:
            pdb.set_trace()
            toggle_pdb()

        # What have we been given?
        if isinstance(expression, basestring):
            if expression.strip().startswith('define '):
                self.define(expression)
                return self.stack.raw()

            # Not a 'define' but a string containing instructions
            atoms = self.parser.gobble(expression)

        elif callable(expression):
            # have something that requires immediate execution
            expression()
            return self.stack

        else:
            # A list of instructions - internally a function.
            atoms = expression

        getFunction = self.funcs.getFunction

        for atom in atoms:
            if _flags['trace']:
                if not self.stack:
                    state = '_empty_'

                else:
                    state = ' '.join(map(repr, self.stack))

                print 'stack: %s' % state
                print "atom:", atom

            # check for quoted string
            if isinstance(atom, basestring) and atom.startswith('"'):
                self.push(atom.strip('"'))
                continue

            # Try to get the atom as a named function first.
            try:
                defined, func = getFunction(atom)

            except Exception, msg:
                raise
                raise Exception, "eval: Error fetching %s (%s)" % (atom, msg)

            if defined:
                if callable(func):
                    # It's a function i.e. built in.
                    func(self)

                else:
                    # Otherwise it's a pre-defined list.
                    self.eval(func)

            else:
                # check for special module.function call, instance.method call, or user variable
                if isinstance(atom, basestring):
                    # check for <module name>.<function name> or <instance name>.<method name>
                    mo = self.parser.parseModule.match(atom)

                    if mo:
                        # look for a user-created instance
                        search = [self.funcs.userNS] + self.funcs.NSdict[self.funcs.userNS]['__links__']

                        for ns in search:
                            is_inst = mo.group(1) in self.funcs.NSdict[ns]['__inst__']

                            if is_inst:
                                break

                        if is_inst:
                            is_callable = callable(self.funcs.NSdict[ns]['__inst__'][atom])

                        else:
                            # FIX: Shouldn't use eval.
                            is_callable = eval("callable(%s)" % atom, sys.modules)

                        # do we have an executable?
                        if is_callable:
                            # a callable w/ or w/o arguments
                            # functions taking no arguments should use the 'nil' word to signal this fact
                            if self.length() == 0:
                                args = []

                            else:
                                args = self.pop()

                            if isinstance(args, basestring) and args.startswith("["):  # pylint: disable=E1103
                                args = eval(args)

                            elif isinstance(args, (list, tuple)):
                                # arguments are taken left-to-right (do arg.reverse() otherwise)
                                arg = str(tuple(args))

                            else:
                                # insert single argument into a tuple
                                arg = str((args,))

                            # evaluate the module-based function
                            cmd = "%s%s" % (atom, arg)

                        # not a callable
                        else:
                            cmd = atom

                        if is_inst:
                            self.push(eval(cmd, globals(), self.funcs.NSdict[ns]['__inst__']))

                        else:
                            self.push(eval(cmd, sys.modules))

                    # Not a module reference, check for a user variable
                    else:
                        defined, val = self.funcs.getVar(atom)

                        if defined:
                            self.push(val)

                        else:
                            self.push(atom)

                # not a string, push the value onto the stack
                else:
                    self.push(atom)

        return self.stack

    def eval2(self, f1, f2):
        '''Evaluates f1() and then f2() -- needed by 'compose'
        '''
        self.eval(f1)
        return self.eval(f2)

    def output(self, msg, color=None):
        print self.output_fn(msg, color)

    def __getattr__(self, what):
        """
            BAD: Mimic old behaviour, pretend CatEval has
                the old stack methods on it.

        """
        return getattr(self.stack, what)

    def __str__(self):
        return str(self.stack)

    @contextmanager
    def new_stack(self, content=None):
        """
            >>> e = CatEval(initial_stack=[1,2,3])
            >>> print e
            ===> 1 2 3
            >>> with e.empty_stack():
            ...    print e
            _empty_
            >>> print e
            ===> 1 2 3
        """
        old_stack = self.stack
        self.stack = Stack(initial=content)
        try:
            yield
        finally:
            self.stack = old_stack
