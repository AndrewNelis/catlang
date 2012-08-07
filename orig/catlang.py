#!/usr/bin/python
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

import sys, re, readline, math, platform
from types import *

# set up to handle colored text to console
try :
    from termcolor import colored

except :
    def colored( text, color ) :
        return text

if platform.system().lower() == 'windows' :
    try :
        import colorama
        colorama.init()
        
    except :
        pass

# debugging switches
traceFlag = False


class Functions :
    """Return a function for a given symbol. Also maintains
    a list of user defined functions."""
    def __init__( self, userfunctions={} ) :
        """Constructor"""
        # Initial map of symbols to functions
        # (as well as the methods defined on this class)
        self.targetNS  = ''
        self.userNS    = 'user'
        self.NSdict    = { 'std' :
                                    {
                                    '+'         : 'add',
                                    '-'         : 'sub',
                                    '*'         : 'mul',
                                    '/'         : 'div',
                                    '='         : 'eq',
                                    '!='        : 'neq',
                                    '<'         : 'lt',
                                    '>'         : 'gt',
                                    '<='        : 'lteq',
                                    '>='        : 'gteq',
                                    'if'        : '_if',
                                    '%'         : 'mod',
                                    '%/'        : '_divmod',
                                    '/%'        : '_divmod',
                                    '**'        : 'pwr',
                                    '+rot'      : '_rotUp',
                                    '-rot'      : '_rotDown',
                                    '++'        : 'inc',
                                    '--'        : 'dec',
                                    '~'         : '_not',
                                    '!'         : '_saveVar',
                                    '@'         : '_fetchVar',
                                    '>>'        : '_rightShift',
                                    '<<'        : '_leftShift',
                                    '&'         : 'bit_and',
                                    '|'         : 'bit_or',
                                    '~'         : 'bit_not',
                                    'and'       : '_and',
                                    'del'       : '_del_word',
                                    'divmod'    : '_divmod',
                                    'float'     : '_float',
                                    'int'       : '_int',
                                    'list'      : '_list',
                                    'not'       : '_not',
                                    'or'        : '_or',
                                    'str_cat'   : 'add', # Go python!
                                    'type'      : 'typeof',
                                    'while'     : '_while',
                                    'cd'        : 'focusNS',
                                    'ls'        : '_udf',
                                    'rm'        : '_del_word',
                                    'ln'        : 'linkToNS',
                                    'pwd'       : 'showUserNS',
                                    '#allDefs'  : '_loadAllDefs',
                                    '#allWords' : '_showAllWords',
                                    '#def'      : '_dumpdef',
                                    '#dir'      : '_dir',
                                    '#doc'      : '_show',
                                    '#dump'     : '_dumpStack',
                                    '#help'     : '_help',
                                    '#import'   : '_import',
                                    '#info'     : '_info',
                                    '#instance' : '_instance',
                                    '#listFiles': '_listDefinitionFiles',
                                    '#load'     : '_load',
                                    '#pdb'      : '_pdb',
                                    '#prompt'   : '_newPrompt',
                                    '#reload'   : '_reload',
                                    '#trace'    : '_trace',
                                    '#types'    : '_type',
                                    '#udf'      : '_udf',
                                    '#vars'     : '_showVars',
                                    '#whereis'  : '_whereis',
                                    '#words'    : '_words',
                                    
                                    '__globals__' : { 'CatDefs' : 'CatDefs/', 'prompt' : 'Cat> ' },
                                    },
                           'user' : { '__vars__' : { }, '__links__' : [ ], '__inst__' : { }, '__loadList__' : [ ] },
                         }
        
        self.NSdict['user'].update( userfunctions )
        self.parseDef = re.compile( r'define\s+(\S+)\s*(:\s*\(.*\))?\s*(\{\{.*\}\})?\s*(\{.*\})', re.DOTALL )
    
    def getFunction( self, what ):
        """Called by the interpreter to get a function named <what>.
        As a name may be None we return a flag stating whether <what>
        was defined, followed by it's definition.
        """
        if type(what) != StringType :
            return False, None
        
        # check 'std' namespace first then built-ins
        if what in self.NSdict['std'] :
            # A method alias.
            return True, getattr( self, self.NSdict['std'][what]  )
        
        elif hasattr( self, what ) :
            # A named method (a built-in).
            return True, getattr( self, what )
        
        else :
            # search name spaces: 'user' then linked namespaces
            search = [self.userNS] + self.NSdict[self.userNS]['__links__']
            
            if '__vars__' in search :
                search.remove('__vars__')
                search.remove('__links__')
                search.remove('__inst__')
                search.remove('__loadList__')
            
            for ns in search :
                if what in self.NSdict[ns] :
                    return True, self.NSdict[ns][what][0]

        return False, None
    
    def setFunction( self, name, definition, descrip='', ns='' ) :
        """Called to *define* new functions"""
        if ns == '' :
            ns = self.userNS
        
        self.NSdict[ns][name] = [definition, descrip]
    
    def isFunction( self, what ) :
        '''
        Returns True if the argument is defined as a function in
        some user-related namespace; False otherwise
        '''
        if hasattr( self, what ) :
            return True, 'std'
        
        search = ['std', self.userNS] + self.NSdict[self.userNS]['__links__']
        search = reduce(lambda x, y: x if y in x else x + [y], search, [])
        
        if '__vars__' in search :
            search.remove('__vars__')
            search.remove('__links__')
            search.remove('__inst__')
            search.remove('__loadList__')
        
        for ns in search :
            if what in self.NSdict[ns] :
                return True, ns
        
        return False, None
    
    def isInstance( self, what ) :
        '''Returns True and the namespace if the argument is an instance in the namespace
        :param what: object in question
        :type what: object
        :rtype: boolean, string:namespace
        '''
        search = [self.userNS] + self.NSdict[self.userNS]['__links__']
        
        for ns in search :
            if what in self.NSdict[ns]['__inst__'] :
                return True, ns
        
        return False, None
    
    def getVar( self, what ) :
        '''
        returns the value associated with user variable named in what from the user's '__var__' dict
        Note that 'what' may be of the form:
            <simple name>
            <namespace>:<simple name>
                <namespace> may also be the special case 'global' to access global variables
        '''
        if what.count(":") == 1 :
            ns, var = what.split( ":" )
            
            if ns.lower() == 'global' :
                if var in self.NSdict['std']['__globals__'] :
                    return True, self.NSdict['std']['__globals__'][var]
                
                else :
                    return False, None
            
            else :
                if ns in self.NSdict and var in self.NSdict[ns]['__vars__'] :
                    return True, self.NSdict[ns]['__vars__'][var]
                
                else :
                    return False, None
        
        else :
            search = [self.userNS] + self.NSdict[self.userNS]['__links__']
            
            for ns in search :
                if what in self.NSdict[ns]['__vars__'] :
                    return True, self.NSdict[ns]['__vars__'][what]
            
            if what in self.NSdict['std']['__globals__'] :
                return True, self.NSdict['std']['__globals__'][what]
            
            else :
                return False, None
    
    def setVar( self, var, val ) :
        '''
        stores val into the __vars__ dictionary in some namespace under key name var
        
        var may take the form:
            <simple name>
            <namespace>:<simple name>
            Note that the namespace 'global' is reserved for saving global variables
        '''
        if var.count(":") == 1 :
            ns, var = var.split( ":" )
            
            if ns.lower == 'global' :
                self.NSdict['std']['__globals__'][var] = val
            
            else :
                self.NSdict[ns]['__vars__'][var] = val
        
        else :
            self.NSdict[self.userNS]['__vars__'][var] = val
    
    def _formatList( self, theList, across=5 ) :
        '''Formats the list
        :param theList: the list to be formatted for printing
        :type theList: a list
        :param across: the number of list items to be printed across
        :type across: integer
        :rtype: string (with coloration)
        '''
        txt = ""
        
        if len(theList) == 0 :
            return "  _none_\n"
        
        theList = [str(x) for x in theList]
        longest = max( [len(x) for x in theList] )
        i       = 0
           
        for item in theList :
            l        = longest + 2 - len( item )
            fragment = "  " + item + " " * l
            txt     += fragment
            i       += 1
            
            if i == across :
                txt += "\n"
                i    = 0
        
        if i > 0 :
            txt += "\n"
        
        return txt
    
    def _printList( self, theList, across=5 ) :
        '''Print the elements in theList'''
        print colored( self._formatList(theList, across), 'green' )
    
    def _dumpList( self, theList, indent=0 ) :
        '''Dump a list'''
        if type(theList) not in [ListType, TupleType] :
            theList = [ theList ]
        
        txt = ""
        
        for item in theList :
