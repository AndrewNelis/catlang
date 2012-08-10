
import re
import sys
from types import (
        IntType, FloatType, LongType, StringType, TupleType,
        ListType, FileType, BooleanType, FunctionType)


import defs   # NOQA
from cat.namespace import NameSpace


class Functions:
    """Return a function for a given symbol. Also maintains
    a list of user defined functions."""
    def __init__(self, userfunctions=None):
        """Constructor"""

        if userfunctions is None:
            userfunctions = {}

        # Initial map of symbols to functions
        # (as well as the methods defined on this class)
        self.loadList = []
        self.userNS = 'user'
        self.NSdict = {'std':
                                    {
                                    '=': 'eq',
                                    '!=': 'neq',
                                    '<': 'lt',
                                    '>': 'gt',
                                    '<=': 'lteq',
                                    '>=': 'gteq',
                                    'if': '_if',
                                    '~': '_not',
                                    '!': '_saveVar',
                                    '@': '_fetchVar',
                                    '&': 'bit_and',
                                    '|': 'bit_or',
                                    '~': 'bit_not',
                                    'del': '_del_word',
                                    'type': 'typeof',
                                    'cd': 'focusNS',
                                    'ls': '_udf',
                                    'rm': '_del_word',
                                    'ln': 'linkToNS',
                                    'pwd': 'showUserNS',
                                    '#allDefs': '_loadAllDefs',
                                    '#allWords': '_showAllWords',
                                    '#def': '_dumpdef',
                                    '#dir': '_dir',
                                    '#doc': '_show',
                                    '#dump': '_dumpStack',
                                    '#instance': '_instance',
                                    '#info': '_info',
                                    '#listFiles': '_listDefinitionFiles',
                                    '#load': '_load',
                                    '#prompt': '_newPrompt',
                                    '#reload': '_reload',
                                    '#udf': '_udf',
                                    '#vars': '_showVars',
                                    '#whereis': '_whereis',
                                    '#words': '_words',

                                    '__globals__': {'CatDefs': 'CatDefs/', 'prompt': 'Cat> '},
                                    },
                           'user': {'__vars__': {}, '__links__': [], '__inst__': {}},
                         }

        self.NSdict['user'].update(userfunctions)
        self.NSdict['user'].update(NameSpace.as_dict())

        self.parseDef = re.compile(r'define\s+(\S+)\s*(:\s*\(.*\))?\s*(\{\{.*\}\})?\s*(\{.*\})', re.DOTALL)

        self._checkAliases()

    def _checkAliases(self):
        """
            Moving functions off this object using the @define decorator.

            Want to make sure we haven't moved anything off this object without
            declaring it elsewhere / etc.
        """
        for field, alias in self.NSdict['std'].items():
            if isinstance(alias, str) and not alias.endswith('NS'):
                assert hasattr(self, alias), '%s expects %s on self' % (field, alias)

    def getFunction(self, what):
        """Called by the interpreter to get a function named <what>.
        As a name may be None we return a flag stating whether <what>
        was defined, followed by it's definition.
        """
        if not isinstance(what, basestring):
            return False, None

        # check 'std' namespace first then built-ins
        if what in self.NSdict['std']:
            # A method alias.
            return True, getattr(self, self.NSdict['std'][what])

        elif hasattr(self, what):
            # A named method (a built-in).
            return True, getattr(self, what)

        else:
            # search name spaces: 'user' then linked namespaces
            search = [self.userNS] + self.NSdict[self.userNS]['__links__']

            if '__vars__' in search:
                search.remove('__vars__')
                search.remove('__links__')
                search.remove('__inst__')

            for ns in search:
                if what in self.NSdict[ns]:
                    return True, self.NSdict[ns][what][0]

        return False, None

    def setFunction(self, name, definition, descrip='', ns=''):
        """Called to *define* new functions"""
        if ns == '':
            ns = self.userNS

        self.NSdict[ns][name] = [definition, descrip]

    def isFunction(self, what):
        '''
        Returns True if the argument is defined as a function in
        some user-related namespace; False otherwise
        '''
        if hasattr(self, what):
            return True

        search = ['std', self.userNS] + self.NSdict[self.userNS]['__links__']

        if '__vars__' in search:
            search.remove('__vars__')
            search.remove('__links__')
            search.remove('__inst__')

        for ns in search:
            if what in self.NSdict[ns]:
                return True

        return False

    def getVar(self, what):
        '''
        returns the value associated with user variable named in what from the user's '__var__' dict
        Note that 'what' may be of the form:
            <simple name>
            <namespace>:<simple name>
                <namespace> may also be the special case 'global' to access global variables
        '''
        if what.count(":") == 1:
            ns, var = what.split(":")

            if ns.lower() == 'global':
                if var in self.NSdict['std']['__globals__']:
                    return True, self.NSdict['std']['__globals__'][var]

                else:
                    return False, None

            else:
                if ns in self.NSdict and var in self.NSdict[ns]['__vars__']:
                    return True, self.NSdict[ns]['__vars__'][var]

                else:
                    return False, None

        else:
            search = [self.userNS] + self.NSdict[self.userNS]['__links__']

            for ns in search:
                if what in self.NSdict[ns]['__vars__']:
                    return True, self.NSdict[ns]['__vars__'][what]

            if what in self.NSdict['std']['__globals__']:
                return True, self.NSdict['std']['__globals__'][what]

            else:
                return False, None

    def setVar(self, var, val):
        '''
        stores val into the __vars__ dictionary in some namespace under key name var

        var may take the form:
            <simple name>
            <namespace>:<simple name>
            Note that the namespace 'global' is reserved for saving global variables
        '''
        if var.count(":") == 1:
            ns, var = var.split(":")

            if ns.lower == 'global':
                self.NSdict['std']['__globals__'][var] = val

            else:
                self.NSdict[ns]['__vars__'][var] = val

        else:
            self.NSdict[self.userNS]['__vars__'][var] = val

    def _printList(self, cat, theList, across=5):
        '''Print the elements in theList'''
        if len(theList) == 0:
            cat.output("  _none_", 'green')
            return

        longest = max([len(x) for x in theList])
        i = 0

        for name in theList:
            l = longest + 2 - len(name)
            fragment = "  " + name + " " * l
            cat.output(fragment, 'green')
            i += 1

            if i == across:
                print
                i = 0

        if i > 0:
            print

    # Methods defining functions with invalid python names.
    # They're prefixed with underscores so people don't unintentionally
    # re-define them and so we can identify these when 'defs' is called

    def _if(self, cat):
        '''
        if : (func:true_func func:false_func bool:condition -> any|none)

        desc:
            executes one predicate or another whether the condition is true

        tags:
            level0,control
        '''
        ffalse, ftrue, truth = cat.stack.pop_n(3)

        if truth:
            cat.stack.push(ftrue)

        else:
            cat.stack.push(ffalse)

        self.eval(cat)

    def _dumpStack(self, stack):
        '''
        #dump : (-- -> --)

        desc:
            non-destructively dumps the entire contents of the stack to the console

        tags:
            custom,console,stack
        '''
        stack.output(str(stack), 'green')

    def _show(self, stack):
        '''
        #doc : (string:func_name -> --)

        desc:
            displays documentation for function whose name string is on top of the stack
            A word name may be prefixed with a namespace. E.g. 'shuffle:abba #doc

        tags:
            custom,definitions,methods
        '''
        name = stack.pop().strip('"')

        if name.count(":") == 1:
            ns, name = name.split(":")

            if name in self.NSdict[ns]:
                obj = self.NSdict[ns][name]
                stack.output(obj[1], 'green')
                return

            else:
                raise ValueError("#doc: No documentation for '%s' in '%s'" % (name, ns))

        if name in ['__vars__', '__links__', '__inst__']:
            return

        if name in self.NSdict['std']:
            # get method's doc string
            fcn = getattr(self, self.NSdict['std'][name])
            stack.output(fcn.__doc__, 'green')

        elif hasattr(self, name):
            fcn = getattr(self, name)
            stack.output(fcn.__doc__, 'green')

        else:
            search = [self.userNS] + self.NSdict[self.userNS]['__links__']

            for ns in search:
                if name in self.NSdict[ns]:
                    obj = self.NSdict[ns][name]
                    stack.output(obj[1], 'green')
                    return

            stack.output("No description for " + name, 'red')

    def _load(self, stack, force=False, ns=''):
        '''
        #load : (string:fileName -> --)

        desc:
            Loads the script whose name string is on top of the stack into a namespace

        tags:
            level0,control,system
        '''
        def stripComments(text):
            temp = text.strip()

            if temp == "" or temp.startswith('//') or temp.startswith('#'):
                return ""

            ix = temp.rfind('//')

            if ix > 0:
                temp = temp[:ix]

            return temp

        fileName = stack.pop()

        if type(fileName) != StringType:
            raise Exception("#load: File name must be a string")

        if not force:
            if fileName in self.loadList:
                raise Warning("#load: The file of Cat definitions called '%s' has already been loaded. Skipping it." % fileName)

        if ns == '':
            ns = self.userNS

        fd = open(fileName, 'r')
        buffer = ""
        lineNo = 0
        inDef = False

        for line in fd:
            lineNo += 1
            temp = stripComments(line.strip())

            if temp == "":
                continue

            if not inDef:
                if not temp.startswith("define"):
                    stack.eval(temp)
                    continue

                else:
                    inDef = True

            # must be in a definition (this hack permits 1-line definitions)
            if inDef:
                # consolidate lines of a definition into a single string
                buffer += line  # to preserve original formatting

                # end of function definition?
                if not temp.endswith("}}") and temp.endswith("}"):
                    # parse parts of the string
                    mo = self.parseDef.match(buffer)

                    if not mo:
                        raise ValueError("#load: Bad definition in file %s at line %d" % (fileName, lineNo))

                    # create definition
                    descrip = mo.group(3).strip("{}") if mo.group(3) else ''
                    effect = mo.group(2).strip(" :") if mo.group(2) else ''
                    lines = mo.group(4).strip("{}").split("\n")
                    buf = ""

                    # remove all comments from the definition
                    for temp in lines:
                        temp = stripComments(temp)

                        if temp != "":
                            buf += temp + " "

                    self.setFunction(mo.group(1), list(stack.gobble(buf)), "  %s : %s\n%s" % (mo.group(1), effect, descrip), ns)
                    buffer = ""
                    inDef = False

        self.loadList.append(fileName)
        fd.close()

    def _reload(self, stack):
        '''
        #reload : (string:fileName -> --)

        desc:
            Reloads the script whose name string is on top of the stack

        tags:
            level0,control,system
        '''
        self._load(stack, True)

    def _loadAllDefs(self, stack):
        '''
        #allDefs : (-- -> --)

        desc:
            load all definitions into their corresponding namespaces

        tags:
            custom,namespaces,definitions
        '''
        loadFile = self.NSdict['std']['__globals__']['CatDefs'] + "everything.cat"
        stack.push(loadFile)
        self._load(stack)

    def _dumpdef(self, stack):
        '''
        #def : (string:name -> --)

        desc:
            prints the definition string of the named function to the console
            the function name may be prefixed with a <namespace>: if desired
            Example: 'shuffle:abba #def

        tags:
            custom,console,debugging
        '''
        atom = stack.pop().strip('"')

        if atom.count(":") == 1:
            ns, name = atom.split(":")
            obj = self.NSdict[ns][name]
            stack.output(obj[0], 'green')
            return

        if hasattr(self, atom):
            stack.output("Function %s is a primitive" % atom, 'green')

        else:
            defined, func = self.getFunction(atom)

            if defined:
                stack.output("%s: %s" % (atom, func), 'green')

            else:
                stack.output("Function %s is undefined" % atom, 'red')

    def _instance(self, stack):
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
        cls, args, name = stack.pop_n(3)

        if type(cls) != StringType:
            raise ValueError("#instance: The module.class identifier must be a string")

        if type(name) != StringType:
            raise ValueError("#instance: The instance name must be a string")

        if type(args) == StringType and args.startswith("["):
            args = eval(args)

        if type(args) in [ListType, TupleType]:
            args = str(tuple(args))

        else:
            args = str((args,))

        self.NSdict[self.userNS]['__inst__'][name] = eval("%s%s" % (cls, args), sys.modules)

    def _saveVar(self, stack):
        '''
        ! : (any string:userVarName ->)

        desc:
            saves the value at [-1] to the user symbol table
            with the name provided by the string at [0]

        tags:
            custom,variables,user
        '''
        varName, value = stack.pop_2()

        if self.isFunction(varName):
            stack.push(value)
            raise ValueError("!: User variable '%s' duplicates an existing method" % varName)

        self.setVar(varName, value)

    def _fetchVar(self, stack):
        '''
        @ : (string:userVarName -> val)

        desc:
            pushes the value of the named user-variable onto the stack
            Note: the userVarName by itself (no quotes or @) will push its value onto the stack

        tags:
            custom,variables,user
        '''
        name = stack.pop()
        defined, val = self.getVar(name)

        if defined:
            stack.push(val)

        else:
            raise KeyError("@: No variable called " + name)

    def _showVars(self, stack):
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
        stack.output("User-defined variables in default namespace '%s':" % self.userNS, 'green')
        self._printList(stack, keys)
        keys = self.NSdict['std']['__globals__'].keys()
        keys.sort()
        stack.output("Variables defined in 'globals':", 'green')
        self._printList(stack, keys)
        search = self.NSdict[self.userNS]['__links__']

        # search for variables in linked-in namespaces
        for ns in search:
            keys = self.NSdict[ns]['__vars__'].keys()
            keys.sort()
            stack.output("User-defined variables in namespace '%s':" % ns, 'green')
            self._printList(stack, keys)

    def _dir(self, stack):
        '''
        #dir : (string -> --)

        desc:
            displays the results of applying the Python 'dir' function
            to the argument on top of the stack. Used to examine the content
            of sys.modules.

        tags:
            custom,python,dir
        '''
        if stack.length() == 0:
            arg = ''

        else:
            arg = str(stack.pop())

        lst = eval("dir(eval('%s'))" % arg, sys.modules)
        self._printList(stack, lst, 4)

    def _words(self, stack, showAll=False):
        '''
        words: (-- -> --)

        desc:
            Prints a list of available words to the user's terminal

        tags:
            level2,words
        '''
        stack.output("Built-in (primitive) words:", 'green')

        functions = self.NSdict['std'].keys()

        for method in dir(self):
            if method not in functions and not method.startswith('_'):
                functions.append(method)

        functions.remove('setFunction')
        functions.remove('getFunction')
        functions.remove('isFunction')
        functions.remove('setVar')
        functions.remove('getVar')
        functions.remove('parseDef')
        functions.remove('loadList')
        functions.remove('userNS')
        functions.remove('NSdict')
        functions.sort()
        self._printList(stack, functions)

        if not showAll:
            search = [self.userNS] + self.NSdict[self.userNS]['__links__']

        else:
            search = self.NSdict.keys()
            search.remove('std')

        search.sort()

        for ns in search:
            print
            stack.output("Words defined in '%s' namespace:" % ns, 'green')
            functions = self.NSdict[ns].keys()
            functions.sort()

            if '__vars__' in functions:
                functions.remove('__vars__')
                functions.remove('__links__')
                functions.remove('__inst__')

            self._printList(stack, functions)

        print

    def _showAllWords(self, stack):
        '''
        #allWords : (-- -> --)

        desc:
            Shows all defined words in all namespaces

        tags:
            custom,namespaces,words,functions
        '''
        self._words(stack, True)

    def _info(self, stack):
        '''
        #info : (-- -> --)

        desc:
            lists modules available for use and other bits of useful information

        tags:
            custom,modules
        '''
        keys = sys.modules.keys()
        keys.sort()
        stack.output("**modules: " + str(keys), 'green')
        keys = self.NSdict[self.userNS]['__inst__'].keys()
        keys.sort()
        stack.output("**instances: " + str(keys), 'green')
        keys = self.NSdict[self.userNS]['__vars__'].keys()
        keys.sort()
        stack.output("**user-defined variables: " + str(keys), 'green')

    def _udf(self, stack):
        '''
        Shows all user-defined functions
        '''
        keys = self.NSdict[self.userNS].keys()
        keys.sort()
        keys.remove('__vars__')
        keys.remove('__links__')
        keys.remove('__inst__')
        self._printList(stack, keys)
        print

    def _del_word(self, stack):
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

        if type(top) == StringType:
            words = [x for x in top.split(",") if x != '']

        elif type(top) in [ListType, TupleType]:
            words = top

        else:
            raise ValueError("del_word: expect a string or list")

        for word in words:
            if word in ['__vars__', '__links__', '__inst__']:
                continue

            elif word.count(":") == 1:
                ns, wrd = word.split(":")

                if wrd in ['__vars__', '__links__', '__inst__']:
                    continue

                if ns == 'std':
                    continue

                if ns in self.NSdict and wrd in self.NSdict[ns]:
                    del self.NSdict[ns][word]

            elif word in self.NSdict[self.userNS]:
                del self.NSdict[self.userNS][word]

    def _listDefinitionFiles(self, stack):
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

        if type(path) != StringType:
            raise ValueError("#listFiles: Directory path must be a string")

        fnmap = {}
        path += "*.cat"
        regex = re.compile(r'^\s*define\s+(\S+)')

        for file in iglob(path):
            fd = open(file, 'r')

            for line in fd:
                mo = regex.match(line)

                if mo:
                    funcName = mo.group(1)

                    if funcName in fnmap:
                        stack.output("File %s duplicates function %s" % (file, funcName), 'red')

                    else:
                        fnmap[funcName] = file

            fd.close()

        keys = fnmap.keys()
        keys.sort()
        maxStr = max([len(x) for x in keys]) + 2
        print

        for key in keys:
            akey = key.rjust(maxStr, " ")
            stack.output("    %s -- %s" % (akey, fnmap[key]), 'green')

    def _whereis(self, stack):
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
        source = 'undefined'
        defined = False
        search = self.NSdict.keys()

        for ns in search:
            if theWord in self.NSdict[ns]:
                if ns == 'std':
                    source = "built-in"

                else:
                    source = ns

                defined = True
                break

        if not defined and hasattr(self, theWord):
            source = "built-in"

        elif not defined:
            path = self.NSdict['std']['__globals__']['CatDefs']
            path += "*.cat"

            # escape characters in theWord that are interpreted by "re"
            letters = [x for x in theWord]

            for i in range(len(letters)):
                c = letters[i]

                if c in ".[]{}^$*?()+-|":  # regular expression characters
                    letters[i] = "\\" + c

            theWord = "".join(letters)

            # search the standard definition files
            regex = re.compile(r'^\s*define\s+(%s)' % theWord)
            found = False

            for file in iglob(path):
                if found:
                    break

                fd = open(file, 'r')

                for line in fd:
                    if regex.match(line.strip()):
                        source = file
                        found = True
                        break

                fd.close()

            if not found:
                source = "undefined" % theWord

        stack.output("%s: %s" % (theWord, source), 'green')

    def _newPrompt(self, stack):
        '''
        #prompt : (string:prompt -> --)

        desc:
            Sets the prompt string to the string on top of the stack

        tags:
            console
        '''
        self.NSdict['std']['__globals__']['prompt'] = str(stack.pop())

    # Now begins methods implementing functions with non-conflicting acceptable Python names

    def zip(self, stack):
        '''
        zip : (list list -> list)

        desc:
            creates a list of paired objects from the two lists on
            top of the stack.

        tags:
            custom,lists
        '''
        r, l = stack.pop_2()
        stack.push([list(x) for x in zip(l, r)])

    def unzip(self, stack):
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
        stack.push(list(lst[0]))
        stack.push(list(lst[1]))

    def split(self, stack):
        '''
        split : (string:target string:splitter -> list)

        desc:
            splits a target string into segments based on the 'splitter' string

        tags:
            custom,strings
        '''
        splitter, target = stack.pop_2()

        if type(target) != StringType or type(splitter) != StringType:
            raise ValueError("split: Both arguments must be strings")

        if len(splitter) == 0:
            stack.push([x for x in target])

        else:
            stack.push(target.split(splitter))

    def join(self, stack):
        '''
        join : (list string:connector -> string)

        desc:
            joins together the elements of the list at [-1] using the connector
            string at [0].

        tags:
            custom,strings,lists
        '''
        conn, lst = stack.pop_2()

        if type(conn) != StringType:
            conn = str(conn)

        result = ''

        for item in lst:
            result += str(item) + conn

        stack.push(result.rstrip(conn))

    def count_str(self, stack):
        '''
        count_str : (string:target string:test -> string:target int)

        desc:
            counts the number of non-overlapping occurrences of the test string at [0]
            found in the target string at [-1]

        tags:
            custom,strings
        '''
        test, target = stack.pop_2()

        if type(test) != StringType or type(target) != StringType:
            raise ValueError("count_str: Both target and test objects must be strings")

        stack.push(target)
        stack.push(target.count(test))

    def eq(self, stack):
        """
        eq : (any any -> bool)

        desc:
            returns True if top two items on stack have the same value; otherwise False

        tags:
            level1,comparison"
        """
        a, b = stack.pop_2()
        stack.push(a == b)

    def neq(self, stack):
        """
        neq : (any any -> bool)

        desc:
            returns True if top two items on stack have differning values; otherwise False

        tags:
            level1,comparison"
        """
        a, b = stack.pop_2()
        stack.push(a != b)

    def gt(self, stack):
        """
        gt : (any any -> bool)

        desc:
            returns True if the value at [-1] is greater than the one at [0];
            otherwise False

        tags:
            level1,comparison"
        """
        a, b = stack.pop_2()
        stack.push(b > a)

    def lt(self, stack):
        """
        lt : (any any -> bool)

        desc:
            returns True if the object at [-1] is less than the one at [0];
            otherwise False

        tags:
            level1,comparison"
        """
        a, b = stack.pop_2()
        stack.push(b < a)

    def gteq(self, stack):
        """
        gteq : (any any -> bool)

        desc:
            returns True if the object at [-1] is greater than or equal to the one at [0];
            otherwise False

        tags:
            level1,comparison"
        """
        a, b = stack.pop_2()
        stack.push(b >= a)

    def lteq(self, stack):
        """
        lteq : (any any -> bool)

        desc:
            returns True if the object at [-1] is less than or equal to the one at [0];
            otherwise False

        tags:
            level1,comparison"
        """
        a, b = stack.pop_2()
        stack.push(b <= a)

    def clear(self, cat):
        '''
        clear : (A -> -)

        desc:
            removes all stack entries

        tags:
            level0,stack
        '''
        cat.stack.clear()

    def pop(self, stack):
        '''
        pop : (A any -> A)

        desc:
            removes the top item from the stack

        tags:
            level0,stack"
        '''
        stack.pop()

    def popd(self, stack):
        '''
        pop : (b a -> a)

        desc:
            removes the item at [-1] on the stack

        tags:
            level0,stack"
        '''
        self.swap(stack)
        stack.pop()

    def pair(self, stack):
        '''
        pair : (b a -> [b, a])

        desc:
            makes a list of the top two stack elements

        tags:
            level0,stack"
        '''
        t, n = stack.pop_2()
        stack.push([n, t])

    def drop(self, stack):
        '''
        drop : (b a -> a)

        desc:
            removes the top item from the stack

        tags:
            level0,stack"
        '''
        stack.pop()

    def dup(self, stack):
        '''
        dup : (a -> a a)

        desc:
            duplicate the top item on the stack

        tags:
            level0,stack"
        '''
        stack.push(stack.peek())

    def swap(self, stack):
        '''
        swap : (a b -> b a)

        desc:
            swap the top two items on the stack

        tags:
            level0,stack"
        '''
        a, b = stack.pop_2()
        stack.push((a, b), multi=True)

    def swapd(self, stack):
        '''
        swapd : (c b a -> b c a)

        desc:
            swap the items at [-1] and [-2]

        tags:
            level0,stack"
        '''
        a, b, c = stack.pop_n(3)
        stack.push((b, c, a), multi=True)

    def dupd(self, stack):
        '''
        dupd : (b a -> b b a)

        desc:
            duplicates the item at [-1] leaving item at [0] on top of the stack

        tags:
            level0,stack"
        '''
        a, b = stack.pop_2()
        stack.push((b, b, a), multi=True)

    def eval(self, cat):
        '''
        eval : (func -> (func(A) -> B))

        desc:
            applies a function to the stack (i.e. executes an instruction)

        tags:
            level0,functions"
        '''
        cat.eval(cat.pop())

    def apply(self, stack):
        '''
        apply: (func -> (func(A) -> B))

        desc:
            applies a function to the stack (i.e. executes an instruction)

        tags:
            level0,functions"
        '''
        stack.eval(stack.pop())

    def nil(self, stack):
        '''
        nil : (-> list)

        desc:
            pushes an empty list onto the stack

        tags:
            level0,lists
        '''
        stack.push([])

    def n(self, stack):
        '''
        n : (n -> [0, 1, ... n-1])

        desc:
            using the integer on top of the stack, a list of sequential integers
            is pushed onto the stack according to the action of the standard
            Python range() function

        tags:
            level1,lists
        '''
        rng = range(int(stack.pop()))
