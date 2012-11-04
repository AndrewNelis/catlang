
from contextlib import contextmanager
import pdb
import sys

from cat.parser import Parser
from cat.stack import Stack
from cat.NS import NS

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
        
        self._flags    = {'pdb': False, 'trace': False}
        self.ns        = NS( self, funcs )
        self.parser    = Parser()
        self.stack     = Stack(initial=initial_stack)
        self.output_fn = output_fn

    def toggle_trace( self ) :
        self._flags['trace'] = not self._flags['trace']
    
#     def toggle_pdb():
#         self._flags['pdb'] = not self._flags['pdb']
#     
    def define(self, line, ns=None):
        """If a line starts with 'define', then it's a function declaration"""

        definition = self.parser.parse_definition(line)

        for word in definition.dependencies:
            if ns :
                self.stack.push( ns + ":" + word )
            
            else :
                self.stack.push(word)
            
            self.ns.exeqt( 'fetch' )

        doc = " %s %s\n\n%s" % (
                definition.name,
                definition.effect,
                definition.description,
                )

        self.ns.addWord(definition.name,
                list(self.parser.gobble(definition.definition)), doc, ns)

    def eval(self, expression):
        """Evaluate the given expression. This is the workhorse."""

#         if self._flags['pdb']:
#             pdb.set_trace()
#             toggle_pdb()
        
        # What have we been given?
        if isinstance(expression, basestring):
            if expression.strip().startswith('define '):
                self.define(expression)
                return self.stack.raw()

            # Not a 'define' but a string containing instructions
            atoms = self.parser.gobble(expression)

        elif callable(expression):
            # have something that requires immediate execution: quote & compose lambda functions
            expression()
            return self.stack.raw()

        else:
            # A list of instructions - internally a function.
            atoms = expression

        for atom in atoms:
            if self._flags['trace']:
                if not self.stack:
                    state = '_empty_'

                else:
                    state = ' '.join(map(repr, self.stack))

                print 'stack: %s' % state
                print "\natom:", atom

            # check for quoted string or variable
            if isinstance(atom, basestring) :
                if atom.startswith('"') :
                    self.stack.push(atom.strip('"'))
                    continue
                
                # not a string, try user variable (getVar handles <namespace>: prefix)
                defined, val = self.ns.getVar( atom )
                
                if defined :
                    self.stack.push( val )
                    continue
            
            # check for already converted number
            if isinstance(atom, (int, float)) :
                self.stack.push( atom )
                continue
            
            # look for a qualified object (<ns name>:<obj>
            if atom.count( ":" ) == 1 :
                ns, atom = atom.split( ":" )
            
            else :
                ns = None 
            
            # Try to get the atom as a named function next.
            try:
                defined, func, _ = self.ns.getWord(atom, ns) if ns else self.ns.getWord(atom)

            except Exception, msg:
                raise
                raise Exception, "eval: Error fetching %s (%s)" % (atom, msg)

            if defined:
                # change execution context if ns has been defined
                default = self.ns.getUserNS()   # save current execution context
                
                func = func[0]  # get the "function" ([1] is the doc)
                
                # if a different execution context is specified change to it
                if ns :
                    self.ns.changeUserNS( ns )
                
                if callable(func):
                    # It's a function i.e. built in.
                    func(self)

                else:
                    # Otherwise it's a pre-defined list.
                    self.eval(func)
                
                # restore original execution context
                self.ns.changeUserNS( default )

            # Not a function. Check for special module.function call or instance.method call
            else:
                if isinstance(atom, basestring):
                    # check for <module name>.<function name> or <instance name>.<method name>
                    mo = self.parser.parseModule.match(atom)

                    if mo:
                        # look for a user-created instance
                        inst    = self.ns.getInst( mo.group(1), ns ) if ns else self.ns.getInst( mo.group(1) )
                        is_inst = inst[0]    # inst == (T|F, instance, namespace)
                        
                        if is_inst :
                            is_callable = eval( "callable(%s)" % atom, self.ns.allInst(inst[2]) )
                        
                        else :
                            is_callable = eval( "callable(%s)" % atom, sys.modules )
                            
                        # do we have an executable?
                        if is_callable:
                            # a callable w/ or w/o arguments
                            # functions taking no arguments should use the 'nil' word to signal this fact
                            if self.stack.length() == 0:
                                args = []

                            else:
                                args = self.stack.pop()

                            if isinstance(args, basestring) and args.startswith("["):  # pylint: disable=E1103
                                args = eval(args)

                            elif isinstance(args, (list, tuple)):
                                # arguments are taken left-to-right (do arg.reverse() otherwise)
                                arg = args  # so that one can pass instances, not just strings and numbers

                            else:
                                # insert single argument into a tuple
                                arg = (args,)

                            # evaluate the module-based function or method
                            if is_inst :
                                cmd = eval( atom, globals(), self.ns.allInst(inst[2]) )
                                res = cmd( *arg )
                                
                                if res != None :
                                    self.stack.push( res )
                            
                            else :
                                cmd = eval(atom, sys.modules)
                                res = cmd( *arg )
                                
                                if res != None :
                                    self.stack.push( res )
                        
                        # not a callable
                        else :
                            cmd = atom
                            
                            if is_inst :
                                self.stack.push( eval(cmd, globals(), self.ns.allInst(inst[2])) )
                            
                            else :
                                self.stack.push( eval(cmd, sys.modules) )
                    
                    # Not a module reference. Push onto stack.
                    else :
                        self.stack.push( (ns + ":" + atom) if ns else atom )
                
                # not a string, push the value onto the stack
                else :
                    self.stack.push( atom )

        return self.stack

    def eval2(self, f1, f2):
        '''Evaluates f1() and then f2() -- needed by 'compose'
        '''
        self.eval(f1)
        return self.eval(f2)

    def output(self, msg, color=None, comma=False):
        if comma :
            print self.output_fn(msg, color),
        
        else :
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
            >>> with e.new_stack():
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
    