#             if type(item) in [ListType, TupleType] :
#                 indent += 1
#                 txt += self._dumpList( item, indent )
#                 txt += "---" * indent + "\n"
#                 indent -= 1
#             
#             else :
#                 txt += "   " * indent + str(item) + "\n"
            txt += str(item) + "\n"
        
        return txt

    # Methods defining functions with invalid python names.
    # They're prefixed with underscores so people don't unintentionally
    # re-define them and so we can identify these when 'defs' is called
  
    def _if( self, stack ) :
        '''
        if : (func:true_func func:false_func bool:condition -> any|none)
        
        desc:
            executes one predicate or another whether the condition is true
        
        tags:
            level0,control
        '''
        ffalse, ftrue, truth = stack.popn(3)
        
        if truth:
            stack.push( ftrue )
        
        else:
            stack.push( ffalse )
        
        self.eval( stack )
    
    def _dumpStack( self, stack ) :
        '''
        #dump : (-- -> --)
        
        desc:
            non-destructively dumps the entire contents of the stack to the console
        
        tags:
            custom,console,stack
        '''
        print colored( str(stack), 'green' )
    
    def _show( self, stack ) :
        '''
        #doc : (string:func_name -> --)
        
        desc:
            displays documentation for function whose name string is on top of the stack
            A word name may be prefixed with a namespace. E.g. 'shuffle:abba #doc
        
        tags:
            custom,definitions,methods
        '''
        name = stack.pop().strip( '"' )
        
        if name.count(":") == 1 :
            ns, name = name.split(":")
            
            if name in self.NSdict[ns] :
                obj = self.NSdict[ns][name]
                print colored( obj[1], 'green' )
                return
            
            else :
                raise ValueError, "#doc: No documentation for '%s' in '%s'" % (name, ns)
        
        if name in ['__vars__', '__links__', '__inst__', '__loadList__'] :
            return
        
        if name in self.NSdict['std'] :
            # get method's doc string
            fcn = getattr( self, self.NSdict['std'][name] )
            print colored( fcn.__doc__, 'green' )
        
        elif hasattr( self, name ) :
            fcn = getattr( self, name )
            print colored( fcn.__doc__, 'green' )
        
        else :
            search = [self.userNS] + self.NSdict[self.userNS]['__links__']
            
            for ns in search :
                if name in self.NSdict[ns] :
                    obj = self.NSdict[ns][name]
                    print colored( obj[1], 'green' )
                    return
            
            print colored( "No description for " + name, 'red' )
    
    def _load( self, stack, force=False, ns='' ) :
        '''
        #load : ( string:fileName -> --)
        
        desc:
            Loads the script whose name string is on top of the stack into a namespace
        
        tags:
            level0,control,system
        '''
        def stripComments( text ) :
            temp = text.strip()
            
            if temp == "" or temp.startswith('//') or temp.startswith('#') :
                return ""
            
            ix = temp.rfind( '//' )
            
            if ix > 0 :
                temp = temp[:ix]
            
            return temp
        
        fileName = stack.pop()
        
        if type(fileName) != StringType :
            raise Exception, "#load: File name must be a string"
        
        # check for a predefined target namespace
        if ns == '' :
            tgtNS = self.userNS  # no predefined namespace => use default
        
        else :
            tgtNS = ns   # use predefined namespace
        
        if not force :
            if fileName in self.NSdict[tgtNS]['__loadList__'] :
                raise Warning, "#load: The file of Cat definitions called '%s' has already been loaded. Skipping it." % fileName
        
        fd     = open( fileName, 'r' )
        buffer = ""
        lineNo = 0
        inDef  = False
        
        for line in fd :
            lineNo += 1
            temp    = stripComments( line.strip() )
            
            if temp == "" :
                continue
            
            if not inDef :
                if not temp.startswith( "define" ) :
                    stack.eval( temp )
                    
                    # the evaluation of temp may have changed the user's initial namespace
                    # if ns arg is '' then there is no predefined namespace
                    if ns == '' :
                        tgtNS = self.userNS
                    
                    continue
                
                else :
                    inDef = True
            
            # must be in a definition (this hack permits 1-line definitions)
            if inDef :
                # consolidate lines of a definition into a single string
                buffer += line  # to preserve original formatting
                
                # end of function definition?
                if not temp.endswith( "}}" ) and temp.endswith( "}" ) : 
                    # parse parts of the string
                    mo = self.parseDef.match(buffer)
                    
                    if not mo :
                        raise ValueError, "#load: Bad definition in file %s at line %d" % (fileName, lineNo)
                    
                    # create definition
                    descrip = mo.group(3).strip("{}") if mo.group(3) else ''
                    effect  = mo.group(2).strip(" :") if mo.group(2) else ''
                    lines   = mo.group(4).strip("{}").split("\n")
                    buf     = ""
                    
                    # remove all comments from the definition
                    for temp in lines :
                        temp = stripComments( temp )
                        
                        if temp != "" :
                            buf += temp + " "
                    
                    self.setFunction( mo.group(1), list(stack.gobble(buf)), "  %s : %s\n%s" % (mo.group(1), effect, descrip), tgtNS )
                    buffer = ""
                    inDef  = False
        
        self.NSdict[tgtNS]['__loadList__'].append( fileName )
        fd.close()
    
    def _reload( self, stack ) :
        '''
        #reload : ( string:fileName -> --)
        
        desc:
            Reloads the script whose name string is on top of the stack
        
        tags:
            level0,control,system
        '''
        self._load( stack, True )
    
    def _loadAllDefs( self, stack ) :
        '''
        #allDefs : (-- -> --)
        
        desc:
            load all definitions into their corresponding namespaces
        
        tags:
            custom,namespaces,definitions
        '''
        loadFile = self.NSdict['std']['__globals__']['CatDefs'] + "everything.cat"
        stack.push( loadFile )
        self._load( stack )
    
    def _rotUp( self, stack ) :
        '''
        +rot : (any:a any:b any:c -> any:c any:a any:b)
        
        desc:
            rotates the top three elements upward one position circularly
        
        tags:
            level0,stack
        '''
        if stack.length() < 3 :
            raise Exception, "+rot: Expect at least three elements on the stack"
        
        t, m, b = stack.popn( 3 )
        stack.push( (t, b, m), multi=True )
    
    def _rotDown( self, stack ) :
        '''
        -rot : (any:a any:b any:c -> any:b any:c any:a)
        
        desc:
            rotates the top three elements downward one position circularly
        
        tags:
            level0,stack
        '''
        if stack.length() < 3 :
            raise Exception, "-rot: Expect at least three elements on the stack"
        
        t, m, b = stack.popn( 3 )
        stack.push( (m, t, b), multi=True )
    
    def _not( self, stack ) :
        '''
        not : (bool -> bool)
        
        desc:
            returns True if the top value on the stack is False and vice versa
        
        tags:
            level0,boolean
        '''
        stack.stack[-1] = not stack.stack[-1]
    
    def _while( self, stack ) :
        '''
        while : (func func:test -> any|none)
        
        desc:
            executes a block of code (function) repeatedly until the condition returns false
            Example: func test while
        
        tags:
            level1,control
        '''
        b, f = stack.pop2()
        
        while (stack.eval(b), stack.pop())[1] :
            stack.eval( f )
    
    def _list( self, stack ) :
        '''
        list : ([...] -> list)
        
        desc:
            creates a list from a function
        
        tags:
            level0,lists
        '''
        func        = stack.pop()
        old         = stack.stack
        stack.stack = []
        stack.eval( func )
        lst         = stack.stack
        stack.stack = old
        stack.push( lst )
    
    def _type( self, stack ) :
        '''
        #types : ( -> list)
        
        desc:
            prints a list of types represented by elements on the stack
            in the same order as the element on the stack with the deepest
            item first and the top item last
        
        tags:
            custom,types,stack 
        '''
        typeList = []
        
        for item in stack.stack :
            typeList.append( type(item) )
        
        print colored( str(typeList), 'green' )
    
    def _int( self, stack ) :
        '''
        int : (obj -> int)
        
        desc:
            casts the object on top of the stack to an integer
        
        tags:
            level1,math,conversion
        '''
        stack.stack[-1] = int( stack.stack[-1] )
    
    def _float( self, stack ) :
        '''
        float : (obj -> float)
        
        desc:
            casts the object on top of the stack to as floating point number
        
        tags:
            level1,math,conversion
        '''
        stack.stack[-1] = float( stack.stack[-1] )
    
    def _pdb( self, stack ) :
        '''
        #pdb : (-- -> --)
        
        desc:
            enters pdb
        
        tags:
            custom,system,debugging
        '''
        import pdb
        
        pdb.set_trace()
    
    def _dumpdef( self, stack ) :
        '''
        #def : (string:name -> --)
        
        desc:
            prints the definition string of the named function to the console
            the function name may be prefixed with a <namespace>: if desired
            Example: 'shuffle:abba #def
        
        tags:
            custom,console,debugging
        '''
        atom = stack.pop().strip( '"' )
        
        if atom.count(":") == 1 :
            ns, name = name.split(":")
            obj = self.NSdict[ns][name]
            print colored( obj[0], 'green' )
            return
        
        if hasattr(self, atom) :
            print colored( "Function %s is a primitive" % atom, 'green' )
        
        else :
            defined, func = self.getFunction( atom )
        
            if defined :
                print colored( "%s: %s" % (atom, func), 'green' )
            
            else :
                print colored( "Function %s is undefined" % atom, 'red' )
    
    def _and( self, stack ) :
        '''
        and : (bool bool -> bool)
        
        desc:
            returns True if both of the top two values on the stack are True
        
        tags:
            level0,boolean
        '''
        a, b = stack.pop2()
        stack.push( a and b )
    
    def _or( self, stack ) :
        '''
        or : (bool bool -> bool)
        
        "desc:
            returns True if either of the top two values on the stack are True
        
        tags:
            level0,boolean
        '''
        a, b = stack.pop2()
        stack.push( a or b )
    
    def _import( self, stack ) :
        '''
        #import : (string:module_name -> --)
        
        desc:
            imports the named module for use by the program
            Note: members of the module are accessed  with this notation: <module name>.<member name>
                  parameters must precede the function call as a list with arguments in the order
                  required by the function. E.g. ([base expt] list math.pow -> base^expt)
            Example: 'math #import
                     'os #import
                     'localModule #import
        
        tags:
            custom,module,import 
        '''
        what = stack.pop()
        
        if type(what) == StringType :
            sys.modules[what] = __import__( what )
        
        else :
            raise Exception, "#import The module name must be a string"
    
    def _instance( self, stack ) :
        '''
        #instance (string:name list:args|any:arg|nil string:module.class -> --)
        
        desc:
            creates an instance of a specified class
            instance is invoked in the usual way: <instance>.<method>
            Example: 'Meeus #import
                     'm nil 'Meeus.Meeus #instance
                      Use:  [2012,7,4] m.JD
        
        tags:
            custom,instance
        '''
        cls, args, name = stack.popn( 3 )
        
        if type(cls) != StringType :
            raise ValueError, "#instance: The module.class name must be a string"
        
        if type(name) != StringType :
            raise ValueError, "#instance: The instance name must be a string"
        
        if type(args) == StringType and args.startswith("[") :
            args = eval( args )
        
        if type(args) in [ListType, TupleType] :
            args = str( tuple(args) )
        
        else :
            args = str( (args,) )
        
        self.NSdict[self.userNS]['__inst__'][name] = eval( "%s%s" % (cls, args), sys.modules )
    
    def _info( self, stack ) :
        '''
        #info : (-- -> --)
        
        desc:
            lists modules available for use and other bits of useful information
            for the default user namespace.
        
        tags:
            custom,modules
        '''
        keys = sys.modules.keys()
        keys.sort()
        print colored( "**sys.modules:", 'green' )
        print colored( self._formatList( keys), 'green' )
        keys = self.NSdict[self.userNS].keys()
        keys.remove('__vars__')
        keys.remove('__links__')
        keys.remove('__inst__')
        keys.remove('__loadList__')
        keys.sort()
        print colored( "**words defined in '%s':" % self.userNS , 'green' )
        print colored( self._formatList(keys), 'green' )
        keys = self.NSdict[self.userNS]['__inst__'].keys()
        keys.remove( '__builtins__' )
        keys.sort()
        print colored( "**instances defined in '%s':" % self.userNS , 'green' )
        print colored( self._formatList(keys), 'green' )
        keys = self.NSdict[self.userNS]['__vars__'].keys()
        keys.sort()
        print colored( "**user-defined variables in '%s':" % self.userNS, 'green' )
        print colored( self._formatList(keys), 'green' )
        keys = self.NSdict[self.userNS]['__loadList__']
        keys.sort()
        print colored( "**files loaded into '%s':" % self.userNS, 'green' )
        print colored( self._formatList(keys), 'green' )
        keys = self.NSdict[self.userNS]['__links__']
        keys.sort()
        print colored( "**namespaces linked to '%s':" % self.userNS, 'green' )
        print colored( self._formatList(keys), 'green' )
    
    def _saveVar( self, stack ) :
        '''
        ! : (any string:userVarName -> )
        
        desc:
            saves the value at [-1] to the user symbol table
            with the name provided by the string at [0]
        
        tags:
            custom,variables,user
        '''
        varName, value = stack.pop2()
        defined, where = self.isFunction( varName )
        
        if defined :
            stack.push( value )
            raise ValueError, "!: User variable '%s' duplicates an existing word in '%s'" % (varName, where)
        
        self.setVar( varName, value )
    
    def _fetchVar( self, stack ) :
        '''
        @ : (string:userVarName -> val)
        
        desc:
            pushes the value of the named user-variable onto the stack
            Note: the userVarName by itself (no quotes or @) will push its value onto the stack
        
        tags:
            custom,variables,user
        '''
        name         = stack.pop()
        defined, val = self.getVar( name )
        
        if defined :
            stack.push( val )
        
        else :
            raise KeyError, "@: No variable called " + name
    
    def _showVars( self, stack ) :
        '''
        #vars : (-- -> --)
        
        desc:
            lists names of variables in the user and global symbol tables
            
        tags:
            custom,user_variables
        '''
        # variables in the default user namespace and in 'globals'
        keys = self.NSdict[self.userNS]['__vars__'].keys()
        keys.sort()
        print colored( "User-defined variables in default namespace '%s':" % self.userNS, 'green' )
        self._printList( keys )
        keys = self.NSdict['std']['__globals__'].keys()
        keys.sort()
        print colored( "Variables defined in 'globals':", 'green' )
        self._printList( keys )
        search = self.NSdict[self.userNS]['__links__']
        
        # search for variables in linked-in namespaces
        for ns in search :
            keys = self.NSdict[ns]['__vars__'].keys()
            keys.sort()
            print colored( "User-defined variables in namespace '%s':" % ns, 'green' )
            self._printList( keys )
    
    def _dir( self, stack ) :
        '''
        #dir : ( string -> --)
        
        desc:
            displays the results of applying the Python 'dir' function
            to the argument on top of the stack. Used to examine the content
            of sys.modules.
        
        tags:
            custom,python,dir
        '''

        if stack.length() == 0 :
            arg = ''
        
        else :
            arg = str( stack.pop() )
        
        lst = eval("dir(eval('%s'))" % arg, sys.modules )
        self._printList( lst, 4 )

    def _words( self, stack, showAll=False ) :
        '''
        words: ( -- -> -- )
        
        desc:
            Prints a list of available words to the user's terminal
        
        tags:
            level2,words
        '''        
        print colored( "Built-in (primitive) words:", 'green' )
        
        functions = self.NSdict['std'].keys()
        
        for method in dir(self) :
            if method not in functions and not method.startswith('_') :
                functions.append( method )
        
        functions.remove( 'setFunction' )
        functions.remove( 'getFunction' )
        functions.remove( 'isFunction' )
        functions.remove( 'isInstance' )
        functions.remove( 'setVar' )
        functions.remove( 'getVar' )
        functions.remove( 'parseDef' )
        functions.remove( 'userNS' )
        functions.remove( 'NSdict' )
        functions.sort()
        self._printList( functions )
        
        if not showAll :
            search = [self.userNS] + self.NSdict[self.userNS]['__links__']
        
        else :
            search = self.NSdict.keys()
            search.remove( 'std' )
        
        search.sort()
        
        for ns in search :
            print
            print colored( "Words defined in '%s' namespace:" % ns, 'green' )
            functions = self.NSdict[ns].keys()
            functions.sort()
            
            if '__vars__' in functions :
                functions.remove( '__vars__' )
                functions.remove( '__links__' )
                functions.remove( '__inst__' )
                functions.remove('__loadList__')
            
            self._printList( functions )
        
        print
    
    def _showAllWords( self, stack ) :
        '''
        #allWords : (-- -> --)
        
        desc:
            Shows all defined words in all namespaces
        
        tags:
            custom,namespaces,words,functions
        '''
        self._words( stack, True )
    
    def _trace( self, stack ) :
        '''
        #trace: (-- -> --)
        
        desc:
            toggles the global traceing flag to enable simple tracing of function
            execution.
        
        tags:
            custom,debugging
        '''
        global traceFlag
        
        traceFlag = not traceFlag
    
    def _rightShift( self, stack ) :
        '''
        >> : (int:base int:n -> int)
        
        descr:
            performs a right shift of n bits on a base integer
        
        tags:
            level0,math
        '''
        n, val = stack.pop2()
        stack.push( int(val) >> n )
    
    def _leftShift( self, stack ) :
        """'
        << : (int:base int:n -> int)
        
        descr:
            performs a left shift of n bits on a base integer
        
        tags:
            level0,math
        """
        n, val = stack.pop2()
        stack.push( int(val) << n )
    
    def _udf( self, stack ) :
        '''
        Shows all user-defined functions
        '''
        keys = self.NSdict[self.userNS].keys()
        keys.sort()
        keys.remove( '__vars__' )
        keys.remove( '__links__' )
        keys.remove( '__inst__' )
        keys.remove( '__loadList__' )
        self._printList( keys )
        print
    
    def _del_word( self, stack ) :
        '''
        del : (string:name -> --)
        
        desc:
            deletes the definition of the word from the current user namespace
            Note: the name may be of the form: word1,word2,...  (e.g. 'test,junk,smmpt)
                  of a list  (e.g. ['test 'junk 'smmpt] list
            Words may have the form: <namespace>:<word>
        
        tags:
            level2,words
        '''
        top = stack.pop()
        
        if type(top) == StringType :
            words = [x for x in top.split(",") if x != '']
        
        elif type(top) in [ListType, TupleType] :
            words = top
        
        else :
            raise ValueError, "del_word: expect a string or list"
        
        for word in words :
            if word in ['__vars__', '__links__', '__inst__', '__loadList__'] :
                continue
            
            elif word.count( ":" ) == 1 :
                ns, wrd = word.split( ":" )
                
                if wrd in ['__vars__', '__links__', '__inst__', '__loadList__'] :
                    continue
                
                if ns == 'std' :
                    continue
                
                if ns in self.NSdict and wrd in self.NSdict[ns] :
                    del self.NSdict[ns][word]
            
            elif word in self.NSdict[self.userNS] :
                del self.NSdict[self.userNS][word]
    
    def _divmod( self, stack ) :
        '''
        divmod : (nbr nbr -> nbr nbr)
        /%     : (nbr nbr -> nbr nbr)
        
        desc:
            applies divmod function to top two members on stack. Number on top
            is the modulus. Returns quotient, remainder on stack (remainder on top).
            
        tags:
            level0,mathematics
        '''
        a, b = stack.pop2()
        stack.push( divmod(b, a), multi=True )
    
    def _listDefinitionFiles( self, stack) :
        '''
        #listFiles : (string:path -> --)
        
        desc:
            lists the contents of all of the definition files in the
            directory indicated by the path (string) on top of the stack
        
        tags:
            extension,definitions
        '''
        from glob import iglob
        
        path = stack.pop()
        
        if type(path) != StringType :
            raise ValueError, "#listFiles: Directory path must be a string"
        
        fnmap = { }
        path += "*.cat"
        regex = re.compile( r'^\s*define\s+(\S+)' )
        
        for file in iglob( path ) :
            fd = open( file, 'r' )
            
            for line in fd :
                mo = regex.match( line )
                
                if mo :
                    funcName = mo.group(1)
                    
                    if funcName in fnmap :
                        print colored( "File %s duplicates function %s" % (file, funcName), 'red' )
                    
                    else :
                        fnmap[funcName] = file
                
            fd.close()
        
        keys = fnmap.keys()
        keys.sort()
        maxStr = max( [len(x) for x in keys] ) + 2
        print
        
        for key in keys :
            akey = key.rjust(maxStr, " ")
            print colored( "    %s -- %s" % (akey, fnmap[key]), 'green' )
    
    def _whereis( self, stack ) :
        '''
        #whereis : (string:word -> --)
        
        desc:
            Shows where the word (a string) is to be found:
                built-in (primitive)
                in a definition file
                user defined
            E.g. 'swap #whereis
        
        tags:
            extension,search,word
        '''
        from glob import iglob
        
        theWord = stack.pop()
        source  = 'undefined'
        defined = False
        search  = self.NSdict.keys()
        
        for ns in search :
            if theWord in self.NSdict[ns] :
                if ns == 'std' :
                    source = "built-in"
                
                else :
                    source = ns
                
                defined = True
                break
        
        if not defined and hasattr( self, theWord ) :
            source = "built-in"
        
        elif not defined :
            path  = self.NSdict['std']['__globals__']['CatDefs']
            path += "*.cat"
            
            # escape characters in theWord that are interpreted by "re"
            letters = [ x for x in theWord ]
            
            for i in range(len(letters)) :
                c = letters[i]
                
                if c in ".[]{}^$*?()+-|" :  # regular expression characters
                    letters[i] = "\\" + c
            
            theWord = "".join( letters )
            
            # search the standard definition files
            regex = re.compile( r'^\s*define\s+(%s)' % theWord )
            found = False
            
            for file in iglob( path ) :
                if found :
                    break
                
                fd = open( file, 'r' )
                
                for line in fd :
                    if regex.match( line.strip() ) :
                        source = file
                        found  = True
                        break
                    
                fd.close()
            
            if not found :
                source = "undefined" % theWord
        
        print colored( "%s: %s" % (theWord, source), 'green' )
    
    def _newPrompt( self, stack ) :
        '''
        #prompt : (string:prompt -> --)
        
        desc:
            Sets the prompt string to the string on top of the stack
        
        tags:
            console
        '''
        self.NSdict['std']['__globals__']['prompt'] = str( stack.pop() )
    
    def _help( self, stack ) :
        '''
        help : (string:name -> --)
        
        desc:
            Searches user namespaces for help on 'name' (combination of #doc and #def)
            If not a built-in or user-defined word, invokes the Python help system for
            the object whose name is on top of the stack
            The 'name' may be of the form <namespace>:<name> or <name>.<name>...
        
        tags:
            console
        '''
        name = stack.pop()
        
        if type(name) != StringType :
            raise ValueError, "help: Expect a string on the stack"
        
        # check for module/instance
        n = name.count( "." )
        
        if n > 0 :
            # have a module/instance w/ function/method
            inst, method   = name.split( ".", 1 )
            defined, where = self.isInstance( inst )
            
            if defined :
                temp = eval( name, sys.modules, self.NSdict[where]['__inst__'] )
                help( temp )
                return
            
            else :
                temp = eval( name, sys.modules )
                help( temp )
                return
        
        # check for user-specified namespace and word
        if name.count(":") == 1 :
            ns, name = name.split( ":" )
            
            if name in self.NSdict[ns] :
                obj = self.NSdict[ns][name]
                print colored( obj[1], 'green' )
                print colored( obj[0], 'green' )
                return
            
            else :
                raise ValueError, "help: No help available for '%s' in '%s'" % (name, ns)
        
        # check for built-in or user-defined 
        if name in self.NSdict['std'] :
            fcn = getattr( self, self.NSdict['std'][name] )
            print colored( fcn.__doc__, 'green' )
            print colored( '\tbuilt-in', 'green' )
            return
        
        elif hasattr( self, name ) :
            fcn = getattr( self, name )
            print colored( fcn.__doc__, 'green' )
            print colored( '\tbuilt-in', 'green' )
            return
        
        # check the default and linked in namespaces
        search = [self.userNS] + self.NSdict[self.userNS]['__links__']
        
        for ns in search :
            if name in self.NSdict[ns] :
                obj = self.NSdict[ns][name]
                print colored( obj[1], 'green' )
                print colored( obj[0], 'green' )
                return
        
        # the name may be an unqualified instance or module name
        defined, where = self.isInstance( name )
        
        if defined :
            item = eval( name + ".__class__", sys.modules, self.NSdict[where]['__inst__'] )
            help( item )
        
        else :
            item = eval(name, sys.modules)
            help( item )
    
    # Now begins methods implementing functions with non-conflicting acceptable Python names
    def inc( self, stack ) :
        '''
        inc : (nbr -> nbr)
        
        desc:
            increments the number on top ofthe stack by 1
            
        tags:
            level0,mathematics
        '''
        stack.stack[-1] += 1
    
    def dec( self, stack ) :
        '''
        dec : (nbr -> nbr)
        
        desc:
            decrements the number on top ofthe stack by 1
            
        tags:
            level0,mathematics
        '''
        stack.stack[-1] -= 1
    
    def add( self, stack ) :
        '''
        add : (nbr nbr -> nbr)
        
        desc:
            adds top two numbers on the stack returning the sum on top of the stack
            Note that if instead of numbers one has other objects such as strings
            or lists, they will be concatenated.
            
        tags:
            level0,mathematics
        '''
        a, b = stack.pop2()
        stack.push( b + a )

    def sub( self, stack ) :
        '''
        sub : (nbr nbr -> nbr)
        
        desc:
            subtracts the number at [0] from that at [-1] returning
            the difference to the top of the stack.
            
        tags:
            level0,mathematics
        '''
        a, b = stack.pop2()
        stack.push( b - a )

    def mul( self, stack ) :
        '''
        mul : (nbr nbr -> nbr)
        
        desc:
            multiplies together the top two numbers on the stack. Result is placed
            on top of the stack. Note if the lower "number" is a string or a list
            it is replicated according to the standard Python rules.
            
        tags:
            level0,mathematics
        '''
        a, b = stack.pop2()
        stack.push( b * a )

    def div( self, stack ) :
        '''
        div : (nbr nbr -> nbr)
        
        desc:
            The number at [0] is divided into the number at [-1] and the
            quotient is pushed onto the stack.
            
        tags:
            level0,mathematics
        '''
        a, b = stack.pop2()
        stack.push( b / a )

    def mod( self, stack ):
        '''
        mod : (nbr nbr -> nbr)
        
        desc:
            applies modulus function to top two members on stack. Number at [0]
            is the modulus.
            
        tags:
            level0,mathematics
        '''
        a, b = stack.pop2()
        stack.push( b % a )

    def pwr( self, stack ) :
        '''
        pwr : (nbr:base nbr:expt -> nbr)
        
        desc:
            base**expt is pushed onto the stack
        
        tags:
            level0,math
        '''
        expt, base = stack.pop2()
        
        if type(base) == StringType :
            base = eval( base )
        
        if type(base) not in [IntType, LongType, FloatType] :
            raise ValueError, "pwr: The base must be a number"
        
        if type(expt) == StringType :
            expt = eval( expt )
        
        if type(expt) not in [IntType, LongType, FloatType] :
            raise ValueError, "pwr: The exponent must be a number"
        
        stack.push( base ** expt )
    
    def round( self, stack ) :
        '''
        round : (float:nbr int:dp -> float:nbr)
        
        desc:
            rounds the floating point number at [-1] to the number of
            decimal places specified by the integer at [0]
        
        tags:
            level1,mathematics
        '''
        dp, nbr = stack.pop2()
        
        if type(nbr) != FloatType :
            nbr = float( nbr )
        
        dp = int( dp )
        
        stack.push( round(nbr, dp) )
    
    def abs( self, stack ) :
        '''
        abs : (nbr -> nbr)
        
        desc:
            replaces the number on top of the stack with its absolute value
        
        tags:
            level1,mathematics
        '''
        nbr = stack.pop()
        
        if type(nbr) == StringType :
            nbr = eval( nbr )
        
        if type(nbr) in [IntType, LongType, FloatType] :
            stack.push( abs(nbr) )
        
        else :
            raise ValueError, "abs: Argument is not a number"
        
    def all( self, stack ) :
        '''
        all : (list -> bool)
        
        desc:
            returns true on top of the  stack if all of the elements of the
            list on top of the stack are true
        
        tags:
            custom,mathematics
        '''
        iter = stack.pop()
        
        if type(iter) == StringType :
            iter = eval( iter )
        
        if type(iter) in [ListType, TupleType] :
            stack.push( all(iter) )
        
        else :
            raise ValueError, "all: Argument must be an iterable"
    
    def any( self, stack ) :
        '''
        any : (list -> bool)
        
        desc:
            Returns true on top of the stack if any element of the list
            on top of the stack is true
        
        tags:
            custom,lists
        '''
        iter = stack.pop()
        
        if type(iter) == StringType :
            iter = eval( iter )
        
        if type(iter) in [ListType, TupleType] :
            stack.push( any(iter) )
        
        else :
            raise ValueError, "any: Expect an iterable (list) on top of the stack"
    
    def chr( self, stack ) :
        '''
        chr : (int -> string)
        
        desc:
            converts the integer on top of the stack to a single character string
        
        tags:
            custom,string
        '''
        val = stack.pop()
        
        if type(val) == StringType and val.isdigit() :
            val = int( val )
        
        if type(val) == FloatType :
            val = int( val )
        
        if type(val) in [IntType, LongType] :
            stack.push( chr(val) )
        
        else :
            raise ValueError, "chr: Cannot convert argument to an integer"
    
    def enum( self, stack ) :
        '''
        enum : (list int:start -> list)
        
        desc:
            returns an enumerated list on top of the stack based on the
            starting int at [0] and the list at [-1] on the stack
        
        tags:
            custom,lists
        '''
        start, lst = stack.pop2()
        
        if type(start) in [StringType, FloatType] :
            start = int( start )
        
        if type(start) not in [IntType, LongType] :
            raise ValueError, "enum: Starting value must be an integer"
        
        if type(lst) == StringType :
            lst = eval( lst )
        
        if type(lst) not in [ListType, TupleType] :
            raise ValueError, "enum: The list must be an iterable or convertable to one"
        
        stack.push( [ [x,y] for x,y in enumerate(lst, start)] )
    
    def hash( self, stack ) :
        '''
        hash : (any -> int)
        
        desc:
            pushes the hash value of the object on top of the stack onto the stack
        
        tags:
            custom,math
        '''
        stack.push( hash(stack.pop()) )
    
    def id( self, stack ) :
        '''
        id : (any -> any int:id)
        
        desc:
            calculates a unique integer id for the object on top of
            the stack and then pushes this id onto the stack. This id
            is unique as long as the session lasts. A new session will
            produce a different id.
        
        tags:
            custom,math
        '''
        stack.push( id(stack.peek()) )
    
    def ord( self, stack ) :
        '''
        ord : (string:chr -> int)
        
        desc:
            takes the single character string (or first character of a longer string)
            and pushes the integer code for that character onto the stack
        
        tags:
            custom,string,math
        '''
        obj = stack.pop()
        
        if type(obj) in [ListType, TupleType] :
            obj = obj[0]
        
        if type(obj) != StringType :
            obj = str(obj)
        
        stack.push( ord(obj[0]) )
    
    def sort( self, stack ) :
        '''
        sort : (list -> list)
        
        desc:
            sorts the list on top of the stack in place
        
        tags:
            custom,sort,list
        '''
        obj = stack.pop()
        
        if type(obj) not in [ListType, TupleType] :
            stack.push( obj )
        
        else :
            stack.push( sorted(obj) )
    
    def zip( self, stack ) :
        '''
        zip : (list list -> list)
        
        desc:
            creates a list of paired objects from the two lists on
            top of the stack.
        
        tags:
            custom,lists
        '''
        r, l = stack.pop2()
        stack.push( [list(x) for x in zip(l, r)] )
    
    def unzip( self, stack ) :
        '''
        unzip : (list -> list:left list:right)
        
        desc:
            unzips the list on top of the stack to a pair of lists that
            are then pushed onto the stack. The first element of each
            of the pairs within the argument list goes into the left list
            and the second into the right list.
        
        tags:
            custom,lists
        '''
        lst = stack.pop()
        lst = zip(*lst)
        stack.push( list(lst[0]) )
        stack.push( list(lst[1]) )
    
    def split( self, stack ) :
        '''
        split : (string:target string:splitter -> list)
        
        desc:
            splits a target string into segments based on the 'splitter' string
        
        tags:
            custom,strings
        '''
        splitter, target = stack.pop2()
        
        if type(target) != StringType or type(splitter) != StringType :
            raise ValueError, "split: Both arguments must be strings"
        
        if len(splitter) == 0 :
            stack.push( [x for x in target] )
        
        else :
            stack.push( target.split(splitter) )
    
    def join( self, stack ) :
        '''
        join : (list string:connector -> string)
        
        desc:
            joins together the elements of the list at [-1] using the connector
            string at [0].
        
        tags:
            custom,strings,lists
        '''
        conn, lst = stack.pop2()
        
        if type(conn) != StringType :
            conn = str( conn )
        
        result = ''
        
        for item in lst :
            result += str(item) + conn
        
        stack.push( result.rstrip(conn) )
    
    def count_str( self, stack ) :
        '''
        count_str : (string:target string:test -> string:target int)
        
        desc:
            counts the number of non-overlapping occurrences of the test string at [0]
            found in the target string at [-1]
        tags:
            custom,strings
        '''
        test, target = stack.pop2()
        
        if type(test) != StringType or type(target) != StringType :
            raise ValueError, "count_str: Both target and test objects must be strings"
        
        stack.push( target )
        stack.push( target.count(test) )
    
    def eq( self, stack ) :
        """
        eq : (any any -> bool)
        
        desc:
            returns True if top two items on stack have the same value; otherwise False
        
        tags:
            level1,comparison"
        """
        a, b = stack.pop2()
        stack.push( a == b )

    def neq( self, stack ) :
        """
        neq : (any any -> bool)
        
        desc:
            returns True if top two items on stack have differning values; otherwise False
        
        tags:
            level1,comparison"
        """
        a, b = stack.pop2()
        stack.push( a != b )

    def gt( self, stack ) :
        """
        gt : (any any -> bool)
        
        desc:
            returns True if the value at [-1] is greater than the one at [0];
            otherwise False
        
        tags:
            level1,comparison"
        """
        a, b = stack.pop2()
        stack.push( b > a )

    def lt( self, stack ) :
        """
        lt : (any any -> bool)
        
        desc:
            returns True if the object at [-1] is less than the one at [0];
            otherwise False
        
        tags:
            level1,comparison"
        """
        a, b = stack.pop2()
        stack.push( b < a )

    def gteq( self, stack ) :
        """
        gteq : (any any -> bool)
        
        desc:
            returns True if the object at [-1] is greater than or equal to the one at [0];
            otherwise False
        
        tags:
            level1,comparison"
        """
        a, b = stack.pop2()
        stack.push( b >= a )

    def lteq( self, stack ) :
        """
        lteq : (any any -> bool)
        
        desc:
            returns True if the object at [-1] is less than or equal to the one at [0];
            otherwise False
        
        tags:
            level1,comparison"
        """
        a, b = stack.pop2()
        stack.push( b <= a )

    def clear( self, stack ) :
        '''
        clear : (A -> - )
        
        desc:
            removes all stack entries
        
        tags:
            level0,stack
        '''
        stack.clear()

    def pop( self, stack ) :
        '''
        pop : (A any -> A)
        
        desc:
            removes the top item from the stack
        
        tags:
            level0,stack"
        '''
        stack.pop()
    
    def popd( self, stack ) :
        '''
        pop : (b a -> a)
        
        desc:
            removes the item at [-1] on the stack
        
        tags:
            level0,stack"
        '''
        self.swap( stack )
        stack.pop()
    
    def drop( self, stack ) :
        '''
        drop : (b a -> a)
        
        desc:
            removes the top item from the stack
        
        tags:
            level0,stack"
        '''
        stack.pop()
    
    def pair( self, stack ) :
        '''
        pair : (b a -> [b, a])
        
        desc:
            makes a list of the top two stack elements
        
        tags:
            level0,stack
        '''
        t, n = stack.pop2()
        stack.push( [n, t] )
    
    def triplet( self, stack ) :
        '''
        pair : (a b c -> [a, b, c])
        
        desc:
            makes a list of the top three stack elements
        
        tags:
            level0,stack
        '''
        t, n, nn = stack.popn( 3 )
        stack.push( [nn, n, t] )
    
    def nTuple( self, stack ) :
        '''
        tuple : (elt_n elt_n-1 ... elt_1 int:n -> list)
        
        desc:
            Creates a list from n elements on the stack
            element at [0] is the number of elements
            elements at [-1] through [-n] are made into a list
        
        tags:
            level3,list
        '''
        n   = int( stack.pop() )
        lst = stack.popn( n )
        lst.reverse()
        stack.push( lst )
        
    def dup( self, stack ) :
        '''
        dup : (a -> a a)
        
        desc:
            duplicate the top item on the stack
        
        tags:
            level0,stack"
        '''
        stack.push( stack.peek() )

    def swap( self, stack ) :
        '''
        swap : (a b -> b a)
        
        desc:
            swap the top two items on the stack
        
        tags:
            level0,stack"
        '''
        a, b = stack.pop2()
        stack.push( (a, b), multi=True )

    def swapd( self, stack ):
        '''
        swapd : (c b a -> b c a)
        
        desc:
            swap the items at [-1] and [-2]
        
        tags:
            level0,stack"
        '''
        a, b, c = stack.popn( 3 )
        stack.push( (b, c, a), multi=True )

    def dupd( self, stack ) :
        '''
        dupd : (b a -> b b a)
        
        desc:
            duplicates the item at [-1] leaving item at [0] on top of the stack
        
        tags:
            level0,stack"
        '''
        a, b = stack.pop2()
        stack.push( (b, b, a), multi=True )

    def eval( self, stack ) :
        '''
        eval : ( func -> (func(A) -> B) )
        
        desc:
            applies a function to the stack (i.e. executes an instruction)
        
        tags:
            level0,functions"
        '''
        stack.eval( stack.pop() )
    
    def apply( self, stack ) :
        '''
        apply: ( func -> (func(A) -> B) )
        
        desc:
            applies a function to the stack (i.e. executes an instruction)
        
        tags:
            level0,functions"
        '''
        stack.eval( stack.pop() )
    
    def nil( self, stack ) :
        '''
        nil : ( -> list)
        
        desc:
            pushes an empty list onto the stack
        
        tags:
            level0,lists
        '''
        stack.push( [] )
    
    def n( self, stack ) :
        '''
        n : ( n -> [0, 1, ... n-1] )
        
        desc:
            using the integer on top of the stack, a list of sequential integers
            is pushed onto the stack according to the action of the standard
            Python range() function
        
        tags:
            level1,lists
        '''
        rng = range( int(stack.pop()) )