#        rng.reverse()
        stack.push(rng)

    def count(self, stack):
        '''
        count : (list -> list int)

        desc:
            returns the number of items in a list

        tags:
            level1,lists
        '''
        stack.push(len(stack.peek()))

    def head(self, stack):
        '''
        head : (list:any -> any)

        desc:
            relaces the list on top of the stack with its first member

        tags:
            level1,lists
        '''
        stack.push(stack.pop()[0])

    def first(self, stack):
        '''
        first : (list:any -> list:any any)

        desc:
            the first member of the list on top of the stack is pushed onto the stack
            the source list is unaltered

        tags:
            level1,lists
        '''
        stack.push(stack.peek()[0])

    def rest(self, stack):
        '''
        rest : (list:any -> list:any)

        desc:
            removes the first member from the list on top of the stack

        tags:
            level1,lists
        '''
        stack.push(stack.pop()[1:])

    def tail(self, stack):
        '''
        tail : (list:any -> list:any)

        desc:
            removes the first member from the list on top of the stack

        tags:
            level1,lists
        '''
        stack.push(stack.pop()[1:])

    def rev(self, stack):
        '''
        rev : (list:obj|string:obj -> reversed_obj)

        desc:
            reverses the order of members of the object on top of the stack.
            The object may be a list or a string

        tags:
            level1,lists
        '''
        val = stack.pop()

        if type(val) == StringType:
            stack.push(val[::-1])

        else:
            val.reverse()
            stack.push(val)

    def map(self, cat):
        '''
        map : (list func -> list)

        desc:
            creates a list from another by transforming each value using the supplied function

        tags:
            level0,lists
        '''
        func, elements = cat.pop_2()
        # Evaluate the function with each of the elements.
        results = []

        # Push the value onto the stack and evaluate the function.
        for element in elements:
            with cat.new_stack([element]):
                cat.eval(func)
                results.extend(cat.stack.to_list())

        cat.push(results)

    def even(self, stack):
        '''
        even : (int -> boolean)

        desc:
            if the integer on top of the stack is even True is pushed onto the stack;
            otherwise False

        tags:
            level0,math,functions
        '''
        stack.push((stack.pop() % 2) == 0)

    def filter(self, cat):
        '''
        filter : ([...] func -> [...])

        desc:
            applies the function on the top of the stack to each element of the list
            immediately below it. If the result of the function is True (or non-zero)
            the corresponding element in the list (the argument to the function) is
            pushed onto a new list. When all elements of the argument list have been
            examined the results list being created is pushed onto the stack.

        tags:
            level0,lists,functions,map
        '''
        func, elements = cat.stack.pop_2()
        results = []

        with cat.new_stack():
            for element in elements:
                cat.stack.push(element)
                cat.eval(func)

                if cat.stack.pop():
                    results.append(element)

        cat.stack.push(results)

    def fold(self, cat):
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
        f, init, a = cat.pop_n(3)

        with cat.new_stack():
            for x in a:
                cat.push(init)
                cat.push(x)
                cat.eval(f)
                init = cat.pop()

        cat.push(init)

    def foreach(self, stack):
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
        f, a = stack.pop_2()

        for x in a:
            stack.push(x)
            stack.eval(f)

    def dip(self, stack):
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
        func, second = stack.pop_2()
        stack.push(func)
        self.eval(stack)
        stack.push(second)

    def cons(self, stack):
        '''
        cons : (list any -> list)

        desc:
            appends an item to the right end of a list

        tags:
            level0,lists
        '''
        t = stack.pop()
        lst = stack.peek()

        if type(lst) == ListType:
            lst.append(t)

        else:
            lst = stack.pop()
            stack.push([lst, t])

    def uncons(self, stack):
        '''
        uncons : (list -> list any)

        desc:
            returns the right end of the list, and the rest of a list

        tags:
            level0,lists
        '''
        x = stack.pop()

        if type(x) in [ListType, TupleType]:
            y = x.pop()
            stack.push(x)
            stack.push(y)

        else:
            stack.push(x)
            raise ValueError("uncons: Argument on top of stack must be a list")

    def size(self, stack):
        '''
        size: (A -> A int)

        desc:
            pushes the size of the stack (i.e. number of items in the stack)
            onto the top of the stack

        tags:
            level0,lists,stack
        '''
        stack.push(stack.length())

    def cat(self, stack):
        '''
        cat : (list list -> list)

        descr:
            concatenates two lists

        tags:
            level0,lists
        '''
        r, l = stack.pop_2()

        if type(r) not in [ListType, TupleType]:
            r = [r]

        if type(l) not in [ListType, TupleType]:
            l = [l]

        stack.push(l + r)

    def get_at(self, stack):
        '''
        get_at : (list int -> list any)

        desc:
            returns the nth item in a list

        tags:
            level1,lists
        '''
        ix = int(stack.pop())
        lst = stack.peek()
        stack.push(lst[ix])

    def set_at(self, stack):
        '''
        set_at : (list 'a int -> list)

        desc:
            sets an item in a list

        tags:
            level1,lists
        '''
        ix, val = stack.pop_2()
        lst = stack.peek()
        lst[int(ix)] = val

    def swap_at(self, stack):
        '''
        swap_at : (list any:value int:index -> list any:swappedOutVal)

        desc:
            swaps an item with an item in the list

        tags:
            level1,lists
        '''
        n = int(stack.pop())
        obj = stack.pop()
        lst = stack.peek()
        x = lst[n]
        lst[n] = obj
        stack.push(x)

    def subseq(self, stack):
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
        end, start = stack.pop_2()
        lst = stack.peek()
        stack.push(lst[int(start): int(end)])

    def true(self, stack):
        '''
        true: (-> bool)

        desc:
            pushes the boolean value True on the stack

        tags:
            level0,boolean"
        '''
        stack.push(True)

    def false(self, stack):
        '''
        false: (-> bool)

        desc:
            pushes the boolean value False on the stack

        tags:
            level0,boolean"
        '''
        stack.push(False)

    def eqz(self, stack):
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
        stack.push(stack.pop() == 0)

    def quote(self, stack):
        '''
        quote: (any -> func)

        desc:
            creates a constant generating function from the top value on the stack

        tags:
            level0,functions"
        '''
        t = stack.pop()
        stack.push(lambda: stack.push(t))

    def compose(self, stack):
        '''
        compose: (func:left func:right -> func)

        desc:
            creates a function by composing (concatenating) two existing functions

        tags:
            level0,functions"
        '''
        f1, f2 = stack.pop_2()
        stack.push(lambda: stack.eval2(f2, f1))

    def empty(self, stack):
        '''
        empty : (list|string -> list|string bool)

        desc:
            pushes True onto the stack if the list or string is empty

        tags:
            level0,lists,strings
        '''
        lst = stack.peek()
        stack.push(len(lst) == 0)

    def unit(self, stack):
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
        stack.push([stack.pop()])

    def repeat(self, stack):
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
        n, f = stack.pop_2()
        n = abs(int(n))

        while n > 0:
            stack.eval(f)
            n -= 1

    def to_int(self, stack):
        '''
        to_int : (any -> int)

        desc:
            coerces any value to an integer

        tags:
            level1,conversion
        '''
        obj = stack.pop()

        if type(obj) in [ListType, TupleType]:
            stack.push(len(obj))

        else:
            stack.push(int(obj))

    def to_str(self, stack):
        '''
        to_str : (any -> str)

        desc:
            coerces any value to a string

        tags:
            level1,conversion
        '''
        stack.push(str(stack.pop()))

    def to_bool(self, stack):
        '''
        to_bool : (any -> bool)

        desc:
            coerces any value to a boolean

        tags:
            level1,conversion
        '''
        stack.push(bool(stack.pop()))

    def write(self, stack):
        '''
        write : (string:text string:color -> --)

        desc:
            outputs the text representation of a value to the console in the specified color

        tags:
            level1,console
        '''
        color, text = stack.pop_2()

        if color == '':
            color = 'black'

        stack.output(text, color)

    def writeln(self, stack):
        '''
        writeln : (string:text string:color -> --)

        desc:
            outputs the text representation of a value to the console in the
            requested color followed by a newline character

        tags:
            level1,console
        '''
        color, text = stack.pop_2()

        if color == '':
            color = 'black'

        lines = text.split("\\n")  # this is curious but it works

        for line in lines:
            stack.output(line, color)   # note absence of final comma

    def neg(self, stack):
        '''
        neg : (nbr -> nbr)

        desc:
            Negates top value.

        tags:
            level1,math
        '''
        arg = stack.pop()

        if type(arg) in [FloatType, IntType, LongType]:
            stack.push(-arg)

        elif type(arg) == BooleanType:
            stack.push(not arg)

        else:
            stack.push(arg)
            raise Exception("neg: Cannot negate %s" % str(arg))

    def papply(self, stack):
        '''
        papply : (any func -> func)

        desc:
            partial application: binds the top argument to the top value in the stack
            E.g. (1 [<=] papply -> [1 <=])

        tags:
            level0,functions
        '''
        self.swap(stack)
        self.quote(stack)
        self.swap(stack)
        self.compose(stack)

    def int_to_byte(self, stack):
        '''
        int_to_byte : (int -> byte)

        desc:
            converts an integer into a byte, throwing away sign and ignoring higher bits

        tags:
            level1,math,conversion
        '''
        val = int(stack.pop())
        stack.push(val & 0377)

    def format(self, stack):
        '''
        format : (list:args string:format -> string)

        desc:
            returns a string as formatted by the format statement on top of the based
            on the argument values in the LIST below the format.
            Uses Python format conventions.

        tags:
            level1,string,format,conversion
        '''
        fmt, vals = stack.pop_2()
        stack.push(fmt % tuple(vals))

    def hex_str(self, stack):
        '''
        hex_str : (int -> string)

        desc:
            converts a number into a hexadecimal string representation.

        tags:
            custom,strings,math,conversion
        '''
        n = int(stack.pop())
        stack.push(hex(n))

    def halt(self, stack):
        '''
        "halt : (A int -> A)

        desc:
            halts the program with an error code by raising an exception

        tags:
            level2,application
        '''
        n = int(stack.pop())
        raise Exception("halt: Program halted with error code: %s" % n)

    def dispatch1(self, stack):
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

        for i in range(len(lst) / 2):
            t = lst[2 * i + 1]
            f = lst[2 * i]

            if t == obj:
                self.eval(f)
                return

        raise Exception("dispatch1: Could not dispatch function")

    def dispatch2(self, stack):
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

        for i in range(len(lst) / 2):
            f = lst[2 * i + 1]
            t = lst[2 * i]

            if t == obj:
                self.eval(f)
                return

        raise Exception("dispatch2: Could not dispatch function")

    def explode(self, stack):
        '''
        explode : (func -> list)

        desc:
            breaks a function up into a list of instructions

        tags:
            level2,functions
        '''
        defined, func = self.getFunction(stack.pop())

        if defined:
            stack.push(func)

        else:
            raise ValueError("explode: Undefined function")

    def throw(self, stack):
        '''
        throw : (any -> --)

        desc:
            throws an exception

        tags:
            level2,control
        '''
        raise Exception("throw: " + str(stack.pop()))

    def try_catch(self, stack):
        '''
        "try_catch : (func func:action -> --)

        desc:
            evaluates a function, and catches any exceptions

        tags:
            level2,control
        '''
        c, t = stack.pop_2()
        old = [] + stack.stack

        try:
            stack.eval(t)

        except Exception, msg:  # pylint: disable=W0703
            stack.stack = old
            stack.output("exception caught", 'red')
            stack.push(msg)
            stack.eval(c)

    def typename(self, stack):
        '''
        typename : (any -> string)

        desc:
            returns the name of the type of an object

        tags:
            level1,types
        '''
        stack.push(type(stack.pop()))

    def typeof(self, stack):
        '''
        typeof : (any -> any type)

        desc:
            returns a type tag for an object

        tags:
            level1,types
        '''
        stack.push(type(stack.peek()))

    def int_type(self, stack):
        '''
        int_type : (-> type)

        desc:
            pushes a value representing the type of an int

        tags:
            level1,types
        '''
        stack.push(IntType)

    def string_type(self, stack):
        '''
        string_type : (-> type)

        desc:
            pushes a value representing the type of a string

        tags:
            level1,types
        '''
        stack.push(StringType)

    def float_type(self, stack):
        '''
        float_type : (-> type)

        desc:
            pushes a value representing the type of a float

        tags:
            level1,types
        '''
        stack.push(FloatType)

    def bool_type(self, stack):
        '''
        bool_type : (-> type)

        desc:
            pushes a value representing the type of a boolean

        tags:
            level1,types
        '''
        stack.push(BooleanType)

    def list_type(self, stack):
        '''
        list_type : (-> type)

        desc:
            pushes a value representing the type of a list

        tags:
            level1,types
        '''
        stack.push(ListType)

    def function_type(self, stack):
        '''
        function_type : (-> type)

        desc:
            pushes a value representing the type of a list

        tags:
            level1,types
        '''
        stack.push(FunctionType)

    def datetime_type(self, stack):
        '''
        datetime_type : (-> type)

        desc:
            pushes a value representing the type of a list

        tags:
            level1,types
        '''
        import datetime
        now = datetime.datetime.now()
        stack.push(type(now))

    def type_eq(self, stack):
        '''
        type_eq : (type type -> bool)

        desc:
            returns true if either type is assignable to the other

        tags:
            level1,types
        '''
        l = stack.stack[-2]
        r = stack.stack[-1]
        stack.push(type(l) == type(r))

    def now(self, stack):
        '''
        now : (-> date_time)

        desc:
            pushes a value representing the current date and time onto the stack

        tags:
            level2,datetime
        '''
        import datetime
        stack.push(datetime.datetime.now())

    def sub_time(self, stack):
        '''
        sub_time : (date_time date_time -> time_span)

        desc:
            computes the time interval between two dates

        tags:
            level2,datetime
        '''
        r, l = stack.pop_2()
        stack.push(l - r)

    def add_time(self, stack):
        '''
        add_time : (date_time time_span -> date_time)

        desc:
            computes a date by adding a time period to a date

        tags:
            level2,datetime
        '''
        r, l = stack.pop_2()
        stack.push(l + r)

    def to_msec(self, stack):
        '''
        to_msec : (time_span -> int)

        desc:
            computes the length of a time span in milliseconds

        tags:
            level2,datetime
        '''
        ts = stack.pop()
        ts = ts.total_seconds() * 1000.0
        stack.push(round(ts, 3))

    def iso_format(self, stack):
        '''
        iso_format : (datetime -> string:iso_date)

        descr:
            returns the ISO formatted date and time string of the datetime on top of the stack

        tags:
            level2,datetime
        '''
        dt = stack.pop()
        stack.push(dt.isoformat())

    def time_str(self, stack):
        '''
        time_str : (time_delta -> string:formatted_time)

        descr:
            returns a formatted time string of the timedelta on top of the stack

        tags:
            level2,datetime
        '''
        td = stack.pop()
        stack.push(str(td))

    def del_var(self, stack):
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

        if type(top) == StringType:
            names = [x for x in top.split(",") if x != '']

        elif type(top) in [ListType, TupleType]:
            names = top

        else:
            raise ValueError("del_var: The variable to be deleted must have a string name or be a list of strings")

        for name in names:
            if name in self.NSdict[self.userNS]['__vars__']:
                del self.NSdict[self.userNS]['__vars__'][name]

    def min(self, stack):
        '''
        min : (a b -> min(a,b))

        desc:
            pushes the minimum of the two arguments on top of the stack.
            Numbers: the smaller number
            Strings: the shorter string
            Lists: the shorter list

        tags:
            level2,math,string,list
        '''
        t, u = stack.pop_2()
        stack.push(min(t, u))

    def max(self, stack):
        '''
        max : (a b -> max(a,b))

        desc:
            pushes the larger of the two arguments on top of the stack.
            Numbers: the larger number
            Strings: the longer string
            Lists: the longer list

        tags:
            level2,math,string,list
        '''
        t, u = stack.pop_2()
        stack.push(max(t, u))

    def new_str(self, stack):
        '''
        new_str : (string:str int:n -> string:new_str)

        desc:
            create a new string on top of the stack from a string and a count

        tags:
            level2,string
        '''
        n, c = stack.pop_2()
        s = eval("'%s' * %d" % (c, n))
        stack.push(s)

    def index_of(self, stack):
        '''
        index_of : (target string:test -> int:index)

        desc:
            returns the index of the starting position of a test string in a target string
            or the index of the test object in a list. Returns -1 if not found.

        tags:
            level2,string
        '''
        tst, tgt = stack.pop_2()

        if type(tgt) in [ListType, TupleType]:
            stack.push(tgt.index(tst))

        else:
            stack.push(tgt.find(tst))

    def rindex_of(self, stack):
        '''
        rindex_of : (target string:test -> int:index)

        desc:
            returns the index of the last position of a test string in a target string
            or the last index of the test object in a list. Returns -1 if not found.

        tags:
            level2,string
        '''
        tst, tgt = stack.pop_2()

        if type(tgt) in [ListType, TupleType]:
            n = len(tgt)
            tgt.reverse()
            ix = tgt.index(tst)

            if ix == -1:
                stack.push(-1)

            else:
                stack.push(n - ix - 1)

        else:
            stack.push(tgt.rfind(tst))

    def replace_str(self, stack):
        '''
        replace_str : (string:target string:test string:replace -> string)

        desc:
            replaces a test string within a target string with a replacement string

        tags:
            level2,string
        '''
        rpl, tst, tgt = stack.pop_n(3)

        if type(rpl) != StringType or type(tst) != StringType or type(tgt) != StringType:
            raise ValueError("replace_str: All three arguments must be strings")

        stack.push(tgt.replace(tst, rpl))

    def str_to_list(self, stack):
        '''
        str_to_list : (string -> list)

        desc:
            explodes the string on top of the stack into a list of individual letters

        tags:
            level2,string,list
        '''
        s = stack.pop()
        stack.push([x for x in s])

    def list_to_str(self, stack):
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

        for item in lst:
            buf += str(item)

        stack.push(buf)

    def list_to_hash(self, stack):
        '''
        list_to_hash : (list -> hash:newDict)

        desc:
            converts a list of pairs to a hash_list (dictionary)
            leaves the new hash list on top of the stack

        tags:
            level2,hash_list,list
        '''
        top = stack.pop()

        if type(top) in [ListType, TupleType]:
            stack.push(dict(top))

        else:
            raise ValueError("list_to_hash: Expect a list on top of the stack")

    def pyList(self, stack):
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

        if type(lst) == StringType:
            if lst[0] in "[(":
                lst = list(eval(lst))

            else:
                lst = eval("[" + lst + "]")

        else:
            lst = [lst]

        stack.push(lst)

    def readln(self, stack):
        '''
        readln : (-> string)

        desc:
            inputs a string from the console
            no conversion of any sort is done
            for a prompt, use write first e.g. "date: " write readln

        tags:
            level1,console
        '''
        line = raw_input("")
        stack.push(line)

    def file_reader(self, stack):
        '''
        file_reader : (string:filePath -> istream)

        desc:
            creates an input stream from a file name

        tags:
            level2,streams
        '''
        fName = stack.pop()

        if fName == StringType:
            stack.push(open(fName, 'r'))

        else:
            raise ValueError("file_reader: File name must be a string")

    def file_writer(self, stack):
        '''
        file_writer : (string:filePath -> ostream)

        desc:
            creates an output stream from a file name

        tags:
            level2,streams
        '''
        fName = stack.pop()

        if fName == StringType:
            stack.push(open(fName, 'w'))

        else:
            raise ValueError("file_writer: File name must be a string")

    def file_exists(self, stack):
        '''
        file_exists : (string:filePath -> string:filePath bool)

        desc:
            returns a boolean value indicating whether a file or directory exists

        tags:
            level2,streams
        '''
        from os import path

        name = stack.peek()

        if type(name) == StringType:
            stack.push(path.exists(name))

        else:
            raise ValueError("file_exists: File name must be a string")

    def temp_file(self, stack):
        '''
        temp_file : (-> fd string:path)

        desc:
            creates a unique temporary file

        tags:
            level2,streams
        '''
        import tempfile

        fd, path = tempfile.mkstemp(suffix='tmp', text=True)
        stack.push((fd, path), multi=True)

    def read_bytes(self, stack):
        '''
        read_bytes : (istream int:nr_bytes -> istream byte_block)

        desc:
            reads a number of bytes into an array from an input stream

        tags:
            level2,streams,string
        '''
        n = stack.pop()
        fd = stack.peek()
        buf = fd.read(n)
        stack.push(buf)

    def write_bytes(self, stack):
        '''
        write_bytes : (ostream byte_block -> ostream)

        desc:
            writes a byte array to an output stream

        tags:
            level2,streams,string
        '''
        buf = stack.pop()
        fd = stack.peek()
        fd.write(buf)

    def close_stream(self, stack):
        '''
        close_stream : (stream ->)

        desc:
            closes a stream

        tags:
            level2,streams
        '''
        fd = stack.pop()

        if type(fd) != FileType:
            stack.push(fd)
            raise ValueError("close_stream: Expect a file descriptor on top of stack")

        fd.flush()
        fd.close()

    # much more i/o and file stuff through "'os.path #import"

    def hash_list(self, stack):
        '''
        hash_list : (-> hash_list)

        desc:
            makes an empty hash list (dictionary)

        tags:
            level2,hash
        '''
        stack.push({})

    def hash_get(self, stack):
        '''
        hash_get : (hash_list any:key -> hash_list any:value)

        desc:
            gets a value from a hash list using a key

        tags:
            level2,hash
        '''
        key = stack.pop()
        dict = stack.peek()

        if key in dict:
            stack.push(dict[key])

        else:
            raise KeyError("hash_get: No hash list entry for key " + str(key))

    def hash_set(self, stack):
        '''
        hash_set : (hash_list any:value any:key -> hash_list)

        desc:
            associates the second value with a key (the top value) in a hash list

        tags:
            level2,hash
        '''
        key, val = stack.pop_2()
        dict = stack.peek()
        dict[key] = val

    def hash_add(self, stack):
        '''
        hash_add : (hash_list any:value any:key -> hash_list)

        desc:
            associates the second value with a key (the top value) in a hash list if the
            key is not already present

        tags:
            level2,hash
        '''
        key, val = stack.pop_2()
        dict = stack.peek()

        if key not in dict:
            dict[key] = val

        else:
            stack.push((key, val), multi=True)
            raise Warning("hash_add: Key already present in hash list. Use 'hash_set' to replace")

    def hash_contains(self, stack):
        '''
        hash_contains : (hash_list any:key -> hash_list bool)

        desc:
            returns true if hash list contains key

        tags:
            level2,hash
        '''
        key = stack.pop()
        dict = stack.peek()
        stack.push(key in dict)

    def hash_to_list(self, stack):
        '''
        hash_to_list : (hash_list -> list)

        desc:
            converts a hash_list to a list of pairs

        tags:
            level2,hash
        '''
        dict = stack.pop()
        stack.push([list(i) for i in dict.items()])

    def as_int(self, stack):
        '''
        as_int : (any -> int)

        desc:
            casts a variant to an int
            same as to_int

        tags:
            level1,conversion
        '''
        obj = stack.pop()
        stack.push(int(obj))

    def as_bool(self, stack):
        '''
        as_bool : (any -> bool)

        desc:
            casts a variant to a bool
            same as to_bool

        tags:
            level1,conversion
        '''
        obj = stack.pop()
        stack.push(bool(obj))

    def as_list(self, stack):
        '''
        as_list : (any -> list)

        desc:
            casts a variant to a list

        tags:
            level1,conversion
        '''
        obj = stack.pop()

        if type(obj) == ListType:
            stack.push(obj)

        elif type(obj) == TupleType:
            stack.push(list(obj))

        else:
            stack.push([obj])

    def as_string(self, stack):
        '''
        as_string : (any -> string)

        desc:
            casts a variant to a string
            same as to_str

        tags:
            level1,conversion
        '''
        obj = stack.pop()
        stack.push(str(obj))

    def as_float(self, stack):
        '''
        as_float : (any -> float)

        desc:
            casts a variant to a float
            same as float

        tags:
            level1,conversion
        '''
        obj = stack.pop()
        stack.push(float(obj))

    def fetch(self, stack):
        '''
        fetch  : (string:word -> --)

        desc:
            fetches and loads into the user's workspace the standard definition of the
            word on top of the stack. The "word" may be of the form 'word1,word2,word3,...
            (e.g. 'test,other) or a list (e.g. ['test 'other] list)
            The words may also be prefixed by <namespace>:  (e.g. 'core:modn)

        tags:
            extension,word,define
        '''
        from glob import iglob

        parseDeps = re.compile(r'.*deps:\s*(\S+)', re.DOTALL)
        theWord = stack.pop()

        if type(theWord) == StringType:
            words = [x for x in theWord.split(",") if x != '']

        elif type(theWord) in [ListType, TupleType]:
            words = theWord

        search = self.NSdict.keys()
        search.remove('std')
        search.remove(self.userNS)

        for word in words:
            if word == '':
                continue

            # make sure its is not a standard method
            if hasattr(self, word):
                continue

            # look first in the namespaces, checking first for a special form
            if word.count(":") == 1:
                # special form: <namespace>:<word>
                ns, func = word.split(":")

                if ns in self.NSdict:
                    if func in self.NSdict[ns]:
                        self.NSdict[self.userNS][func] = self.NSdict[ns][func]
                        found = True
                        # have to take care of any dependencies
                        doc = self.NSdict[self.userNS][func][1]
                        mo = parseDeps.match(doc)

                        if mo:
                            deps = mo.group(1).split(",")

                            for dep in deps:
                                stack.push(dep)
                                self.fetch(stack)
                        break

                    else:
                        raise ValueError("fetch: No word called '%s' in namespace '%s'" % (func, ns))

                else:
                    raise ValueError("fetch: No namespace called '%s'" % ns)

            else:
                # not a special form, search namespaces
                found = False

                for ns in search:
                    if ns in self.NSdict[ns]:
                        self.NSdict[self.userNS][word] = self.NSdict[ns][word]
                        found = True
                        # have to take care of any dependencies
                        doc = self.NSdict[self.userNS][word][1]
                        mo = parseDeps.match(doc)

                        if mo:
                            deps = mo.group(1).split(",")

                            for dep in deps:
                                stack.push(dep)
                                self.fetch(stack)
                        break

            # not in a namespace?
            if not found:
                # not present in the name space dictionaries, search the standard definition files
                path = self.NSdict['std']['__globals__']['CatDefs']
                path += "*.cat"

                # escape characters in theWord that are interpreted by "re"
                letters = [x for x in word]

                for i in range(len(letters)):
                    c = letters[i]

                    if c in ".[]{}^$*?()+-|":  # regular expression characters
                        letters[i] = "\\" + c

                theWord = "".join(letters)
                expression = ""

                # search the standard definition files
                regex = re.compile(r'^\s*define\s+(%s)' % theWord)
                inDef = False

                for file in iglob(path):
                    if inDef:
                        break

                    fd = open(file, 'r')

                    for line in fd:
                        temp = line.strip()

                        if temp == "":
                            continue

                        if temp.startswith("//") or temp.startswith("#"):
                            continue

                        # look for line starting with "define"
                        if not inDef and regex.match(temp):
                            inDef = True

                        if inDef:
                            ix = line.rfind("//")

                            if ix > 0:
                                line = line[:ix]

                            expression += line

                            if not temp.endswith("}}") and temp.endswith("}"):
                                break

                    fd.close()

                if inDef:
                    stack.define(expression)

                else:
                    raise ValueError("fetch: No definition can be found for " + word)

    def bin_str(self, stack):
        """
        bin_str : (int -> string)

        desc
            Pushes the binary string representation of the number on top of the stack
            onto the stack

        tags:
            level2,strings,math,conversion
        """
        stack.push(bin(int(stack.pop())))

    def oct_str(self, stack):
        """
        oct_str : (int -> string)

        desc
            Pushes the octal string representation of the number on top of the stack
            onto the stack

        tags:
            string,conversion
        """
        stack.push(oct(int(stack.pop())))

    def bit_and(self, stack):
        '''
        &       : (int int -> int)
        bit_and : (int int -> int)

        desc:
            performs bit-wise logical and on top two stack elements

        tags:
            custom,math
        '''
        r, l = stack.pop_2()
        stack.push(int(l) & int(r))

    def bit_or(self, stack):
        '''
        |      : (int int -> int)
        bit_or : (int int -> int)

        desc:
            performs bit-wise logical or on top two stack elements

        tags:
            custom,math
        '''
        r, l = stack.pop_2()
        stack.push(int(l) | int(r))

    def bit_not(self, stack):
        '''
        ~ : (int -> int)
        bit_not : (int -> int)

        desc:
            performs bit-wise logical negation on top stack element as an integer

        tags:
            custom,math
        '''
        def bitLen(anInt):
            length = 0

            while anInt:
                anInt >>= 1
                length += 1

            return length

        n = int(stack.pop())
        length = bitLen(n)
        value = ~n & (2 ** length - 1)
        stack.push(value)

    def cross_prod(self, stack):
        '''
        cross_prod : (list:nbr list:nbr -> list:nbr)

        desc:
            computes the standard 3-D vector cross product

        tags:
            level1,vectors
        '''
        r, l = stack.pop_2()

        if len(l) != len(r) or len(l) > 3 or len(r) > 3:
            raise ValueError("cross_prod: Both vectors must each be of length 3")

        a1, a2, a3 = l
        b1, b2, b3 = r
        c = [a2 * b3 - b2 * a3, a3 * b1 - b3 * a1, a1 * b2 - b1 * a2]
        stack.push(c)

    def powers(self, stack):
        '''
        powers : (int:base int:max_exponent -> list)

        desc:
            pushes a list of powers of the base onto the stack in descending order of exponent.
            E.g. x 3 powers -> [x**3, x**2, x**1, x**0] for some value x

        tags:
            custom,math,polynomials
        '''
        n, x = stack.pop_2()

        if type(n) not in [IntType, LongType]:
            raise ValueError("powers: Exponent must be an integer")

        if type(x) not in [IntType, LongType, FloatType]:
            raise ValueError("powers: Base must be a number")

        l = [x ** i for i in range(n + 1)]
        l.reverse()
        stack.push(l)

    def poly(self, stack):
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
        x, a = stack.pop_2()

        n = len(a) - 1
        p = a[n]

        for i in range(1, n + 1):
            p = p * x + a[n - i]

        return p

    def bin_op(self, cat):
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
        f, r, l = cat.pop_n(3)
        if len(l) != len(r):
            raise ValueError("bin_op: Lists must be of the same length")

        result = []

        with cat.new_stack():

            for li, ri in zip(l, r):
                cat.push(li)
                cat.push(ri)
                cat.eval(f)

                if cat.length() > 0:
                    result.append(cat.pop())
                else:
                    result.append(None)

        cat.push(result)

    def getWords(self, stack):
        '''
        getWords : (-> list:names)

        desc:
            returns a list of words defined in the current user namespace

        tags:
            custom,words,user
        '''
        keys = self.NSdict[self.userNS].keys()
        keys.remove('__vars__')
        keys.remove('__links__')
        keys.remove('__inst__')

        if len(keys) == 0:
            stack.push([])

        else:
            stack.push(keys)

    def help(self, stack):
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

        if not isinstance(name, basestring):
            raise ValueError("help: Expect a string on the stack")

        # check for user-specified namespace and word
        if name.count(":") == 1:
            ns, name = name.split(":")

            if name in self.NSdict[ns]:
                obj = self.NSdict[ns][name]
                stack.output(obj[1], 'green')
                stack.output(obj[0], 'green')
                return

            else:
                raise ValueError("help: No help available for '%s' in '%s'" % (name, ns))

        # check for built-in or user-defined
        if name in self.NSdict['std']:
            fcn = getattr(self, self.NSdict['std'][name])
            stack.output(fcn.__doc__, 'green')
            stack.output('\tbuilt-in', 'green')
            return

        elif hasattr(self, name):
            fcn = getattr(self, name)
            stack.output(fcn.__doc__, 'green')
            stack.output('\tbuilt-in', 'green')
            return

        search = [self.userNS] + self.NSdict[self.userNS]['__links__']

        for ns in search:
            if name in self.NSdict[ns]:
                obj = self.NSdict[ns][name]
                stack.output(obj[1], 'green')
                stack.output(obj[0], 'green')
                return

        # must be a module -- try Python help()
        search = [self.userNS] + self.NSdict[self.userNS]['__links__']
        inst, _ = name.split(".", 1)

        for ns in search:
            if inst in self.NSdict[ns]['__inst__']:
                name = eval(name, sys.modules, self.NSdict[ns]['__inst__'])
                break

        help(name)
