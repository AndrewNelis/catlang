#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# catlang.py - Andrew Nelis <andrew.nelis@gmail.com>
#            - extended by Wayne Wiitanen <wiitanen@paonia.com> June, 2012
#
# An interpreter for the cat language.
#
# Usage:
#
# ./catlang.py --eval "code" - Evaluate the given source
# ./catlang.py - (no arguments) Start an interactive session.
#
# If you add a new function, be sure to add a test (or two) to the runtest
# function.
#
# LICENSE: LGPL
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License (LGPL) as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA,
# or see http://www.gnu.org/copyleft/lesser.html

__version__ = '0.6'

import pdb
import platform
import re
import sys

from types import StringType, FunctionType, ListType, TupleType, LambdaType

# set up to handle colored text to console
try:
    from termcolor import colored

except ImportError:
    def colored(text, _):
        return text

if platform.system().lower() == 'windows':
    try:
        import colorama  # pylint: disable=F0401
        colorama.init()

    except ImportError:
        pass


# debugging switches
_flags = {
    'trace': False,
    'pdb': False,
}


def toggle_trace():
    _flags['trace'] = not _flags['trace']


def toggle_pdb():
    _flags['pdb'] = not _flags['pdb']


import functions
import lang_tests


class Cat:
    '''
    Implements the main stack for the Cat language
    Implements a "parser" for input lines
    Implements eval function
    Implements a variety of stack manipulation functions
    '''
    def _collectFunction(self, line, dopen='[', dclose=']'):
        '''
        returns the string enclosed between the open and close delimiters

        :param line: the string to be analyzed
        :type line: string
        :param dopen: the opening delimiter
        :type dopen: string
        :param close: the closing delimiter
        :type close: string
        :rtype: string
        '''
        buf = ""
        count = 0

        while line:
            c = line[0]
            buf += c

            if c == dopen:
                count += 1

            elif c == dclose:
                count -= 1

                if count == 0:
                    return buf, line[1:]

            line = line[1:]

        return buf, line.lstrip()

    def __init__(self, stack=None, funcs=None):
        '''
        Initialize the stack and define a bunch of regular expressions

        :param stack: an initial stack (default: [])
        :type stack: list
        :param funcs: an initial collection of user-defined functions (default: {})
        :type funcs: dictionary
        :rtype: none
        '''
        if stack is None:
            stack = []

        if funcs is None:
            funcs = {}

        self.stack       = stack
        self.funcs       = functions.Functions( funcs )
        self.parseInt    = re.compile( r'^0\((?P<base>\d+)\)(?P<value>.*)$' )
        self.parseFloat  = re.compile( r'(?P<value>[+-]?\d*\.\d+([eE][+-]?\d+)?)$' )
        self.parseDefine = re.compile( r'define\s*(?P<name>\S+)\s*{(?P<definition>[^}]*)}' )
        self.parseModule = re.compile( r'(\w+)([.]\w+)+' )
        self.parseDef    = re.compile( r'define\s+(?P<name>\S+)\s*(?P<effect>:\s*\(.*\))?\s*(?P<desc>\{\{.*\}\})?\s*{(?P<definition>[^}]*)}', re.DOTALL )
        self.findDeps    = re.compile( r'deps:\s*(\S+)' )

    def define( self, line ) :
        """If a line starts with 'define', then it's a function declaration"""
        match = self.parseDef.match( line )

        if not match:
            raise Exception, 'expect functions of the form "define name (: effect)? {{description}}? {definition}"'

        else:
            name, effect, desc, definition = match.groups()
            effect = effect if effect else ' : none'
            desc   = desc.strip( "{}" ) if desc else "  none"
            doc    = "  %s %s\n\n%s" % (name, effect, desc)

            # look for dependencies (e.g. for word abba we would have deps:abab,aba or just deps:abab as abab has deps:aba)
            mo = self.findDeps.finditer( desc )

            if mo :
                for dep in mo :
                    deps  = dep.group( 1 )
                    words = deps.split( ',' )

                    for word in words :
                        if word == '' :
                            continue

                        self.push( word )
                        self.funcs.fetch( self )

            self.funcs.setFunction( name, list(self.gobble(definition)), doc )

    def norm( self, value ) :
        '''
        Convert string representation of a number to its internal form
        Numbers MUST start with a digit
        If the value is not a number it is returned as is
        Floating point numbers MUST have a decimal point
        Integers may be of the form (where 'd' is a decimal digit, h a hex  digit)
            dddd -- decimal integer
            0xhhhh -- hex integer
            0dddd -- octal integer
            0bdddd -- binary integer
            0(z)xxxx -- integer to base z (for bases > 10, digits following 9 are a,b,c,d,...,y,z)
        '''
        if len(value) == 0 :
            return value

        if len(value) == 1 :
            if value.isdigit() :
                return int( value )

            else :
                return value

        if value[0] == '-' and value[1].isdigit():
            sign = -1
            value = value[1:]

        elif value[0] == '+' and value[1].isdigit() :
            sign = +1
            value = value[1:]

        else :
            sign = +1

        if value[0].isdigit() :
            # have a number
            if value.count(".") == 1 or value.lower().count("e") == 1 :
                # have a float
                return sign * float( value )

            else :
                # have an integer
                if value.startswith('0b') :
                    return sign * int( value, 2 )

                elif value.startswith('0x') or value.startswith('0X') :
                    return sign * int( value, 16 )

                elif value.startswith("0(") :
                    mo = self.parseInt.match( value )

                    if mo :
                        return sign * int( mo.group('value'), int(mo.group('base')) )

                    else :
                        return value

                elif value.startswith('0') :
                    return sign * int( value, 8 )

                else :
                    return sign * int( value, 10 )

        else :
            # have something else
            return value

    def gobble( self, expr ) :
        """Return the given expression a token at a time allowing for string
        quoting and anonymous functions"""

        instring    = False
        stringConst = False
        buff        = ''

        while expr :
            char = expr[0]

            if not instring and char in "\t\r\n" :
                expr = expr[1:]
                continue

            if char == '[' and not (instring or stringConst) :
                function, expr = self._collectFunction( expr )
                yield list( self.gobble(function[1:-1]) )

            elif char == '"':
                if instring:
                    if len(buff) == 0 :
                        yield ""    # empty string
                        buff = ''
                        instring = False

                    elif buff[-1] == "\\" :
                        buff += char

                    else :
                        yield '"' + buff + '"'  # flag it as a string with quotation marks
                        buff = ''
                        instring = False

                else:
                    instring = True

            elif char == "'" :  # special string quote: '<string to space>
                stringConst = True

            elif char == ' ' :
                if instring:
                    # Quoted strings can contain spaces.
                    buff += char

                elif stringConst :
                    yield '"' + buff + '"'  # flag it as a string with quotation marks
                    buff = ''
                    stringConst = False

                elif buff.strip():
                    # Given character may be a number.
                    yield self.norm( buff )
                    buff = ''

            elif instring or stringConst or char not in ' []' :
                buff += char

            if len(expr) > 1 :
                expr = expr[1:]

            else :
                expr = None

        if buff :
            if stringConst :
                yield '"' + buff + '"'  # flag it as a string with quotation marks

            else :
                yield self.norm( buff )

    def eval(self, expression):
        """Evaluate the given expression. This is the workhorse."""

        if _flags['pdb']:
            pdb.set_trace()
            toggle_pdb()

        # What have we been given?
        if type(expression) == StringType :
            if expression.strip().startswith( 'define ' ) :
                self.define( expression )
                return self.stack

            # Not a 'define' but a string containing instructions
            atoms = self.gobble( expression )

        elif type(expression) in [FunctionType, LambdaType] :
            # have something that requires immediate execution
            expression()
            return self.stack

        else :
            # A list of instructions - internally a function.
            atoms = expression

        getFunction = self.funcs.getFunction

        for atom in atoms :
            if _flags['trace']:
                if not self.stack:
                    state = '_empty_'

                else:
                    state = ' '.join(map(repr, self.stack))

                print 'stack: %s' % state
                print "atom:", atom

            # check for quoted string
            if type( atom ) == StringType and atom.startswith( '"' ) :
                self.push(atom.strip('"'))
                continue

            # Try to get the atom as a named function first.
            try :
                defined, func = getFunction( atom )

            except Exception, msg:
                raise Exception, "eval: Error fetching %s (%s)" % (atom, msg)

            if defined :
                if callable( func ) :
                    # It's a function i.e. built in.
                    func( self )

                else :
                    # Otherwise it's a pre-defined list.
                    self.eval( func )

            else :
                # check for special module.function call, instance.method call, or user variable
                if type(atom) == StringType :
                    # check for <module name>.<function name> or <instance name>.<method name>
                    mo = self.parseModule.match( atom )

                    if mo :
                        # look for a user-created instance
                        search = [self.funcs.userNS] + self.funcs.NSdict[self.funcs.userNS]['__links__']

                        for ns in search :
                            is_inst = mo.group( 1 ) in self.funcs.NSdict[ns]['__inst__']

                            if is_inst :
                                break

                        if is_inst :
                            is_callable = eval( "callable(%s)" % atom, self.funcs.NSdict[ns]['__inst__'] )

                        else :
                            is_callable = eval( "callable(%s)" % atom, sys.modules )

                        # do we have an executable?
                        if is_callable :
                            # a callable w/ or w/o arguments
                            # functions taking no arguments should use the 'nil' word to signal this fact
                            if self.length() == 0 :
                                args = []

                            else :
                                args = self.pop()

                            if isinstance(args, basestring) and args.startswith("["):  # pylint: disable=E1103
                                args = eval(args)

                            if type(args) in [ListType, TupleType] :
                                # arguments are taken left-to-right (do arg.reverse() otherwise)
                                arg = str( tuple(args) )

                            else :
                                # insert single argument into a tuple
                                arg = str( (args,) )

                            # evaluate the module-based function
                            cmd = "%s%s" % (atom, arg)

                        # not a callable
                        else :
                            cmd = atom

                        if is_inst :
                            self.push( eval(cmd, globals(), self.funcs.NSdict[ns]['__inst__']) )

                        else :
                            self.push( eval(cmd, sys.modules) )

                    # Not a module reference, check for a user variable
                    else :
                        defined, val = self.funcs.getVar( atom )

                        if defined :
                            self.push( val )

                        else :
                            self.push( atom )

                # not a string, push the value onto the stack
                else :
                    self.push( atom )

        return self.stack

    def eval2( self, f1, f2 ) :
        '''Evaluates f1() and then f2() -- needed by 'compose'
        '''
        self.eval( f1 )
        return self.eval( f2 )

    def output(self, msg, color=None):
        print colored(msg, color)

    # Functions for manipulating the stack.

    def push( self, value, multi=False ) :
        '''
        Push one or more objects onto the stack
        :param: the value(s) to be pushed onto the stack
        :type value: an object or a tuple of objects
        :param multi: signals whether the value is a tuple (True) or not (False)
        :type multi: boolean (default: False)
        :rtype: none
        '''
        if multi :
            self.stack += list( value )

        elif value != None :
            self.stack.append( value )

    def pop( self ) :
        '''Removes and returns the top item on the stack'''
        try :
            return self.stack.pop()

        except :
            raise IndexError, "pop: popping an empty stack (too few parameters on stack?)"

    def peek( self ) :
        '''Returns the top item on the stack without removing it'''
        try :
            return self.stack[-1]

        except :
            raise IndexError, "peek: stack is empty (too few parameters on stack?)"

    def peekn( self, n ) :
        '''
        Return a copy of the stack element n-th (n >= 0) from the top.
        Note peekn(0) == peek()
        :param n: the depth index (0 == top, 1 == top[-1], ...)
        :type n: integer
        :rtype: an object
        '''
        try :
            n = -1 - n
            return self.stack[n]

        except :
            raise IndexError, "peekn: Too few items on stack"

    def pop2( self ) :
        '''returns the top two items on the stack'''
        try :
            return self.stack.pop(), self.stack.pop()

        except :
            raise IndexError, "pop2: Too few items on stack"

    def popn(self, n):
        '''
        Returns the top n objects on the stack as a list
        :param n: the number of objects to return (popn(1) == pop())
        :type n: integer
        :rtype: list
        '''
        if n == 0:
            return []

        try:
            return [self.stack.pop() for i in range(n)]
        except:
            raise IndexError("popn(%d): Too few items on stack" % n)

    def popall( self ) :
        '''Returns all of the elements of a stack as a list'''
        all = self.stack
        all.reverse()
        self.stack = []
        return all

    def clear(self) :
        '''clears the stack of all elements'''
        self.stack = []

    def length(self) :
        '''Returns the depth of the stack (i.e. number of elements in it)'''
        return len(self.stack)

    def clearTo( self, n ) :
        '''
        Clears the stack to a specified depth
        :param n: the number of earlier elements to retain
        :type n: integer
        :rtype: none
        '''
        sl = len(self.stack)

        if sl <= n:
            return

        else:
            self.popn(sl - n)

    def __str__(self):
        """Return a string representation of the stack"""
        if not self.stack:
            state = '_empty_'

        else:
            state = ' '.join([repr(i) for i in self.stack])

        return '===> %s' % state