#        rng.reverse()
        stack.push( rng )

    def count( self, stack ) :
        '''
        count : (list -> list int)
        
        desc:
            returns the number of items in a list
        
        tags:
            level1,lists
        '''
        stack.push( len(stack.peek()) )

    def head( self, stack ) :
        '''
        head : ( list:any -> any )
        
        desc:
            relaces the list at [0] with its first member
        
        tags:
            level1,lists
        '''
        stack.push( stack.pop()[0] )

    def first( self, stack ) :
        '''
        first : ( list:any -> list:any any )
        
        desc:
            the first member of the list at [0] is pushed onto the stack
            the source list is unaltered
        
        tags:
            level1,lists
        '''
        stack.push( stack.peek()[0] )
    
    def rest( self, stack ) :
        '''
        rest : ( list:any -> list:any )
        
        desc:
            removes the first member from the list on top of the stack
        
        tags:
            level1,lists
        '''
        stack.push( stack.pop()[1:] )
    
    def tail( self, stack ) :
        '''
        tail : ( list:any -> list:any )
        
        desc:
            removes the first member from the list on top of the stack
        
        tags:
            level1,lists
        '''
        stack.push( stack.pop()[1:] )

    def rev( self, stack ) :
        '''
        rev : ( list:obj|string:obj -> reversed_obj )
        
        desc:
            reverses the order of members of the object on top of the stack.
            The object may be a list or a string
        
        tags:
            level1,lists
        '''
        val = stack.pop()
        
        if type(val) == StringType :
            stack.push( val[::-1] )
        
        else :
            val.reverse()
            stack.push( val )
    
    def map( self, stack ):
        '''
        map : (list func -> list)
        
        desc:
            creates a list from another by transforming each value using the supplied function
        
        tags:
            level0,lists
        '''
        func, elements = stack.pop2()
        # Evaluate the function with each of the elements.
        results  = []
        oldStack = [] + stack.stack     # this copies the stack
        
        # Push the value onto the stack and evaluate the function.
        for element in elements :
            stack.stack = [ element ]    # Create a new working stack 
            stack.eval( func )
            results.extend( stack.popall() )
        
        stack.stack = oldStack
        stack.push( results )

    def even( self, stack) :
        '''
        even : ( int -> boolean )
        
        desc:
            if the integer on top of the stack is even True is pushed onto the stack;
            otherwise False
        
        tags:
            level0,math,functions
        '''
        stack.push( (stack.pop() % 2) == 0 )

    def filter( self, stack ) :
        '''
        filter : ( [...] func -> [...] )
        
        desc:
            applies the function on the top of the stack to each element of the list
            immediately below it. If the result of the function is True (or non-zero)
            the corresponding element in the list (the argument to the function) is
            pushed onto a new list. When all elements of the argument list have been
            examined the results list being created is pushed onto the stack.
        
        tags:
            level0,lists,functions,map
        '''
        func, elements = stack.pop2()
        results        = []
        oldStack       = [] + stack.stack
        stack.stack    = []
        
        for element in elements :
            stack.push( element )
            stack.eval( func )
            
            if stack.pop() :
                results.append( element )
        
        stack.stack = oldStack
        stack.push( results )
    
    def fold( self, stack ) :
        '''
        fold : ('A list any:init func -> 'A any)
        
        desc:
            Also known as a reduce function, this combines adjacent values in a list
            using an initial value and a binary function.
            Semantics:
                define fold(xs x f) { xs empty [x] [xs uncons x swap f apply f fold] if }
        test:
            in:
                [1 2 3 4] list 0 [add] fold
            out:
                10
        test:
            in:
                [1 2 3 4] list 0 [popd] fold
            out:
                1
        tags:
            level0,lists

        '''
        f, init, a = stack.popn( 3 )
#        a.reverse()
        oldStack    = [] + stack.stack
        stack.stack = []
        
        for x in a :
            stack.push( init )
            stack.push( x )
            stack.eval( f )
            init = stack.pop()
        
        stack.stack = oldStack
        stack.push( init )
    
    def foreach( self, stack ) :
        '''
        foreach : (list func -> any|none)

        desc:
            Executes a function with each item in the list, and consumes the list.
            Semantics:
                $A $b [$C] foreach == $A $b empty not [uncons pop [$C] foreach] [pop] if }
            
        test:
            in:
                0 [1 2 3 4] list [add] foreach
            out:
                10
        
        tags:
            level2,control,iteration
        '''
        f, a = stack.pop2()
#        a.reverse()
        
        for x in a :
            stack.push( x )
            stack.eval( f )
    
    def dip( self, stack ) :
        '''
        dip: (arg any:saved func -> any:result any:saved)
        
        desc:
            Evaluates a function, temporarily removing the item below the function.
            This makes the item now on top of the stack the argument to the function.
            After evaluation of the function the removed item is restored to the
            top of the stack
        
        tags:
            level0,functions
        '''
        func, second = stack.pop2()
        stack.push( func )
        self.eval( stack )
        stack.push( second )
    
    def cons( self, stack ) :
        '''
        cons : (list any -> list)
        
        desc:
            appends an item to the right end of a list
          
        tags:
            level0,lists        
        '''
        t   = stack.pop()
        lst = stack.peek()
        
        if type(lst) == ListType :
            lst.append( t )
        
        else :
            lst = stack.pop()
            stack.push( [lst, t] )
    
    def uncons( self, stack ) :
        '''
        uncons : (list -> list any)
        
        desc:
            returns the right end of the list, and the rest of a list
        
        tags:
            level0,lists
        '''
        x = stack.pop()
        
        if type(x) in [ListType, TupleType] :
            y = x.pop()
            stack.push( x )
            stack.push( y )
        
        else :
            raise ValueError, "uncons: Argument on top of stack must be a list"
    
    def size( self, stack ) :
        '''
        size: (A -> A int)
        
        desc:
            pushes the size of the stack (i.e. number of items in the stack)
            onto the top of the stack
        
        tags:
            level0,lists,stack
        '''
        stack.push( stack.length() )
    
    def cat( self, stack ) :
        '''
        cat : (list list -> list)
        
        descr:
            concatenates two lists
        
        tags:
            level0,lists
        '''
        r, l = stack.pop2()
        
        if type(r) not in [ListType, TupleType] :
            r = [ r ]
        
        if type(l) not in [ListType, TupleType] :
            l = [ l ]
        
        stack.push( l + r )
    
    def get_at( self, stack ) :
        '''
        get_at : (list int -> list any)
        
        desc:
            returns the nth item in a list
        
        tags:
            level1,lists
        '''
        ix  = int( stack.pop() )
        lst = stack.peek()
        stack.push( lst[ix] )
    
    def set_at( self, stack ) :
        '''
        set_at : (list 'a int -> list)
        
        desc:
            sets an item in a list
        
        tags:
            level1,lists
        '''
        ix, val = stack.pop2()
        lst     = stack.peek()
        lst[int(ix)] = val
    
    def swap_at( self, stack ) :
        '''
        swap_at : (list any:value int:index -> list any:swappedOutVal)
        
        desc:
            swaps an item with an item in the list
        
        tags:
            level1,lists
        '''
        n     = int( stack.pop() )
        obj   = stack.pop()
        lst   = stack.peek()
        x     = lst[n]
        lst[n] = obj
        stack.push( x )
    
    def subseq( self, stack ) :
        '''
        subseq : (list|string int:start int:end -> list|string sublist|substring)
        
        desc:
            pushs a segment of a list or a string onto the stack
            start is the starting offset into the list or string
            end is the ending offset (i.e. the up-to index)
            the usual Python rules for slicing a list or string apply
        
        tags:
            level1,lists,strings
        '''
        end, start = stack.pop2()
        lst        = stack.peek()
        stack.push( lst[int(start) : int(end)] )
    
    def true( self, stack ) :
        '''
        true: ( -> bool)
        
        desc:
            pushes the boolean value True on the stack
        
        tags:
            level0,boolean"
        '''
        stack.push( True )
    
    def false( self, stack ) :
        '''
        false: ( -> bool)
        
        desc:
            pushes the boolean value False on the stack
        
        tags:
            level0,boolean"
        '''
        stack.push( False )
    
    def eqz( self, stack ) :
        '''
        eqz : (int -> bool)

        desc:
            Returns true if the top value is zero
        test:
            in:
                5 eqz
            out:
                False
        test:
            in:
                0 eqz
            out:
                True
        tags:
            level0,math
        '''
        stack.push( stack.pop() == 0 )
    
    def quote( self, stack ) :
        '''
        quote: (any -> func)
        
        desc:
            creates a constant generating function from the top value on the stack
        
        tags:
            level0,functions"
        '''
        t = stack.pop()
        stack.push( lambda : stack.push(t) )
    
    def compose( self, stack ) :
        '''
        compose: (func:left func:right -> func)
        
        desc:
            creates a function by composing (concatenating) two existing functions
        
        tags:
            level0,functions"
        '''
        f1, f2 = stack.pop2()
        stack.push( lambda : stack.eval2(f2, f1) )
    
    def empty( self, stack ) :
        '''
        empty : (list|string -> list|string bool)

        desc:
            pushes True onto the stack if the list or string is empty
        
        tags:
            level0,lists,strings
        '''
        lst = stack.peek()
        stack.push( len(lst) == 0 )
    
    def unit( self, stack ) :
        '''
        unit : ('A 'b -> 'A list)

        desc:
            Creates a list containing one element taken from the top of the stack
            
        test:
            in:
                42 unit
            out:
                [42]
        tags:
            level1,lists
        '''
        stack.push( [stack.pop()] )
    
    def repeat( self, stack ) :
        '''
        repeat : (func int:n -> any|none)

        desc:
            Executes a loop a fixed number of times
            Semantics: $A [$B] $c repeat == $A $c eqz [] [$B $c dec] if
        test:
            in:
                3 [inc] 3 repeat
            out:
                6
        test:
            in:
                3 [2 mul] 2 repeat
            out:
                12
        test:
            in:
                3 [inc] 0 repeat
            out:
                3
        tags:
            level1,control
        '''
        n, f = stack.pop2()
        n    = abs( int(n) )
        
        while n > 0 :
            stack.eval( f )
            n -= 1
    
    def to_int( self, stack ) :
        '''
        to_int : (any -> int)
        
        desc:
            coerces any value to an integer
        
        tags:
            level1,conversion
        '''
        obj = stack.pop()
        
        if type(obj) in [ListType, TupleType] :
            stack.push( len(obj) )
        
        else :
            stack.push( int(obj) )
    
    def to_str( self, stack ) :
        '''
        to_str : (any -> str)
        
        desc:
            coerces any value to a string
        
        tags:
            level1,conversion
        '''
        stack.push( str(stack.pop()) )
    
    def to_bool( self, stack ) :
        '''
        to_bool : (any -> bool)
        
        desc:
            coerces any value to a boolean
        
        tags:
            level1,conversion
        '''
        stack.push( bool(stack.pop()) )
    
    def write( self, stack ) :
        '''
        write : (string:text string:color -> --)
        
        desc:
            outputs the text representation of a value to the console in the specified color
        
        tags:
            level1,console
        '''
        color, text = stack.pop2()
        
        if color == '' :
            color = 'black'
        
        if type(obj) in [ListType, TupleType] :
            print colored( self._formatList( obj, 4 ), color ),
        
        elif type(obj) == DictType :
            print colored( repr(obj), color ),
        
        else :
            if type(obj) != StringType :
                obj = str( obj )
            
            lines = obj.split( "\\n" )  # this is curious but it works
            
            for line in lines:
                print colored( line, color ),
    
    def writeln( self, stack ) :
        '''
        writeln : (string:text string:color -> --)
        
        desc:
            outputs the text representation of a value to the console in the
            requested color
        
        tags:
            level1,console,display
        '''
        color, obj = stack.pop2()
        
        if color == '' :
            color = 'black'
        
        if type(obj) in [ListType, TupleType] :
            print colored( self._formatList( obj, 4 ), color )
        
        elif type(obj) == DictType :
            print colored( repr(obj), color )
        
        else :
            if type(obj) != StringType :
                obj = str( obj )
            
            lines = obj.split( "\\n" )  # this is curious but it works
            
            for line in lines:
                print colored( line, color )
    
    def neg( self, stack ) :
        '''
        neg : (nbr -> nbr)
        
        desc:
            Negates top value.
        
        tags:
            level1,math
        '''
        arg = stack.pop()
        
        if type(arg) in [FloatType, IntType, LongType] :
            stack.push( -arg )
        
        elif type(arg) == BooleanType :
            stack.push( not arg )
        
        else :
            raise Exception, "neg: Cannot negate %s" % str(arg)
    
    def papply( self, stack ) :
        '''
        papply : (any func -> func)
        
        desc:
            partial application: binds the top argument to the top value in the stack
            E.g. (1 [<=] papply -> [1 <=])
        
        tags:
            level0,functions
        '''
        self.swap( stack )
        self.quote( stack )
        self.swap( stack )
        self.compose(stack )
    
    def int_to_byte( self, stack ) :
        '''
        int_to_byte : (int -> byte)
        
        desc:
            converts an integer into a byte, throwing away sign and ignoring higher bits
        
        tags:
            level1,math,conversion
        '''
        stack.push( int(stack.pop()) & 0377 )
    
    def bin_str( self, stack ) :
        '''
        bin_str : (int -> string)
      
        desc:
            converts an integer into its binary string representation.
        
        tags:
            level2,strings,math,conversion
        '''
        stack.push( bin(int(stack.pop())) )
    
    def format( self, stack ) :
        '''
        format : (list:args string:format -> string)
        
        desc:
            returns a string as formatted by the format statement on top of the based
            on the argument values in the LIST below the format.
            Uses Python format conventions.
        
        tags:
            level1,string,format,conversion
        '''
        fmt, vals = stack.pop2()
        stack.push( fmt % tuple(vals) )
    
    def hex_str( self, stack ) :
        '''
        hex_str : (int -> string)
        
        desc:
            converts a number into a hexadecimal string representation.
        
        tags:
            custom,strings,math,conversion
        '''
        stack.push( hex(int(stack.pop())) )
    
    def halt( self, stack ) :
        '''
        "halt : (A int -> A )
        
        desc:
            halts the program with an error code by raising an exception
            
        tags:
            level2,application
        '''
        n = int( stack.pop() )
        raise Exception, "halt: Program halted with error code: " + n
    
    def dispatch1( self, stack ) :
        '''
        dispatch1 : (list:functions any:arg -> any)
        
        desc:
            dynamically dispatches a function depending on the object on top of the stack
            E.g. (3 [[dup] 1 [drop] 2 [swap] 3] list 1 dispatch1 -> 3 3)
        
        tags:
            level1,functions
        '''
        lst = stack.pop()