if __name__ == '__main__':
    import traceback

    cat = Cat()

    if len(sys.argv) > 1:
        if sys.argv[1] in ('-e', '--eval'):
            cat.eval(' '.join(sys.argv[2:]))
            print cat

    else:
        print
        print colored("#words prints a list of built-in Cat words (functions)", 'green')
        print colored("'wordName #doc prints documentation for wordName", 'green')
        print colored("'wordName #def prints the definition of wordName", 'green')
        print colored("A 'naked' CR terminates interactive session as does the word 'quit'", 'green')
        print colored("The word 'runtests' runs some test code", 'green')
        print

        showStack = True
        fullErrorInfo = False

        while True:
            cat.eval("global:prompt")
            try:
                line = raw_input(cat.pop())
            except EOFError:
                # CTRL+D
                break

            if line == "":
                break

            elif line == 'quit':
                break

            elif line.lower().startswith("showstack"):
                showStack = line.lower().endswith(('on', 'true', 'yes'))

                if showStack:
                    print colored(str(cat), 'blue')

            elif line.lower().startswith("fullerrorinfo"):
                fullErrorInfo = line.lower().endswith(('on', 'true', 'yes'))

            elif line.lower() == 'runtests':
                lang_tests.runtests(cat)

            else:
                try:
                    cat.eval(line.strip())

                    if showStack:
                        print colored(str(cat), 'blue')

                except Exception, msg:
                    raise
                    print colored(msg, 'red')

                    if fullErrorInfo:
                        for frame in traceback.extract_tb(sys.exc_info()[2]):
                            _, lineno, fn, _ = frame
                            print colored("Error in %s on line %d" % (fn, lineno), 'red')

                    print colored(str(cat), 'blue')