#        obj = stack.peek()
        obj = stack.pop()
        
        for i in range(len(lst) / 2) :
            t = lst[2 * i + 1]
            f = lst[2 * i]
            
            if t == obj :
                self.eval( f )
                return
        
        raise Exception, "dispatch1: Could not dispatch function"
    
    def dispatch2( self, stack ) :
        '''
        dispatch2 : (list:functions any:arg -> any)
        
        desc:
            dynamically dispatches a function depending on the object on top of the stack
            E.g. (3 [1 [dup] 2 [drop] 3 [swap]] list 1 dispatch2 -> 3 3)
        
        tags:
            level1,functions
        '''
        lst = stack.pop()
#        obj = stack.peek()
        obj = stack.pop()
        
        for i in range(len(lst) / 2) :
            f= lst[2 * i + 1]
            t = lst[2 * i]
            
            if t == obj :
                self.eval( f )
                return
        
        raise Exception, "dispatch2: Could not dispatch function"
    
    def explode( self, stack ) :
        '''
        explode : (func -> list)
        
        desc:
            breaks a function up into a list of instructions
        
        tags:
            level2,functions
        '''
        defined, func = self.getFunction( stack.pop() )
        
        if defined :
            stack.push( func )
        
        else :
            raise ValueError, "explode: Undefined function"
    
    def throw( self, stack ) :
        '''
        throw : (any -> --)
        
        desc:
            throws an exception
        
        tags:
            level2,control
        '''
        raise Exception, "throw: " + str( stack.pop() )
    
    def try_catch( self, stack ) :
        '''
        "try_catch : (func func:action -> --)
        
        desc:
            evaluates a function, and catches any exceptions
        
        tags:
            level2,control
        '''
        c, t = stack.pop2()
        old  = [] + stack.stack
        
        try :
            stack.eval( t )
        
        except Exception, msg :
            stack.stack = old
            print colored( "exception caught", 'red' )
            stack.push( msg )
            stack.eval( c )
    
    def typename( self, stack ) :
        '''
        typename : (any -> string)
        
        desc:
            returns the name of the type of an object
        
        tags:
            level1,types
        '''
        stack.push( type(stack.pop()) )
    
    def typeof( self, stack ) :
        '''
        typeof : (any -> any type)
        
        desc:
            returns a type tag for an object
        
        tags:
            level1,types
        '''
        stack.push( type(stack.peek()) )
    
    def int_type( self, stack ) :
        '''
        int_type : ( -> type)
        
        desc:
            pushes a value representing the type of an int
        
        tags:
            level1,types
        '''
        stack.push( IntType )
    
    def string_type( self, stack ) :
        '''
        string_type : ( -> type)
        
        desc:
            pushes a value representing the type of a string
        
        tags:
            level1,types
        '''
        stack.push( StringType )
    
    def float_type( self, stack ) :
        '''
        float_type : ( -> type)
        
        desc:
            pushes a value representing the type of a float
        
        tags:
            level1,types
        '''
        stack.push( FloatType )
    
    def bool_type( self, stack ) :
        '''
        bool_type : ( -> type)
        
        desc:
            pushes a value representing the type of a boolean
        
        tags:
            level1,types
        '''
        stack.push( BooleanType )
    
    def list_type( self, stack ) :
        '''
        list_type : ( -> type)
        
        desc:
            pushes a value representing the type of a list
        
        tags:
            level1,types
        '''
        stack.push( ListType )
    
    def function_type( self, stack ) :
        '''
        function_type : ( -> type)
        
        desc:
            pushes a value representing the type of a list
        
        tags:
            level1,types
        '''
        stack.push( FunctionType )
    
    def datetime_type( self, stack ) :
        '''
        datetime_type : ( -> type)
        
        desc:
            pushes a value representing the type of a list
        
        tags:
            level1,types
        '''
        import datetime

        now = datetime.datetime.now()
        stack.push( type(now) )
    
    def type_eq( self, stack ) :
        '''
        type_eq : (type type -> type type bool)
        
        desc:
            returns true if either type is assignable to the other
        
        tags:
            level1,types
        '''
        l = stack.stack[-2]
        r = stack.stack[-1]
        stack.push( type(l) == type(r) )
    
    def now( self, stack ) :
        '''
        now : ( -> date_time)
        
        desc:
            pushes a value representing the current date and time onto the stack
        
        tags:
            level2,datetime
        '''
        import datetime

        stack.push( datetime.datetime.now() )
    
    def sub_time( self, stack ) :
        '''
        sub_time : (date_time date_time -> time_span)
        
        desc:
            computes the time interval between two dates
        
        tags:
            level2,datetime
        '''
        r, l = stack.pop2()
        stack.push( l - r )
    
    def add_time( self, stack ) :
        '''
        add_time : (date_time time_span -> date_time)
        
        desc:
            computes a date by adding a time period to a date
        
        tags:
            level2,datetime
        '''
        r, l = stack.pop2()
        stack.push( l + r )
    
    def to_msec( self, stack ) :
        '''
        to_msec : (time_span -> int)
        
        desc:
            computes the length of a time span in milliseconds
        
        tags:
            level2,datetime
        '''
        ts = stack.pop()
        ts = ts.total_seconds() * 1000.0
        stack.push( round(ts, 3) )
    
    def iso_format( self, stack ) :
        '''
        iso_format : ( datetime -> string:iso_date)
        
        descr:
            returns the ISO formatted date and time string of the datetime on top of the stack
        
        tags:
            level2,datetime
        '''
        dt = stack.pop()
        stack.push( dt.isoformat() )
    
    def time_str( self, stack ) :
        '''
        time_str : ( time_delta -> string:formatted_time)
        
        descr:
            returns a formatted time string of the timedelta on top of the stack
        
        tags:
            level2,datetime
        '''
        td = stack.pop()
        stack.push( str(td) )
    
    def del_var( self, stack ) :
        '''
        del_var : (string:name -> --)
        
        desc:
            removes user variable from symbol table
            Note: name can be a string of the form: name1,name2,...   (e.g. 'var1,test)
                  or a list  (e.g. ['var1 'test])
        
        tags:
            custom,user_variables
        '''
        top = stack.pop()
        
        if type(top) == StringType :
            names = [x for z in top.split(",") if x != '']
        
        elif type(top) in [ListType, TupleType] :
            names = top
        
        else :
            raise ValueError, "del_var: The variable to be deleted must have a string name or be a list of strings"
        
        for name in names :
            if name in self.NSdict[self.userNS]['__vars__'] :
                del self.NSdict[self.userNS]['__vars__'][name]
    
    def min( self, stack ) :
        '''
        min : (a b -> min(a,b) )
        
        desc:
            pushes the minimum of the two arguments on top of the stack.
            Numbers: the smaller number
            Strings: the shorter string
            Lists: the shorter list
        
        tags:
            level2,math,string,list
        '''
        t, u = stack.pop2()
        stack.push( min(t, u) )
    
    def max( self, stack ) :
        '''
        max : (a b -> max(a,b) )
        
        desc:
            pushes the larger of the two arguments on top of the stack.
            Numbers: the larger number
            Strings: the longer string
            Lists: the longer list
        
        tags:
            level2,math,string,list
        '''
        t, u = stack.pop2()
        stack.push( max(t, u) )
    
    def new_str( self, stack ) :
        '''
        new_str : ( string:str int:n -> string:new_str )
        
        desc:
            create a new string on top of the stack from a string and a count
        
        tags:
            level2,string
        '''
        n, c = stack.pop2()
        s = eval( "'%s' * %d" % (c, n) )
        stack.push( s )
    
    def index_of( self, stack ) :
        '''
        index_of : (target string:test -> int:index)
        
        desc:
            returns the index of the starting position of a test string in a target string
            or the index of the test object in a list. Returns -1 if not found.
        
        tags:
            level2,string
        '''
        tst, tgt = stack.pop2()
        
        if type(tgt) in [ListType, TupleType] :
            stack.push( tgt.index(tst) )
        
        else :
            stack.push( tgt.find(tst) )
    
    def rindex_of( self, stack ) :
        '''
        rindex_of : (target string:test -> int:index)
        
        desc:
            returns the index of the last position of a test string in a target string
            or the last index of the test object in a list. Returns -1 if not found.
        
        tags:
            level2,string
        '''
        tst, tgt = stack.pop2()
        
        if type(tgt) in [ListType, TupleType] :
            n = len(tgt)
            tgt.reverse()
            ix = tgt.index(tst)
            
            if ix == -1 :
                stack.push( -1 )
            
            else :
                stack.push( n - ix - 1 )
        
        else :
            stack.push( tgt.rfind(tst) )
    
    def replace_str( self, stack ) :
        '''
        replace_str : (string:target string:test string:replace -> string)
        
        desc:
            replaces a test string within a target string with a replacement string
        
        tags:
            level2,string
        '''
        rpl, tst, tgt = stack.popn( 3 )
        
        if type(rpl) != StringType or type(tst) != StringType or type(tgt) != StringType :
            raise ValueError, "replace_str: All three arguments must be strings"
        
        stack.push( tgt.replace(tst, rpl) )
    
    def str_to_list( self, stack ) :
        '''
        str_to_list : (string -> list)
        
        desc:
            explodes the string on top of the stack into a list of individual letters
        
        tags:
            level2,string,list
        '''
        s = stack.pop()
        stack.push( [x for x in s] )
    
    def list_to_str( self, stack ) :
        '''
        list_to_str : (list -> string)
        
        desc:
            creates a string by concatenating the string representations of items
            in the list on top of the stack
        
        tags:
            level2,string,list
        '''
        lst = stack.pop()
        buf = ''
        
        for item in lst :
            buf += str( item )
        
        stack.push( buf )
    
    def list_to_hash( self, stack ) :
        '''
        list_to_hash : (list -> hash:newDict)
        
        desc:
            converts a list of pairs to a hash_list (dictionary)
            leaves the new hash list on top of the stack
        
        tags:
            level2,hash_list,list
        '''
        top = stack.pop()
        
        if type(top) in [ListType, TupleType] :
            stack.push( dict(top) )
        
        else :
            raise ValueError, "list_to_hash: Expect a list on top of the stack"
    
    def pyList( self, stack ) :
        '''
        pyList : (string:arg|any:arg -> list)
        
        desc:
            converts a string to a list
            string formats:
                "1,2,3,4,'x'"
                "zzz"
                "[1,2,3,4,'x']"
                "(1,2,3,4,'x')"
            other format:
                any (e.g. 3.14)
        
        tags:
            custom,string,list
        '''
        lst = stack.pop()
        
        if type(lst) == StringType :
            if lst[0] in "[(" :
                lst = list( eval(lst) )
            
            else :
                lst = eval( "[" + lst + "]" )
        
        else :
            lst = [lst]
        
        stack.push( lst )
    
    def readln( self, stack ) :
        '''
        readln : ( -> string)
        
        desc:
            inputs a string from the console
            no conversion of any sort is done
            for a prompt, use write first e.g. "date: " write readln
        
        tags:
            level1,console
        '''
        line = raw_input( "" )
        stack.push( line )
    
    def file_reader( self, stack ) :
        '''
        file_reader : (string:filePath -> istream)
        
        desc:
            creates an input stream from a file name
        
        tags:
            level2,streams
        '''
        fName = stack.pop()
        
        if fName == StringType :
            stack.push( open(fName, 'r') )
        
        else :
            raise ValueError, "file_reader: File name must be a string"
    
    def file_writer( self, stack ) :
        '''
        file_writer : (string:filePath -> ostream)
        
        desc:
            creates an output stream from a file name
        
        tags:
            level2,streams
        '''
        fName = stack.pop()
        
        if fName == StringType :
            stack.push( open(fName, 'w') )
        
        else :
            raise ValueError, "file_writer: File name must be a string"
    
    def file_exists( self, stack ) :
        '''
        file_exists : (string:filePath -> string:filePath bool)
        
        desc:
            returns a boolean value indicating whether a file or directory exists
        
        tags:
            level2,streams
        '''
        from os import path
        
        name = stack.peek()
        
        if type(name) == StringType :
            stack.push( path.exists(name) )
        
        else :
            raise ValueError, "file_exists: File name must be a string"
    
    def temp_file( self, stack ) :
        '''
        temp_file : ( -> fd string:path)
        
        desc:
            creates a unique temporary file
        
        tags:
            level2,streams
        '''
        import tempfile
        
        fd, path = tempfile.mkstemp( suffix='tmp', text=True )
        stack.push( (fd, path), multi=True )
    
    def read_bytes( self, stack ) :
        '''
        read_bytes : (istream int:nr_bytes -> istream byte_block)
        
        desc:
            reads a number of bytes into an array from an input stream
        
        tags:
            level2,streams,string
        '''
        n   = stack.pop()
        fd  = stack.peek()
        buf = fd.read( n )
        stack.push( buf )
    
    def write_bytes( self, stack ) :
        '''
        write_bytes : (ostream byte_block -> ostream)
        
        desc:
            writes a byte array to an output stream
        
        tags:
            level2,streams,string
        '''
        buf = stack.pop()
        fd  = stack.peek()
        fd.write( buf )
    
    def close_stream( self, stack ) :
        '''
        close_stream : (stream -> )
        
        desc:
            closes a stream
        
        tags:
            level2,streams
        '''
        fd = stack.pop()
        
        if type(fd) != FileType :
            stack.push( fd )
            raise ValueError, "close_stream: Expect a file descriptor on top of stack"
        
        fd.flush()
        fd.close()
    
    # much more i/o and file stuff through "'os.path #import"
    
    def hash_list( self, stack ) :
        '''
        hash_list : ( -> hash_list)
        
        desc: 
            makes an empty hash list (dictionary)
        
        tags:
            level2,hash
        '''
        stack.push( {} )
    
    def hash_get( self, stack ) :
        '''
        hash_get : (hash_list any:key -> hash_list any:value)
        
        desc:
            gets a value from a hash list using a key
        
        tags:
            level2,hash
        '''
        key  = stack.pop()
        dict = stack.peek()
        
        if key in dict :
            stack.push( dict[key] )
        
        else :
            raise KeyError, "hash_get: No hash list entry for key " + str(key)
    
    def hash_set( self, stack ) :
        '''
        hash_set : (hash_list any:value any:key -> hash_list)
        
        desc:
            associates the second value with a key (the top value) in a hash list
        
        tags:
            level2,hash
        '''
        key, val  = stack.pop2()
        dict      = stack.peek()
        dict[key] = val
    
    def hash_add( self, stack ) :
        '''
        hash_add : (hash_list any:value any:key -> hash_list)
        
        desc:
            associates the second value with a key (the top value) in a hash list if the
            key is not already present
        
        tags:
            level2,hash
        '''
        key, val  = stack.pop2()
        dict      = stack.peek()
        
        if key not in dict :
            dict[key] = val
        
        else :
            stack.push( (key, val), multi=True )
            raise Warning, "hash_add: Key already present in hash list. Use 'hash_set' to replace"
    
    def hash_contains( self, stack ) :
        '''
        hash_contains : (hash_list any:key -> hash_list bool)
        
        desc:
            returns true if hash list contains key
        
        tags:
            level2,hash
        '''
        key  = stack.pop()
        dict = stack.peek()
        stack.push( key in dict )
    
    def hash_to_list( self, stack ) :
        '''
        hash_to_list : (hash_list -> list)
        
        desc:
            converts a hash_list to a list of pairs
        
        tags:
            level2,hash
        '''
        dict = stack.pop()
        stack.push( [list(i) for i in dict.items()] )
    
    def as_int( self, stack ) :
        '''
        as_int : (any -> int)
        
        desc:
            casts a variant to an int
            same as to_int
        
        tags:
            level1,conversion
        '''
        stack.push( int(stack.pop()) )
    
    def as_bool( self, stack ) :
        '''
        as_bool : (any -> bool)
        
        desc:
            casts a variant to a bool
            same as to_bool
        
        tags:
            level1,conversion
        '''
        stack.push( bool(stack.pop()) )
    
    def as_list( self, stack ) :
        '''
        as_list : (any -> list)
        
        desc:
            casts a variant to a list
        
        tags:
            level1,conversion
        '''
        obj = stack.pop()
        
        if type(obj) == ListType :
            stack.push( obj )
        
        elif type(obj) == TupleType :
            stack.push( list(obj) )
        
        else :
            stack.push( [obj] )
    
    def as_string( self, stack ) :
        '''
        as_string : (any -> string)
        
        desc:
            casts a variant to a string
            same as to_str
        
        tags:
            level1,conversion
        '''
        stack.push( str(stack.pop()) )
    
    def as_float( self, stack ) :
        '''
        as_float : (any -> float)
        
        desc:
            casts a variant to a float
            same as float
        
        tags:
            level1,conversion
        '''
        stack.push( float(stack.pop()) )
    
    def fetch( self, stack ) :
        '''
        fetch  : (string:word -> --)
        
        desc:
            fetches and loads into the user's workspace the standard definition of the
            word on top of the stack. The "word" may be of the form 'word1,word2,word3,...
            (e.g. 'test,other) or a list (e.g. ['test 'other] list)
            The words may also be prefixed by <namespace>:  (e.g. 'core:modn) to fetch
            the word from an existing namespace (e.g. 'core:modn fetch fetches word 'modn'
            from namespace 'core')
        
        tags:
            extension,word,define
        '''
        from glob import iglob
        
        # check to see if we are coming from 'loadNS'
        if self.targetNS == '' :
            tgtNS = self.userNS
        
        else :
            tgtNS = self.targetNS
        
        parseDeps = re.compile( r'.*deps:\s*(\S+)', re.DOTALL )
        theWord   = stack.pop()
        
        if type(theWord) == StringType :
            words = [x for x in theWord.split(",") if x != '']
        
        elif type(theWord) in [ListType, TupleType] :
            words = theWord
        
        search  = self.NSdict.keys()
        search.remove( 'std' )
        search.remove( self.userNS )
        
        for word in words :
            if word == '' :
                continue
            
            # make sure it is not a standard method
            if hasattr( self, word ) :
                continue
            
            # look first in the namespaces, checking first for a special form
            if word.count( ":" ) == 1 :
                # special form: <namespace>:<word>
                ns, func = word.split( ":" )
                
                if ns in self.NSdict :
                    if func in self.NSdict[ns] :
                        self.NSdict[self.userNS][func] = self.NSdict[ns][func]
                        found = True
                        # have to take care of any dependencies
                        doc = self.NSdict[tgtNS][func][1]
                        mo  = parseDeps.match( doc )
                        
                        if mo :
                            deps = mo.group(1).split(",")
                            
                            for dep in deps :
                                stack.push( dep )
                                self.fetch( stack )
                        break
                    
                    else :
                        raise ValueError, "fetch: No word called '%s' in namespace '%s'" % (finc, ns)
                
                else :
                    raise ValueError, "fetch: No namespace called '%s'" % ns
            
            else :
                # not a special form, search namespaces
                found = False
                
                for ns in search :
                    if ns in self.NSdict[ns] :
                        self.NSdict[self.userNS][word] = self.NSdict[ns][word]
                        found = True
                        # have to take care of any dependencies
                        doc = self.NSdict[tgtNS][word][1]
                        mo  = parseDeps.match( doc )
                        
                        if mo :
                            deps = mo.group(1).split(",")
                            
                            for dep in deps :
                                stack.push( dep )
                                self.fetch( stack )
                        break
            
            # not in a namespace?
            if not found :
                # not present in the name space dictionaries, search the standard definition files
                path  = self.NSdict['std']['__globals__']['CatDefs']
                path += "*.cat"
                
                # escape characters in theWord that are interpreted by "re"
                letters = [ x for x in word ]
                
                for i in range(len(letters)) :
                    c = letters[i]
                    
                    if c in ".[]{}^$*?()+-|" :  # regular expression characters
                        letters[i] = "\\" + c
                
                theWord    = "".join( letters )
                expression = ""
                
                # search the standard definition files
                regex = re.compile( r'^\s*define\s+(%s)' % theWord )
                inDef = False
                
                for file in iglob( path ) :
                    if inDef :
                        break
                    
                    fd = open( file, 'r' )
                    
                    for line in fd :
                        temp = line.strip()
                        
                        if temp == "" :
                            continue
                        
                        if temp.startswith( "//" ) or temp.startswith( "#" ) :
                            continue
                        
                        # look for line starting with "define"
                        if not inDef and regex.match( temp ) :
                            inDef = True
                            
                        if inDef :
                            # collect all up to a single closing }
                            ix = line.rfind( "//" )
                            
                            if ix > 0 :
                                line = line[:ix]
                            
                            expression += line
                            
                            if not temp.endswith( "}}" ) and temp.endswith( "}" ) :
                                break
                    
                    fd.close()
                
                if inDef :
                    stack.define( expression, tgtNS )
                
                else :
                    raise ValueError, "fetch: No definition can be found for " + word
    
    def bin_str( self, stack ):
        """
        bin_str : (int -> string)
        
        desc
            Pushes the binary string representation of the number on top of the stack
            onto the stack
        
        tags:
            string,conversion
        """
        stack.push( bin(int(stack.pop())) )
    
    def oct_str( self, stack ) :
        """
        oct_str : (int -> string)
        
        desc
            Pushes the octal string representation of the number on top of the stack
            onto the stack
        
        tags:
            string,conversion
        """
        stack.push( oct(int(stack.pop())) )
    
    def bit_and( self, stack ) :
        '''
        &       : (int int -> int)
        bit_and : (int int -> int)
        
        desc:
            performs bit-wise logical and on top two stack elements
        
        tags:
            custom,math
        '''
        r, l = stack.pop2()
        stack.push( int(l) & int(r) )
    
    def bit_or( self, stack ) :
        '''
        |      : (int int -> int)
        bit_or : (int int -> int)
        
        desc:
            performs bit-wise logical or on top two stack elements
        
        tags:
            custom,math
        '''
        r, l = stack.pop2()
        stack.push( int(l) | int(r) )
    
    def bit_not( self, stack ) :
        '''
        ~ : (int -> int)
        bit_not : (int -> int)
        
        desc:
            performs bit-wise logical negation on top stack element as an integer
        
        tags:
            custom,math
        '''
        def bitLen( anInt ) :
            length = 0
            
            while anInt :
                anInt >>= 1
                length += 1
            
            return length
        
        n      = int( stack.pop() )
        length = bitLen( n )
        value  = ~n & (2**length - 1)
        stack.push( value )
    
    def cross_prod( self, stack ) :
        '''
        cross_prod : (list:nbr list:nbr -> list:nbr)
        
        desc:
            computes the standard 3-D vector cross product
        
        tags:
            level1,vectors
        '''
        r, l = stack.pop2()
        
        if len(l) != len(r) or len(l) > 3 or len(r) > 3 :
            raise ValueError, "cross_prod: Both vectors must each be of length 3"
        
        a1, a2, a3 = l
        b1, b2, b3 = r
        c = [ a2 * b3 - b2 * a3, a3 * b1 - b3 * a1, a1 * b2 - b1 * a2 ]
        stack.push( c )
    
    def powers( self, stack ) :
        '''
        powers : ( int:base int:max_exponent -> list)
        
        desc:
            pushes a list of powers of the base onto the stack in descending order of exponent.
            E.g. x 3 powers -> [x**3, x**2, x**1, x**0] for some value x
        
        tags:
            custom,math,polynomials
        '''
        n, x = stack.pop2()
        
        if type(n) not in [IntType, LongType] :
            raise ValueError, "powers: Exponent must be an integer"
        
        if type(x) not in [IntType, LongType, FloatType] :
            raise ValueError, "powers: Base must be a number"
        
        l    = [x**i for i in range(n + 1)]
        l.reverse()
        stack.push( l )
    
    def poly( self, stack ):
        '''
        poly : (list:coeffs nbr:x -> nbr)
        
        desc:
            Calculate polynomial with coefficients 'a' at point x.
            The polynomial is a[0] + a[1] * x + a[2] * x^2 + ...a[n-1]x^(n-1)
            the result is
                a[0] + x(a[1] + x(a[2] +...+ x(a[n-1])...)
            This implementation is also known as Horner's Rule.
        
        tags:
            math,polynomials
        '''
        x, a = stack.pop2()
        
        n = len( a ) - 1
        p = a[n]
        
        for i in range( 1, n + 1 ) :
            p = p * x + a[n - i]
        
        return p
    
    def bin_op( self, stack ) :
        '''
        bin_op : (list:any list:any func -> list:any)
        
        desc:
            puts the i-th argument from each list on the stack
            applies the function originally on top of the stack to the two arguments
            appends the result left on top of the stack to a list
            The result list is finally returned on top of the stack
        
        tags:
            custom,lists,math
        '''
        f, r, l        = stack.popn( 3 )
        original_stack = [] + stack.stack
        stack.stack    = [ ]
        
        if len(l) != len(r) :
            stack.stack = original_stack
            raise ValueError, "bin_op: Lists must be of the same length"
        
        result = [ ]
        n      = len( r )
        
        for i in range(n) :
            stack.push( l[i] )
            stack.push( r[i] )
            stack.eval( f )
            
            if stack.length > 0 :
                result.append( stack.pop() )
            
            else :
                result.append( None )
        
        stack.stack = original_stack
        stack.push( result )
    
    def getWords( self, stack ) :
        '''
        getWords : (-> list:names)
        
        desc:
            returns a list of words defined in the current user namespace
        
        tags:
            custom,words,user
        '''
        keys = self.NSdict[self.userNS].keys()
        keys.remove( '__vars__' )
        keys.remove( '__links__' )
        keys.remove( '__inst__' )
        keys.remove( '__loadList__' )
        
        if len(keys) == 0 :
            stack.push( [] )
        
        else :
            stack.push ( keys )
    
    # namespace methods
    def createNS( self, stack ) :
        '''
        createNS : (string:name -> --)
        
        desc:
            Creates one or more namespaces from the string on top of the stack
            Note: name may also be of the form name1,name2,name3,... (e.g. 'flow,test)
                  or a list  (e.g. ['flow 'test] list
        
        tags:
            custom,namespace
        '''
        top = stack.pop()
        
        if type(top) == StringType :
            names = [x for x in top.split( "," ) if x != '']
        
        elif type(top) in [ListType, TupleType] :
            names = top
        
        else :
            raise ValueError, "createNS: Expect a string or list"
        
        for name in names :
            if name == '' :
                continue
            
            if name in ['', 'std', self.userNS] :
                continue
            
            elif name in self.NSdict.keys() :
                raise ValueError, "createNS: The name '%s' is already in use" % name
            
            else :
                self.NSdict[name] = { '__vars__' : { }, '__links__' : [ ], '__inst__' : { }, '__loadList__' : [ ] }
    
    def setNS( self, stack ) :
        '''
        setNS : (string:ns|list:ns -> --)
        
        desc:
            sets the list of namespaces to be searched to the string on top of the stack
            Note: ns may be of the form name1.name2,name3,...  (e.g. 'flow,predicates)
                  or a list (e.g. ['predicates 'flow] list)
        
        tags:
            custom,namespaces
        '''
        ns = stack.pop()
        
        if type(ns) == StringType :
            items = [ x for x in ns.split(",") if x != '']
        
        elif type(ns) in [ListType, TupleType] :
            items = ns
        
        else :
            raise ValueError, "setNS: Expect a string or list"
        
        lst = [ ]
        
        for name in items :
            if name == self.userNS :
                continue
            
            if name in self.NSdict :
                lst.append( name )
        
        self.NSdict[self.userNS]['__links__'] = lst
    
    def renameNS( self, stack ) :
        '''
        renameNS : (string:old string:new -> --)
        
        desc:
            renames an old namespace to a new name
        
        tags:
            custom,namespaces
        '''
        new, old  = stack.pop2()
        protected = ['std', 'user']
        
        if old in protected or new in protected :
            raise ValueError, "renameNS: Cannot rename 'user' or 'std'"
        
        elif new in self.NSdict.keys() :
            raise ValueError, "renameNS: The name '%s' is already in use" % name
        
        if old in self.NSdict :
            temp = self.NSdict[old].copy()
            del self.NSdict[old]
            self.NSdict[new] = temp
        
        if old == self.userNS :
            self.userNS = new
    
    def copyNS( self, stack ) :
        '''
        copyNS : (string:src string:dest -> --)
        
        desc:
            copy the src namespace to a new dest
        
        tags:
            custom,namespace
        '''
        dest, src = stack.pop2()
        
        if dest in ['std', self.userNS, ''] :
            raise ValueError, "copyNS: Copying '%s' to '%s' is forbidden!" % (src, dest)
        
        if src not in self.NSdict.keys() :
            raise ValueError, "copyNS: No source namespace called '%s'" % src
        
        self.NSdict[dest] = self.NSdict[src]
    
    def appendNS(self ,stack ) :
        '''
        appendNS : (string:src string:dest -> --)
        
        desc:
            append the src namespace to a dest one
        
        tags:
            custom,namespace
        '''
        dest, src = stack.pop2()
        
        if dest in ['std', ''] :
            raise ValueError, "appendNS: Appending '%s' to '%s' is forbidden!" % (src, dest)
        
        if dest not in self.NSdict :
            self.NSdict[dest] = { '__vars__' : { }, '__links__' : [ ], '__inst__' : { }, '__loadList__' : [ ] }
        
        if src not in self.NSdict.keys() :
            raise ValueError, "appendNS: No namespace called '%s'" % src
        
        funcs = self.NSdict[src].items()
        
        for key,val in funcs :
            if key not in ['__vars__', '__links__', '__inst__', '__loadList__'] :
                self.NSdict[dest][key] = val
            
            elif type(self.NSdict[dest][key]) == DictType :
                    self.NSdict[dest][key].update( val )
            
            else :
                l = self.NSdict[dest][key] + val
                self.NSdict[dest][key] = reduce(lambda x, y: x if y in x else x + [y], l, [])
    
    def delNS( self, stack ) :
        '''
        delNS : (string:name -> --)
        
        desc:
            Removes the named namespace dictionary
        
        tags:
            custom,namespaces
        '''
        top = stack.pop()
        
        if type(top) == StringType :
            names = [x for x in top.split( "," ) if x != '']
        
        elif type(top) in [ListType, TupleType] :
            names = top
        
        else :
            raise ValueError, "delNS: Expect a string or a list"
        
        for ns in names :
            if ns in ['', self.userNS, 'std', 'user'] :
                continue
            
            if ns in self.NSdict :
                del self.NSdict[ns]
    
    def listNS( self, stack ) :
        '''
        listNS : (-- -> --)
        
        desc:
            Lists the names of the available namespaces
        
        tags:
            custom,namespaces
        '''
        names = self.NSdict.keys()
        names.remove( 'std' )
        names.sort()
        self._printList( names )
    
    def getNS( self, stack ) :
        '''
        getNS : (-- -> list:names)
        
        desc:
            Pushes a list of the names of the available namespaces onto the stack
        
        tags:
            custom,namespaces
        '''
        names = self.NSdict.keys()
        names.remove( 'std' )
        names.sort()
        stack.push( names )
    
    def loadNS( self, stack ) :
        '''
        loadNS : (string:fileName string:nameSpaceName -> --)
        
        desc:
            Loads the named file of definitions into the specified namespace
            If the namespace does not exist it is created
            If the namespace exists it is added to
            
        
        tags:
            custom,namespaces
        '''
        nsName        = stack.pop()
        self.targetNS = nsName
        
        if nsName not in self.NSdict :
            self.NSdict[nsName] = { '__vars__' : { }, '__links__' : [ ], '__inst__' : { }, '__loadList__' : [ ] }
        
        self._load( stack, True, nsName )
        self.targetNS = ''
    
    def wordsNS( self, stack ) :
        '''
        wordsNS : (string:nsName -> --)
        
        desc:
            Displays on the console the names of all words in a given namespace
            Note: namespace name may be of the form: nsName1,nsName2,...  (e.g. 'test,flow)
                  or a list  (e.g. ['test 'flow] list)
        
        tags:
            custom,namespaces,console
        '''
        top = stack.pop()
        
        if type(top) == StringType :
            nsNames = [x for x in top.split(",") if x != '']
        
        elif type(top) in [ListType, TupleType] :
            nsNames = top
        
        else :
            raise ValueError, "functionsNS: Expect a string or list"
        
        for nsName in nsNames :
            if nsName in self.NSdict :
                keys = self.NSdict[nsName].keys()
                keys.sort()
                
                if '__vars__' in keys :
                    keys.remove( '__vars__' )
                    keys.remove( '__links__' )
                    keys.remove( '__inst__' )
                    keys.remove( '__loadList__' )
                
                print colored("For namespace %s:" % nsName, 'green' )
                self._printList( keys )
            
            else :
                print colored( "No namespace called '%s'" % nsName, 'green' )
    
    def purgeNS( self, stack ) :
        '''
        purgeNS : (string:nsNames -> --)
        
        desc:
            Removes all definitions from the namespace
            Note: nsNames may be of the form nsName1,nsName2,nsName3,...  (e.g. 'geometry,flow)
                  or a list (e.g. ['geometry 'flow] list)
        
        tags:
            custom,namespaces
        '''
        names = stack.pop().split( "," )
        
        if type(names) == StringType :
            items = [x for x in names.split(",") if x != '']
        
        elif type(name) in [ListType, TupleType] :
            items = names
        
        else :
            raise ValueError, "purgeNS: Expect a string or list"
        
        for ns in items :
            if ns in ['', 'std'] :
                continue
            
            if ns in self.NSdict :
                self.NSdict[ns] = { }
    
    def focusNS( self, stack ) :
        '''
        focusNS : (string:name -> --)
        cd      : (string:name -> --)
        
        desc:
            Changes the working (active) namespace to the one given by
            the string on top of the stack
        
        tags:
            custom,namespaces
        '''
        name = stack.pop()
        
        if type(name) != StringType :
            raise ValueError, "focusNS: New target namespace name must be a string"
        
        if name not in self.NSdict :
            raise ValueError, "focusNS: No namespace called '%s'" % name
        
        self.userNS = name
    
    def showUserNS( self, stack ) :
        '''
        showUserNS : (-- -> --)
        pwd        : (-- -> --)
        
        desc:
            pushes the current user namespace onto the stack
        
        tags:
            custom,namespaces
        '''
        print colored( "  " + self.userNS, 'green' )
    
    def getUserNS( self, stack ) :
        '''
        getUserNS : ( 'A -> 'A string:namespace)
        
        desc:
            pushes the name of the currently active namespace onto the stack
        
        tags:
            custom,namespaces
        '''
        stack.push( self.userNS )
    
    def linkToNS( self, stack ) :
        '''
        linkToNS : (string:namespaceName -> --)
        ln       : (string:namespaceName -> --)
        
        desc:
            appends the namespace name on top of the stack to the active namespace list
            Note: name may be of the form: nsName1,nsName2,...  (e.g. 'math,geometry)
                  or a list (e.g. ['math 'shuffle] list)
        
        tags:
            custom,namespaces
        '''
        top = stack.pop()
        
        if type(top) == StringType :
            names = [x for x in top.split(",") if x != '']
        
        elif type(top) in [ListType, TupleType] :
            names = top
        
        else :
            raise ValueError, "appendNS: Expect a string or a list"
        
        for name in names :
            if name == self.userNS :
                continue
            
            if name not in self.NSdict :
                raise ValueError, "appendNS: No namespace called '%s'" % name
        
            self.NSdict[self.userNS]['__links__'].append( name )
    
    def unlinkNS( self, stack ) :
        '''
        unlinkNS : (string:name -> --)
        
        desc:
            removes the namespace whose name is on top of the stack
            from the list of active namespaces associated with the
            current user's active namespace. The name may be of the form
            'name1,name2,... or a list of names
        
        tags:
            custom,namespaces
        '''
        top = stack.pop()
        
        if type(top) == StringType :
            names = [x for x in top.split(",") if x != '']
        
        elif type(top) in [ListType, TupleType] :
            names = top
        
        else :
            raise ValueError, "unlinkNS: Invalid namespace name"
        
        for name in names :
            if name in ['std', self.userNS, 'user', ''] :
                continue
            
            if name not in self.NSdict :
                continue
            
            if name in self.NSdict[self.userNS]['__links__'] :
                self.NSdict[self.userNS]['__links__'].remove( name )
    
    def removeWordNS( self, stack ) :
        '''
        removeWordNS : (string:word string:namespace -> --)
        
        desc:
            removes the word(s) from the specified namespace
            Note: the word may be of the form word1,word2,...  (e.g. 'dupd,swapd)
                  or a list  (e.g. ['dupd 'swapd] list)
        
        tags:
            custom,namespaces
        '''
        ns, words = stack.pop2()
        
        if type(words) == StringType :
            names = [x for x in words.split(",") if x != '']
        
        elif type(words) in [ListType, TupleType] :
            names = words
        
        else :
            raise ValueError, "removeWordNS: Expect a string or a list for words"
        
        if ns not in self.NSdict :
            raise ValueError, "removeWordNS: No namespace called '%s'" % ns
        
        for word in names :
            if word in ['__vars__', '__links__','__inst__', '__loadList__', ''] :
                continue
            
            if word in self.NSdict[ns] :
                del self.NSdict[ns][word]
    
    def showLinkedNS( self, stack ) :
        '''
        showLinkedNS : (-- -> --)
        
        desc:
            lists all the active namespaces (those linked to the user's current namespace)
        
        tags:
            custom,namespaces
        '''
        print colored("Linked namespaces:", 'green')
        self._printList( self.NSdict[self.userNS]['__links__'] )
    
    def purgeLinksNS( self, stack ) :
        '''
        purgeLinksNS : (-- -> --)
        
        desc:
            removes all links from the active user namespace
        
        tags:
            custom,namespaces
        '''
        self.NSdict[self.userNS]['__links__'] = []


class CatStack:
    '''
    Implements the main stack for the Cat language
    Implements a "parser" for input lines
    Implements eval function
    Implements a variety of stack manipulation functions
    '''
    def _collectFunction( self, line, open='[', close=']' ) :
        '''
        returns the string enclosed between the open and close delimiters
        
        :param line: the string to be analyzed
        :type line: string
        :param open: the opening delimiter
        :type open: string
        :param close: the closing delimiter
        :type close: string
        :rtype: string
        '''
        buf   = ""
        count = 0
        
        while line :
            c = line[0]
            
            if c == open :
                count += 1
                buf   += c
                
            elif c == close :
                buf   += c
                count -= 1
                
                if count == 0 :
                    return buf, line[1:]
            
            else :
                buf += c
                
            line = line[1:]
        
        return buf, line.lstrip()
    
    def __init__( self, stack=[], funcs={} ) :
        '''
        Initialize the stack and define a bunch of regular expressions
        
        :param stack: an initial stack (default: [])
        :type stack: list
        :param funcs: an initial collection of user-defined functions (default: {})
        :type funcs: dictionary
        :rtype: none
        '''
        self.stack       = stack
        self.funcs       = Functions( funcs )
        self.undoStack   = [ ]
        self.parseInt    = re.compile( r'^0\((?P<base>\d+)\)(?P<value>.*)$' )
        self.parseFloat  = re.compile( r'(?P<value>[+-]?\d*\.\d+([eE][+-]?\d+)?)$' )
        self.parseDefine = re.compile( r'define\s*(?P<name>\S+)\s*{(?P<definition>[^}]*)}' )
        self.parseModule = re.compile( r'(\w+)([.]\w+)+' )
        self.parseDef    = re.compile( r'define\s+(?P<name>\S+)\s*(?P<effect>:\s*\(.*\))?\s*(?P<desc>\{\{.*\}\})?\s*{(?P<definition>[^}]*)}', re.DOTALL )
        self.findDeps    = re.compile( r'deps:\s*(\S+)' )
    
    def define( self, line, ns='' ) :
        """If a line starts with 'define', then it's a function declaration"""
        match = self.parseDef.match( line )
        
        if not match:
            raise Exception, 'expect functions of the form "define name (: effect)? {{description}}? {definition}"'
        
        else:
            name, effect, desc, definition = match.groups()
            effect = effect if effect else ' : none'
            desc   = desc.strip( "{}" ) if desc else "  none"
            doc    = "  %s %s\n\n%s" % (name, effect, desc)
            
            # look for dependencies (e.g. for word abba we would have deps:abab,aba
            # or just deps:abab as abab has deps:aba)
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
                        
            self.funcs.setFunction( name, list(self.gobble(definition)), doc, ns )
    
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
                if instring :
                    buff += char
                
                else :
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

    def eval( self, expression ) :
        """Evaluate the given expression. This is the workhorse."""
        global traceFlag
        
        # What have we been given?
        if type(expression) == StringType :
            if expression.strip().startswith( 'define ' ) :
                self.define( expression )
                return self.stack
            
            # Not a 'define' but a string containing instructions
            atoms = self.gobble( expression )
        
        elif type(expression) in [FunctionType, LambdaType] :
            # have something that requires immediate execution (e.g. a 'quote')
            expression()
            return self.stack
        
        else :
            # A list of instructions - internally a function.
            atoms = expression

        getFunction = self.funcs.getFunction
        
        for atom in atoms :
            if traceFlag :
                if not self.stack:
                    state = '_empty_'
                
                else:
                    state = ' '.join(map(repr, self.stack))
                
                print colored('stack: %s' % state, 'red' )
                print colored("atom: %s" % atom, 'red' )
            
            # check for quoted string
            if type( atom ) == StringType and atom.startswith( '"' ) :
                    self.push( atom.strip('"') )
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
                            
                            if type(args) == StringType and args.startswith("[") :
                                args = eval( args )
                            
                            if type(args) not in [ListType, TupleType] :
                                # insert single argument into a tuple
                                arg = (args,)
                            
                            else :
                                arg = args
                            
                            # evaluate the module-based function or method
                            if is_inst :
                                cmd = eval( atom, globals(), self.funcs.NSdict[ns]['__inst__'])
                                self.push( cmd(*arg) )
                            
                            else :
                                cmd = eval(atom, sys.modules)
                                self.push( cmd(*arg) )
                        
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

    def popn( self, n ) :
        '''
        Returns the top n objects on the stack as a list
        :param n: the number of objects to return (popn(1) == pop())
        :type n: integer
        :rtype: list
        '''
        if n == 0 :
            return []
        
        try :
            return [self.stack.pop() for x in range(n)]
        
        except :
            raise IndexError, "popn(%d): Too few items on stack" % n

    def popall( self ) :
        '''Returns all of the elements of a stack as a list'''
        all = self.stack
        all.reverse()
        self.stack = []
        return all

    def clear( self ) :
        '''clears the stack of all elements'''
        self.stack = []
    
    def length( self ) :
        '''Returns the depth of the stack (i.e. number of elements in it)'''
        return len( self.stack )
    
    def clearTo( self, n ) :
        '''
        Clears the stack to a specified depth
        :param n: the number of earlier elements to retain
        :type n: integer
        :rtype: none
        '''
        sl = len( self.stack )
        
        if sl <= n :
            return
        
        else :
            self.popn( sl - n )
    
    def __str__(self):
        """Return a string representation of the stack"""
        if not self.stack:
            state = '_empty_'
        
        else:
            state = ' '.join( map(str, self.stack) )
        
        return '===> %s' % state
    

if __name__ == '__main__': 
    import traceback
    
    def runtests() :
        cs = CatStack()
        e  = cs.eval
    
        tests = (
            # List of ('input expression', [expected stack])
            ('123 0b1010 0xff 017 0(3)12 0(11)2a -3.1415', [123, 10, 255, 15, 5, 32, -3.1415]),
            ('clear 3 5 +', [8]),
            ('10 9 -', [8, 1]),
            ('2 3 *', [8, 1, 6]),
            ('20 10 /', [8, 1, 6, 2]),
            ('+ + +', [17]),
            ('3 %/', [5, 2]),
            ('**', [25]),
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
            ('clear 3 n dup count', [[0, 1, 2], [0, 1, 2], 3]),
            ('clear 3 n head', [0]),
            ('clear 3 n first', [[0, 1, 2], 0]),
            ('clear 3 n tail', [[1, 2]]),
            ('clear 3 n rest', [[1, 2]]),
            ('clear 3 n rev', [[2, 1, 0]]),
            ('clear "abcde" rev', ["edcba"]),
            ('clear 3 n [] map', [[0, 1, 2]]),
            ('clear 3 n [1 +] map', [[1, 2, 3]]),
            ('clear 5 even 0 even 1 even 8 even', [False, True, False, True]),
            ('clear 6 n [even] filter', [[0, 2, 4]]),
            ('clear 10 9 %', [1]),
            ('clear 10 5 divmod', [2, 0]),
            ('clear', []),
            ('clear 1 ++ 2 --', [2, 1]),
            ('clear 1 2 3 +rot', [3, 1, 2]),
            ('-rot', [1, 2, 3]),
            ('[swap] dip', [2, 1, 3]),
            ('clear "test text" "test" !', []),
            ('"test" @', ["test text"]),
            ('clear test', ["test text"]),
            ('clear 3 2 <<', [12]),
            ('2 >>', [3]),
            ('drop 0b10 0b11 & bin_str', ['0b10']),
            ('drop 0b100 0b010 | bin_str', ['0b110']),
            ('clear 0b110 ~ bin_str', ['0b1']),
            ('drop 0b1 as_bool', [True]),
            ('pop 10 as_float', [10.0]),
            ('as_int', [10]),
            ('drop "123" as_int', [123]),
            ('drop "123.45" as_float', [123.45]),
            ('as_list',[[123.45]]),
            ('uncons', [[], 123.45]),
            ('popd as_string', ['123.45']),
            ('clear bool_type', [BooleanType]),
            ('clear [1 2 3] list', [[1, 2, 3]]),
            ('[4 5 6] list cat', [[1, 2, 3, 4, 5, 6]]),
            ('pop [1 2 3] list 4 cons', [[1, 2, 3, 4]]),
            ('pop 42 [dup inc] [add] compose  "test" !',[42]),
            ('test apply', [85]),
            ('dec', [84]),
            ('2 div', [42]),
            ('3 divmod', [14, 0]),
            ('clear nil empty', [[], True]),
            ('drop 1 cons empty', [[1], False]),
            ('clear 12 eqz', [False]),
            ('drop 0 eqz', [True]),
            ('clear false', [False]),
            ("drop 'abba fetch", []),
            ('1 2 abba', [1, 2, 2, 1]),
            ("clear 'catlang.py file_exists", ['catlang.py', True]),
            ('clear [1 2 3] list first', [[1, 2, 3], 1]),
            ('clear 123 float', [123.0]),
            ('321 cons "is ok?" cons "%f %d %s" format', ['123.000000 321 is ok?']),
            ('pop [1 2 3 4] list 2 get_at', [[1, 2, 3, 4], 3]),
            ('clear 123 hex_str', ['0x7b']),
            ('pop 41 inc', [42]),
            ("pop ['tom 'dick 'harry] list 'dick index_of", [1]),
            ('pop "this is a test string" "a test" index_of', [8]),
            ('drop 3.14 int', [3]),
            ('drop 65534 int_to_byte', [254]),
            ('pop [1 2 3] list list_to_str', ['123']),
            ('pop 7 2 max', [7]),
            ('2 min', [2]),
            ('drop "abc" 3 new_str', ['abcabcabc']),
            ('drop 123 neg', [-123]),
            ('drop nil', [[]]),
            ('drop true not', [False]),
            ('not', [True]),
            ('false or', [True]),
            ('drop 2 3 pair', [[2, 3]]),
            ('drop 3 2 popd', [2]),
            ('drop "1,2,3,4" pyList', [[1, 2, 3, 4]]),
            ('drop 3 [2 mul] 2 repeat', [12]),
            ('drop "Hello world?" "world" "Dolly" replace_str', ['Hello Dolly?']),
            ('drop "abcabc" "b" rindex_of', [4]),
            ('drop [1 2 3 4 3 2] list 3 rindex_of', [4]),
            ('pop [1 2 3 4] 5 2 set_at', [[1, 2, 5, 4]]),
            ('size', [[1, 2, 5, 4], 1]),
            ('clear "abvdegf" str_to_list', [['a', 'b', 'v', 'd', 'e', 'g', 'f']]),
            ('pop "abc def ghi" 4 7 subseq', ['abc def ghi', 'def']),
            ('clear [1 2 3 4 5] list 6 3 swap_at', [[1, 2, 3, 6, 5], 4]),
            ('clear 3 unit', [[3]]),
            ('pop 10 [dup dec] [dup 0 neq] while', [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]),
            ('clear hash_list', [{}]),
            ("'dict !", []),
            ("dict 23 'a hash_set", [{'a': 23}]),
            ("42 'b hash_set", [{'a': 23, 'b': 42}]),
            ("32 'c hash_add", [{'a': 23, 'c': 32, 'b': 42}]),
            ("'c hash_contains", [{'a': 23, 'c': 32, 'b': 42}, True]),
            ("pop 'b hash_get", [{'a': 23, 'c': 32, 'b': 42}, 42]),
            ('pop hash_to_list', [[['a', 23], ['c', 32], ['b', 42]]]),
            ("'hashList !", []),
            ('dict', [{'a': 23, 'c': 32, 'b': 42}]),
            ("clear hashList list_to_hash", [{'a': 23, 'c': 32, 'b': 42}]),
            ('clear [1 2 3 4] list 0 [add] fold', [10]),
            ('clear 0 [1 2 3 4] list [add] foreach', [10]),
            ('typeof int_type eq', [10, True]),
            ('pop typeof float_type eq', [10, False]),
            ("clear 1 [<=] papply 'test !", []),
            ('0 test apply', [True]),
            ('clear 3 test apply', [False]),
            ('clear 42.0 to_int', [42]),
            ('to_bool', [True]),
            ('clear 0 to_bool', [False]),
            ('clear [1 2 3] list [4 5 6] list [mul] bin_op', [[4, 10, 18]]),
            ('clear [2 1 -1] list [-3 4 1] list cross_prod', [[5, 1, 11]]),
            ('clear -23 abs -42.12 abs 6 abs', [23, 42.12, 6]),
            ('clear [1 1 true] list all', [True]),
            ('clear [true false true] list all', [False]),
            ('clear [0 true false] list any', [True]),
            ('clear [0 false 0.0] list any', [False]),
            ('clear 122 chr', ['z']),
            ("clear ['abc, 'def, 'ghi] list 0 enum", [[[0, 'abc,'], [1, 'def,'], [2, 'ghi']]]),
            ("clear ['test 13 45.67] list [hash] map", [[hash('test'), hash(13), hash(45.67)]]),
            ("clear 'z ord", [122]),
            ("clear ['abc 'ghi 'def 'aaa 'bab] list sort", [['aaa', 'abc', 'bab', 'def', 'ghi']]),
            ("clear [1 2 3 4 5] list ['a 'b 'c 'd 'e] list zip", [[[1, 'a'], [2, 'b'], [3, 'c'], [4, 'd'], [5, 'e']]]),
            ("'zipped !", []),
            ('zipped unzip', [[1, 2, 3, 4, 5], ['a', 'b', 'c', 'd', 'e']]),
            ('clear "bob,alice,frank,princess edna,joe,doreen" "," split', [['bob', 'alice', 'frank', 'princess edna', 'joe', 'doreen']]),
            ('"**" join', ['bob**alice**frank**princess edna**joe**doreen']),
            ('clear "abcdef ghi" "" split', [['a', 'b', 'c', 'd', 'e', 'f', ' ', 'g', 'h', 'i']]),
            ('clear 1 2 3 triplet', [[1, 2, 3]]),
            ('clear 1 2 3 4 5 6 6 nTuple', [[1, 2, 3, 4, 5, 6]]),
            ('clear "***end of tests***" "green" writeln', [])
        )
        
        bad = 0
        
        for expression, result in tests:
            value   = e(expression)
            if value != result :
                print colored( "Error: '%s' --> expected: %s got: %s" % (expression, str(result), str(value)), 'red' )
                bad += 1
        
        if not bad :
            print colored( "No errors!!", 'green' )
        
        else :
            print colored( "%d errors" % bad, 'green' )
        
        cs.clear()
        cs.undoStack = []

    cat = CatStack()
    
    if len(sys.argv) > 1 :
        if sys.argv[1] in ( '-e', '--eval' ) :
            cat.eval(' '.join(sys.argv[2:]))
            print cat
        
        elif sys.argv[1] in ( '-r', '--runtests' ) :
            runtests()
    
    else :
        # cat.eval( '"Cat> ", #prompt' )
        print
        print colored( "#words prints a list of built-in Cat words (functions)", 'green' )
        print colored( "'wordName #doc prints documentation for wordName", 'green' )
        print colored( "'wordName #def prints the definition of wordName", 'green' )
        print colored( "Use the word 'quit' to quit the interactive session", 'green' )
        print colored( "The word 'runtests' runs some test code", 'green' )
        print
        
        showStack     = True
        fullErrorInfo = False
        
        while True :
            cat.eval( "global:prompt" )
            line = raw_input( cat.pop() )
            
            if line == "" :
                if showStack :
                    print colored( str(cat), 'blue' )
                
            elif line == 'quit' :
                break
            
            elif line.lower().startswith("showstack") :
                if line.lower().endswith("on") or line.lower().endswith('true') or line.lower().endswith('yes') :
                    showStack = True
                
                else :
                    showStack = False
                
                if showStack :
                    print colored( str(cat), 'blue' )
            
            elif line.lower().startswith("fullerrorinfo") :
                if line.lower().endswith("on") or line.lower().endswith('true') or line.lower().endswith('yes') :
                    fullErrorInfo = True
                
                else :
                    fullErrorInfo = False
            
            elif line.lower() == 'runtests' :
                runtests()
                cat.clear()
            
            else :
                try :
                    cat.eval( line.strip() )
                    
                    if showStack :
                        print colored( str(cat), 'blue' )
                
                except Exception, msg :
                    print colored( msg, 'red' )
                    
                    if fullErrorInfo :
                        for frame in traceback.extract_tb(sys.exc_info()[2]) :
                            fname, lineno, fn, text = frame
                            print colored( "Error in %s on line %d" % (fn, lineno), 'red' )
                    
                    print colored( str(cat), 'blue' )
