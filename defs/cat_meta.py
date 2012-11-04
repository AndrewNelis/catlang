# meta

from cat.namespace import *
import sys,os,re
from sets import Set
from fnmatch import fnmatch
from cat_tagExpr import TagExpr

ns      = NameSpace()
mapTags = { }
letters = Set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")

@define(ns, 'doc')
def show_doc( cat ) :
    '''
    doc : (string:function_name -> --)
    
    desc:
        Displays documentation for function (word) whose name string is on top of the stack.
        A word name may be prefixed with a namespace. E.g. 'shuffle:abba doc
        function_name: the word for which to fetch documentation
        
        Example: 'doc doc
    tags:
        meta,definitions,methods,word,documentation,display,doc
    '''
    name = cat.stack.pop().strip( '"' )
    
    if name.count(":") == 1 :
        ns, name = name.split(":")
        
        if not cat.ns.isNS(ns) :
            raise ValueError, "doc: No namespace called '%s'" % ns
        
        else :
            defined, obj, _ = cat.ns.getWord( name, ns )
            
            if defined :
                cat.output( obj[1], cat.ns.info_colour )
                return
            
            else :
                raise ValueError, "doc: No documentation for '%s' in '%s'" % (name, ns)
    
    defined, obj, _ = cat.ns.getWord( name )
    
    if defined :
        cat.output( obj[1], cat.ns.info_colour )
    
    else :
        cat.output( "doc: No documentation for " + name, cat.ns.info_colour )

@define(ns, 'def')
def dumpdef( cat ) :
    '''
    def : (string:name -> --)
    
    desc:
        Displays the definition string of the named function to the console
        The function name may be prefixed with a '<namespace>:' if desired.
        name: the name of the word whose definition is to be displayed
        
        Example: 'shuffle:abba def
    tags:
        custom,console,debugging,word,definition,display
    '''
    atom = cat.stack.pop().strip( '"' )
    
    if atom.count(":") == 1 :
        ns, name = atom.split(":")
        
        if cat.ns.isNS(ns) :
            defined, func, _ = cat.ns.getWord(name, ns)
        
        else :
            raise ValueError, "def: Namespace in '%s' is undefined" % atom
    
    else :
        defined, func, _ = cat.ns.getWord( atom )
    
    if defined :
        if callable(func) :
            cat.output( "Function %s is a primitive" % atom, cat.ns.info_colour )
        
        else :
            cat.output( "%s: %s" % (atom, func[0]), cat.ns.info_colour )
    
    else :
        cat.output( "Function %s is undefined" % atom, cat.ns.config.get('display', 'error') )

@define(ns, 'info')
def info( cat ) :
    '''
    info : (string:namespace_name -> --)
    
    desc:
        Lists modules available for use and other bits of useful information
        for the specified namespace.
        namespace_name: the name of the namespace to be examined. To examine
            the system namespace use 'sys' as the name.
        
        Example: 'sys info
    tags:
        modules,words,instances,variables,links,files,info,modules
    '''
    if cat.stack.length() == 0 :
        nsName = cat.ns.getUserNS()
    
    else :
        nsName = cat.stack.pop()
    
    i_c = cat.ns.info_colour
    
    # sys.modules
    if nsName == 'sys' :
        keys   = sys.modules.keys()
        keys.sort()
        cat.output( "**sys.modules:", i_c )
        cat.output( cat.ns._formatList( keys, across=3), i_c )
        words = cat.ns.builtinWords()
        words.sort()
        cat.output( "**Standard (built-in) words:", i_c )
        cat.output( cat.ns._formatList(words), i_c )
        vars = cat.ns._nsDict['std'].allVarNames()
        vars.sort()
        cat.output( "**Global variables:", i_c )
        cat.output( cat.ns._formatList(vars), i_c )

    else :    
        # words
        keys = cat.ns.allWordNames( nsName )
        keys.sort()
        cat.output( "**Words defined in '%s':" % nsName, i_c )
        cat.output( cat.ns._formatList(keys, across=3), i_c )
        
        # variable names
        keys = cat.ns.allVarNames( nsName)
        keys.sort()
        cat.output( "**Variables defined in '%s':" % nsName, i_c )
        cat.output( cat.ns._formatList(keys), i_c )
        
        # instances
        keys = cat.ns.instNames( nsName )
        keys.sort()
        cat.output( "**Instances defined in '%s':" % nsName , i_c )
        cat.output( cat.ns._formatList(keys), i_c )
        
        # files loaded
        keys = cat.ns.allFileNames( nsName )
        keys.sort()
        cat.output( "**Files loaded '%s':" % nsName, i_c )
        cat.output( cat.ns._formatList(keys), i_c )
        
        # linked namespaces
        keys = cat.ns.getLinks( nsName )
        keys.sort()
        cat.output( "**Namespaces linked to '%s':" % nsName, i_c )
        cat.output( cat.ns._formatList(keys), i_c )

@define(ns, 'vars')
def showVars( cat ) :
    '''
    vars : (-- -> --)
    
    desc:
        Shows names of variables in the user and global symbol tables
        
        Example: vars
    tags:
        user_variables,display,user,variables,console
    '''
    i_c = cat.ns.info_colour
    
    # variables in the default user namespace and in 'globals'
    keys = cat.ns.allVarNames()
    keys.sort()
    cat.output( "User-defined variables in default namespace '%s':" % cat.ns.getUserNS(), i_c )
    cat.output( cat.ns._formatList(keys), i_c )
    keys = cat.ns.allVarNames( 'std' )
    keys.sort()
    cat.output( "Variables defined in 'globals':", i_c )
    cat.output( cat.ns._formatList(keys), i_c )
    search = cat.ns.getLinks()
    
    # search for variables in linked-in namespaces
    for ns in cat.ns.getLinks() :
        keys = cat.ns.allVarnames( ns )
        keys.sort()
        cat.output( "User-defined variables in linked-in namespace '%s':" % ns, i_c )
        cat.output( cat.ns._formatList(keys), i_c )

@define(ns, 'dir')
def catDir( cat ) :
    '''
    dir : ( string:module_name -> --)
    
    desc:
        Displays the results of applying the Python 'dir' function
        to the argument on top of the stack. Usually used to examine the content
        of sys.modules or the contents of a class
        module_name: the name of the module (or class) whose functions (methods)
                     are to be displayed
        
        Example: 'math dir
    tags:
        python,dir,module,class,function,method
    '''
    if cat.stack.length() == 0 :
        arg = ''
    
    else :
        arg = str( cat.stack.pop() )
    
    # the name may be an unqualified instance or module name
    defined, where = cat.ns.isInst( arg )
    
    if defined :
        lst = eval( "dir(eval(%s))" % arg + ".__class__", sys.modules, cat.ns.allInst() )
    
    else :
        lst = eval("dir(eval('%s'))" % arg, sys.modules )
    
    cat.output( cat.ns._formatList(lst, 4), cat.ns.info_colour )

@define(ns, 'show_words')
def words( cat, showAll=False ) :
    '''
    show_words: (-- -> --)
    
    desc:
        Displays the names of available words to the user's terminal
        
        Example: show_words
    tags:
        words,display,console
    '''
    i_c   = cat.ns.info_colour
    words = cat.ns.builtinWords()
    words.sort()
    cat.output( "Standard (built-in) words:", i_c )
    cat.output( cat.ns._formatList(words), i_c )
    
    if not showAll :
        words = cat.ns.allWordNamesInNS( None )
        words.sort()
        cat.output("\nAll words in '%s'" % cat.ns.getUserNS(), i_c )
        cat.output( cat.ns._formatList(words), i_c )
    
    else :
        wordList = cat.ns.allDefinedWords()
        
        for words in wordList :
            cat.output( "\nWords defined in namespace '%s':" % words[0], i_c )
            words = words[1:]
            words.sort()
            cat.output( cat.ns._formatList(words), i_c )
    
    cat.output( "" )

@define(ns, 'all_words')
def showAllWords( cat ) :
    '''
    allWords : (-- -> --)
    
    desc:
        Shows all defined words in all namespaces
        
        Example: all_words
    tags:
        namespaces,words,functions
    '''
    words( cat, True )

@define(ns, 'find_words')
def find_words( cat ) :
    '''
    find_words : (string:regex -> --)
    
    desc:
        Display the names of all words whose names satisfy a regular expression
        regex: the regular expression
        
        Example: '.*_ns$ find_words --> displays all words ending in NS
    tags:
        words,regex,display,console,regular,expression
    '''
    i_c = cat.ns.info_colour
    foundSome = False
    regex     = re.compile( cat.stack.pop() )
    words     = cat.ns.builtinWords()
    selected  = [ x for x in words if regex.match(x) ]
    selected.sort()
    
    if len(selected) > 0 :
        cat.output( "Matching standard (built-in) words:", i_c )
        cat.output( cat.ns._formatList(selected), i_c )
        foundSome = True
    
    wordList = cat.ns.allDefinedWords()
    
    for words in wordList :
        selected = [ x for x in words[1:] if regex.match(x) ]
        
        if len(selected) > 0 :
            cat.output( "\nMatching words defined in namespace '%s':" % words[0], i_c )
            selected.sort()
            cat.output( cat.ns._formatList(selected), i_c )
            foundSome = True
    
    if not foundSome :
        cat.output( "No words match the supplied regex", i_c )
    
    cat.output( "" )

# support functions to create the global tag->word mappings
def _tagMap( cat ) :
    '''Creates the global tag to words mapping'''
    global mapTags
    
    # build the tag-mapping directory if necessary
    mapTags  = { 'universe' : Set() }
    findTags = re.compile( r'tags:\s*(\S+)' )
    
    # first the built-in words
    words = cat.ns.builtinWords()
    
    for word in words :
        wordRef = cat.ns.getWord( word, ns='std' )  # returns (<TF>,(<function>, <documentation>))
        doc     = wordRef[1][1]             # get the documentation
        tags    = findTags.search( doc )    # get the list of tags
        
        # check to see if tags exist
        if tags :
            tags = tags.group( 1 ).split( "," )     # split up the list of tags
            
            # process each tag
            for tag in tags:
                tag = tag.lower()
                
                # tag is either already in dict or needs to be inserted
                if tag not in mapTags:
                    mapTags[tag] = Set( [word] )  # new tag entry
                
                else :
                    mapTags[tag].add( word )    # existing tag entry
                
                mapTags['universe'].add( word ) # the universe is all tags
    
    # now the namespace words
    wordsInNS = cat.ns.allDefinedWords()
    
    for item in wordsInNS :
        if len(item) == 1 : # check for no definitions in the namespace
            continue
        
        nspc = item[0]  # get the namespace name
        
        # this code follows the same logic as for built-in words
        for word in item[1:] :
            wordRef = cat.ns.getWord( word, ns=nspc )
            doc     = wordRef[1][1]
            tags    = findTags.search( doc )
            
            if tags :
                tags = tags.group( 1 ).split( "," )
                word = nspc + ":" + word    # attach a namespace label to the word
                
                for tag in tags:
                    tag = tag.lower()
                    
                    if tag not in mapTags:
                        mapTags[tag] = Set( [word] )
                    
                    else :
                        mapTags[tag].add( word )
                    
                    mapTags['universe'].add( word )

def _globAnalysis( text, dict_ ) :    
    text1   = text.replace("(", " ").replace(")", " ")
    text2   = text1
    globs   = { }
    
    while True :
        text2 = text1
        text1 = text1.replace("  ", " ")
        
        if len(text1) == len(text2) :
            break
    
    items = text1.strip().split( " " )
    
    for glob in items :
        if len(Set(glob) - letters) > 0 :
            tags = []
            
            for key in dict_ :
                if fnmatch(key, glob) :
                    tags.append( key )
            
            globs[glob] = tags
    
    for glob in globs :
        alternatives = globs[glob]
        n            = len( alternatives )
        
        if n > 0 :
            alternatives = reduce( lambda y,x: y + [x] if x not in y else y, alternatives, [] )   # remove duplicates
            clause       = " or ".join( alternatives )
            
            if n > 1 :
                text = text.replace( glob, "(" + clause + ")" )
            
            else :
                text = text.replace( glob, clause )
        
        else :
            raise ValueError, "tag_search: no tags match '%s'" % glob
    
    return text

@define(ns, 'tag_search')
def tag_search( cat ) :
    '''
    tag_search : (string:tag_expression -> --)
    
    desc:
        Displays all words satisfying a search condition based on tags.
        The search expression consists of tag names or tag name 'globs',
        the 'and', 'or', and 'not' operators, and parentheses. The output is a list of words
        satisfying the provided tag expression. Tag glob expressions can contain the
        usual glob characters: *, ?, [, ]. A glob is used to select one or more tags that
        match it. If there are more tags than one the glob is replaced by a list of tags
        in the form: (tag1 or tag2 or tag3...) including the parentheses.
        The selected words have the form: <namespace name>:<word name>
        
        Example: "list and not (display or console)" tag_search
                 "cond* and not display" tag_search
    tags:
        tags,search,words
    '''
    _tagMap( cat )
    
    # Parse the tag expression and evaluate it
    i_c   = cat.ns.info_colour
    texpr = TagExpr( mapTags )
    expr  = cat.stack.pop()
    expr2 = _globAnalysis( expr, mapTags )
    words = texpr.parse( expr2 ) # returns a set (that might be empty), or None
    
    if not words or not list(words) :
        cat.output( "No words matching '%s'" % expr, i_c )
    
    else :
        words = list( words )
        words.sort()
        cat.output( "Words matching tag expression '%s':" % expr, i_c )
        cat.output( cat.ns._formatList(words), i_c )

@define(ns, 'show_tags')
def show_tags( cat ) :
    '''
    show_tags : (-- -> --)
    
    desc:
        Show all tags and their number of associated words: <tag name>/<count>
        
        Example: show_tags
    tags:
        display,tags,console
    '''
    _tagMap( cat )
    
    tags = mapTags.keys()
    tags.sort()
    tagInfo = []
    
    for tag in tags :
        count = len( mapTags[tag] )
        tagInfo.append( "%s/%d" % (tag, count) )
    
    cat.output( cat.ns._formatList(tagInfo), cat.ns.info_colour )

@define(ns, 'show_insts')
def show_inst( cat ) :
    '''
    show_insts : (-- -> --)
    
    desc:
        Displays all instances defined in the currently active namespace
    
        Example: show_insts
    tags:
        instances,display,console
    '''
    cat.output( cat.ns._formatList(cat.ns.instNames()), cat.ns.info_colour )

@define(ns, 'show_all_insts')
def showAllInsts( cat ) :
    '''
    show_all_insts : (-- -> --)
    
    desc:
        Shows all instances defined in any namespace
        
        Example: show_all_insts
    tags:
        instances,display,console
    '''
    i_c      = cat.ns.info_colour
    allInst  = cat.ns.allInstNames()    # returns a dict
    sortKeys = allInst.keys()
    sortKeys.sort()
    
    for item in sortKeys :
        cat.output( "\nInstances defined in '%s':" % item, i_c )
        cat.output( cat.ns._formatList(allInst[item]), i_c )

@define(ns, 'udef')
def udf( cat ) :
    '''
    udef : (-- -> --)
    
    desc:
        Shows all user-defined functions
        
        Example: udef
    tags:
        words,user,defined,display,console
    '''
    keys = cat.ns.allWordNames()
    cat.output( cat.ns._formatList(keys), cat.ns.info_colour )

@define(ns, 'list_files')
def listDefinitionFiles( cat) :
    '''
    list_files : (string:path -> --)
    
    desc:
        Lists the contents of all of the definition files in the
        directory indicated by the path (string) on top of the stack
        path: path to directory containing files to list
        
        Example: 'CatDefs/ list_files
    tags:
        extension,definitions,files,display
    '''
    from glob import iglob
    
    path = cat.stack.pop()
    
    if not isinstance(path, basestring) :
        raise ValueError, "list_files: Directory path must be a string"
    
    fnmap = { }
    
    if not path.endswith("*.cat") :
        path += "*.cat"
    
    regex = re.compile( r'^\s*define\s+(\S+)' )
    
    for file in iglob( path ) :
        fd = open( file, 'r' )
        
        for line in fd :
            mo = regex.match( line )
            
            if mo :
                funcName = mo.group(1)
                
                if funcName in fnmap :
                    cat.output( "File %s duplicates word %s" % (file, funcName), cat.ns.config.get('display', 'error') )
                
                else :
                    fnmap[funcName] = file
            
        fd.close()
    
    keys = fnmap.keys()
    keys.sort()
    maxStr = max( [len(x) for x in keys] ) + 2
    print
    i_c = cat.ns.info_colour
    
    for key in keys :
        akey = key.rjust(maxStr, " ")
        cat.output( "    %s -- %s" % (akey, fnmap[key]), i_c )

@define(ns, 'whereis')
def whereis( cat ) :
    '''
    whereis : (string:word -> --)
    
    desc:
        Shows where the word (a string) is to be found:
            built-in (primitive)
            in a definition file
            user defined
        word: the word whose namespace is sought
        
        Example: 'swap whereis
    tags:
        search,word,display
    '''
    from glob import iglob
    
    theWord = cat.stack.pop()
    source  = 'undefined'
    defined = False
    search  = cat.ns.getWordAnyNS( theWord )
    
    if search[0] :
        if search[2] in cat.ns.defns + ['std'] :
            source = "built-in  (file: %s.py)" % search[2]
        
        else :
            source = search[2]
    
    else :
        path  = cat.ns.getVar('global:CatDefs')[1]
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
            search = cat.ns.getVarAnyNS( theWord, triplet=True )
            
            if search[0] :
                source  = search[2]
                theWord = "variable " + theWord
            
            else :
                search = cat.ns.getInstAnyNS( theWord )
                
                if search[0] :
                    source  = search[2]
                    theWord = "instance " + theWord
                
                else :
                    source = 'undefined'
    
    cat.output( "%s: %s" % (theWord, source), cat.ns.info_colour )

@define(ns, 'help')
def _help( cat ) :
    '''
    help : (string:name -> --)
    
    desc:
        Searches user namespaces for help on 'name' (combination of 'doc' and 'def')
        If not a built-in or user-defined word, the Python help system is invoked for
        the object whose name is on top of the stack.
        'name': string may be of the form <namespace>:<name> or <name>.<name>...
        
        Example: 'swap help
                 'math help
    tags:
        console,help,display,help
    '''
    name = cat.stack.pop()
    i_c  = cat.ns.info_colour
    
    if not isinstance(name, basestring) :
        raise ValueError, "help: Expect a string on the cat.stack"
    
    # check for module/instance
    if name.count( "." ) > 0 :
        # have a module/instance w/ function/method
        inst, method   = name.split( ".", 1 )
        defined, where = cat.ns.isInst( inst )
        
        if defined :
            temp = eval( name, sys.modules, cat.ns.allInst(where) )
            help( temp )
            return
        
        else :
            temp = eval( name, sys.modules )
            help( temp )
            return
    
    # check for user-specified namespace and word
    if name.count(":") == 1 :
        ns, name = name.split( ":" )
        obj      = cat.ns.getWord( name, ns )
        
        if obj[0] :
            func = obj[1]
            
            if callable(func) :
                help( func )
            
            else :
                cat.output( func[1], i_c )   # documentation
                cat.output( str(func[0]), i_c )   # definition
            
            return
        
        else :
            raise ValueError, "help: No help available for '%s' in namespace '%s'" % (name, ns)
    
    # get the info searching all namespaces
    obj = cat.ns.getWordAnyNS( name )
    
    if obj[0] :
        fcn = obj[1]
        
        if callable(fcn) :
            print colored( fcn.__doc__, i_c )
            print colored( '\tbuilt-in', i_c )
    
        else :
            cat.output( fcn[1], i_c )
            cat.output( str(fcn[0]), i_c )
        
        return
        
    # the name may be an unqualified instance or module name
    defined, where = cat.ns.isInst( name )
    
    if defined :
        item = eval( name + ".__class__", sys.modules, cat.ns.allInst(where) )
        help( item )
    
    else :
        item = eval(name, sys.modules)
        help( item )

@define(ns, 'get_words')
def getWords( cat ) :
    '''
    get_words : (-> list:words)
    
    desc:
        Returns a list of words defined in the current user namespace
        to the top of the stack.
        words: defined in user namespace
        
        Example: get_words
    tags:
        words,user,list
    '''
    cat.stack.push( cat.ns.allWordNames() )
    
@define(ns, 'fetch')
def fetch( cat, wrd=None ) :
    '''
    fetch  : (string:word -> --)
    
    desc:
        Fetches and loads into the user's workspace, or a specified one one or more words.
        A "word" may be of the form 'word1,word2,word3,...
        (e.g. 'test,other) or a list (e.g. ['test 'other] list)
        The words may also be prefixed by <namespace>:  (e.g. 'core:modn) to indicate
        thaT the FETCHED word is to be placed in <namespace> (e.g. 'core').
        The order of searching is:
            existing namespaces (copy the file into targeted namespace)
            standard Cat definition files (definition is compiled into the targeted namespace)
            user-defined Cat definition files (as above)
        The 'catlang.cfg' file has an option defining where the standard Cat definition
        files are to be found. The user may add one or more other paths to the
        definition. Entries must be comma separated and no spaces are allowed.
        When indicated in the definition, dependencies are honored and the antecedent
        definitions are loaded as well.
        NOTE: any word in an unlinked namespace can be accessed directly using the
                format <word's namespace>:<word name> and thus need not be copied to user's
                default namespace, nor must the namespace containing the word be
                linked to the user's default namespace.
        word: the name of the word (or list of words) to fetch 
        
        Example: 'abba fetch
    tags:
        word,define,fetch
    '''
    from glob import iglob
    
    parseDeps = re.compile( r'.*deps:\s*(\S+)', re.DOTALL )
    define    = re.compile( r'^\s*define\s+(\S+)(\s*\{|\s)' )
    paths     = cat.ns.config.get( 'paths', 'catdefs' ).split( "," )
    
    # support functions
    def copyTo( text, char ) :
        '''Copies the text from text[0] to the first occurrence of 'char'.
        :param text: the text to be "scanned"
        :type text: string
        :param char: the "scan" terminating character
        :type char: character
        :rtype: a tuple of the form (scanned_text, remaining_text)
        '''
        frag = ""
        ix = text.find( char )
        
        if ix == -1 :
            return ( text, "" )
        
        return ( text[:ix + 1], text[ix+ 1:] )
    
    def search_namespace( word , tgtNS ) :
        if cat.ns.isWord( word )[0] :   # searches 'std' and 'user'
            return True
        
        defined, wd, nmspc = cat.ns.getWordAnyNS( word )
        
        if defined :
            cat.ns.copyWord( word, nmspc, tgtNS )
            process_dependencies( word, tgtNS )
            return True
        
        return False
    
    def process_dependencies( word, nspc ) :
        doc = cat.ns.getWord(word, nspc)
        
        if not doc :
            return 
        
        mo = parseDeps.match( doc[1][1] )
        
        if mo :
            deps = mo.group(1).split( "," )
            
            for i in range( len(deps) ) :
                deps[i] = nspc + ":" + deps[i]
            
            deps = ",".join( deps )
            cat.stack.push( deps )
            cat.ns.exeqt( 'fetch' )
        
    def search_file( fileName, word, tgtNS ) :
        fd         = open( fileName, 'r' )
        expression = ""
        foundWord  = False
        
        for line in fd:
            temp = line.strip()
            
            if temp == "" or temp.startswith( ("//", "#") ) :
                continue
            
            # look for a line starting with "define"
            if not foundWord :
                mo = define.match( temp )
                
                if mo and mo.group(1) == word :
                    foundWord = True
                
                else :
                    continue
            
            # 'else' won't work here because we need to include the 'define' line
            if foundWord :
                # collect all up to a single closing '}'
                # strip line-end comments first
                ix = line.rfind( "//" )
                
                if ix == - 1 :
                    ix = line.rfind( "#" )
                
                if ix > 0 :
                    line = line[:ix]
                
                expression += line
                
                if not temp.endswith( "}}" ) and temp.endswith( "}" ) :
                    break
            # end of for loop over lines in file
        
        fd.close()
        
        # compile the definition if there is one
        if foundWord :
            # first replace newlines in the definition code with spaces
            ix   = expression.rfind( "{" )  # find start of definition
            lhs  = expression[:ix]          # part preceding definition
            rhs  = expression[ix:]          # definition
            expr = ""
            
            # scan over characters looking for special cases
            while rhs :
                c   = rhs[0]
                rhs = rhs[1:]
                
                if c == '"' :   # starting a quote
                    expr += c
                    res   = copyTo( rhs, '"' )
                    expr += res[0]
                    rhs   = res[1]
                
                elif c == "'" :     # starting a string constant
                    expr += c
                    res   = copyTo( rhs, " " )
                    expr += res[0]
                    rhs   = res[1]
                
                elif c == "\n" :    # the dreaded newline
                    expr += " "
                
                else :
                    expr += c
            
            # now parse the definition
            cat.define( lhs + expr, tgtNS )
            process_dependencies( word, tgtNS )
            return True
        
        else :
            return False
    
    # ------- main code starts here -------
    # check to see if we are coming from 'loadNS'
    if wrd :
        words = wrd
    
    else :
        words = cat.stack.pop_list()
    
    # find definition for each word
    for word in words :
        tgtNS = cat.ns.targetNS if cat.ns.targetNS else cat.ns.getUserNS()
        
        # check for stipulated namespace
        if word.count( ":" ) == 1 :
            tgtNS, word = word.split( ":" )
            
            if not cat.ns.isNS( tgtNS ) :
                cat.ns.createNS( tgtNS )
        
        # look in defined namespaces first
        found = search_namespace( word, tgtNS )
        
        if found :
            continue
        
        # not in a namespace -- check definition files
        for path in paths :
            if found :
                break   # next word
            
            path += "*.cat"
            
            # search the definition files
            for file in iglob( path ) :
                if found :
                    break   # next path
                
                found = search_file( file, word, tgtNS )
        
        if not found :
            raise ValueError, "fetch: cannot find the word '%s'" % word

@define(ns, 'load')
def load( cat, force=False, nmsp='' ) :
    '''
    load : ( list|string:fileName -> --)
    
    desc:
        Loads the script whose name string is on top of the stack into a namespace
        The object on the stack may take the form:
            string: <simple file name>
            string: <simple file name>,<simple file name>,...
            string: <namespace>:<simple file name>
            string: <namespace>:<simple file name>, <namespace>:<simple file name>,...
            list: [<simple file name>, <simple file name>, ...]
            list: [<namespace>:<simple file name>,...]
            fileName: the string or list providing the name of the file(s) to load
            
            Example: 'TS:TimeStack.cat load
    tags:
        file,load,script
    '''
    def stripComments( text ) :
        temp = text.strip()
        
        if temp == "" or temp.startswith( ('//','#') ) :
            return ""
        
        ix = temp.rfind( '//' )
        
        if ix > 0 :
            temp = temp[:ix]
        
        else :
            ix = temp.rfind( '#' )
            
            if ix > 0 :
                temp = temp[:ix]
        
        return temp + "\n"
    
    def flatten(x):
        result = []
        
        for el in x:
            if hasattr(el, "__iter__") and not isinstance(el, basestring):
                result.extend(flatten(el))
            
            else:
                result.append(el)
            
        return result
    
    currentUserNS = cat.ns.getUserNS()
    deps          = []
    fileNames     = cat.stack.pop_list()
    
    # check for a predefined target namespace
    if nmsp :
        tgtNS = nmsp   # use required namespace
    
    else :
        tgtNS = cat.ns.getUserNS()  # no predefined namespace => use default
    
    # iterate over all file names in the list
    for fileName in fileNames :
        if not isinstance(fileName, basestring) :
            raise Exception, "load: File name must be a string"
        
        if fileName.count(":") == 1 :
            nspc, fileName = fileName.split(":")
            
            # if nmsp arg is '' then there is no predefined namespace having precedence
            if not nmsp :
                tgtNS = nspc
         
            if not cat.ns.isNS( tgtNS ) :
                cat.ns.createNS( tgtNS )
            
        cat.ns.changeUserNS( tgtNS )
            
        if not force and cat.ns.hasFile(fileName, tgtNS) :
            continue
        
        if not os.access(fileName, os.F_OK) :
            raise Exception, "load: no file called '%s'" % fileName
        
        fd     = open( fileName, 'r' )
        buffer = ""
        lineNo = 0
        inDef  = False
        
        for line in fd :
            lineNo += 1
            temp    = stripComments( line.strip() )
            
            if not temp :
                continue
            
            if not inDef :
                if not temp.startswith( "define" ) :
                    cat.eval( temp.strip() )
                    
                    # the evaluation of temp may have changed the user's initial namespace
                    # if nmsp arg is '' then there is no predefined namespace
                    if not nmsp :
                        tgtNS = cat.ns.getUserNS()
                    
                    continue
                
                else :
                    inDef = True
            
            # must be in a definition (this hack permits 1-line definitions)
            if inDef :
                # consolidate lines of a definition into a single string
                buffer += temp
                temp    = temp.strip()
                
                # end of function definition?
                if not temp.endswith( "}}" ) and temp.endswith( "}" ) : 
                    # end of definition: parse the string
                    ix    = buffer.rfind( "{" )
                    front = buffer[:ix]
                    repl  = buffer[ix:].replace("\n", " ")
                    buffer = front + repl
                    defn   = cat.parser.parse_definition( buffer )
                    cat.ns.addWord( defn.name, list(cat.parser.gobble(defn.definition)),
                                    "  %s %s\n%s" % (defn.name, defn.effect, defn.description), tgtNS )
                    deps.append( defn.dependencies )
                    buffer = ""
                    inDef  = False
                
                else :
                    continue    # examine the next line
        
        cat.ns.addFile( fileName, tgtNS )
        fd.close()
        
        # process any dependencies
        depList = flatten( deps )
        depList = reduce( lambda y,x: y + [x] if x not in y else y, depList, [] )   # remove duplicates
        
        for dep in depList :
            # check to see if the dependency is in the target namespace
            if cat.ns.isWord( dep, tgtNS ) :
                continue
            
            # is it in some namespace?
            res = cat.ns.getWordAnyNS( dep )
            
            if res[0] :
                # OK fetch it
                cat.ns.addWord( dep, res[1][0], res[1][1], tgtNS )
            
            else :
                fetch( cat, [dep] )
        
    cat.ns.changeUserNS( currentUserNS )

@define(ns, 'reload')
def reload( cat ) :
    '''
    reload : ( string:fileName -> --)
    
    desc:
        Reloads the script whose name string is on top of the stack
        fileName: the string or list of files to be reloaded, as described in 'load'
                    word documentation.
        
        Example: 'TS:TimeStack.cat reload
    tags:
        file,reload,script
    '''
    load( cat, True )

@define(ns, 'load_defs')
def loadAllDefs( cat ) :
    '''
    load_defs : (-- -> --)
    
    desc:
        Load all definitions (in CatDefs directory) into their corresponding namespaces
        Accesses definition files in directory pointed to by 'global:CatDefs'
        
        Example: load_defs
    tags:
        namespaces,definitions,file,script
    '''
    paths = cat.ns.config.get( 'paths', 'catdefs' ).split( "," )
    
    for path in paths :
        loadFile = path + "everything.cat"
        
        if os.access(loadFile, os.F_OK) :
            cat.ns.addVar( 'global:CatDefs', path )
            cat.stack.push( loadFile )
            load( cat )

@define(ns, 'import')
def catImport( cat ) :
    '''
    import : (string:module_name -> --)
    
    desc:
        Imports the named module for use by the program.
        Note: members of the module are accessed  with this notation: <module name>.<member name>
              parameters must precede the function call as a list with arguments in the order
              required by the function. E.g. ([base expt] list math.pow -> base^expt)
        module_name: the name of the module to import
        
        Example: 'math import
                 'os import
                 'localModule import
    tags:
        module,import 
    '''
    what = cat.stack.pop()
    
    if isinstance(what, basestring) :
        sys.modules[what] = __import__( what )
    
    else :
        raise Exception, "import: The module name must be a string"

@define(ns, 'instance')
def catInstance( cat ) :
    '''
    instance : (list:args string:module.class string:name -> --)
    
    desc:
        Creates an instance of a specified class.
        The instance is invoked in the usual way: <instance>.<method>
        args: a list of arguments required by __init__ when creating an instance (if none, use 'nil')
        module.class: the class within the module called to create an instance
        name: the name by which the instance will be known. Can be of the form
                <namespace>:<instance name> to force the instance into the
                selected namespace
        
        Example: 'Meeus import
                 nil 'Meeus.Meeus 'm instance
                 Use:  [2012 7 4] list m.JD
    tags:
        instance,class,module
    '''
    name, cls, args = cat.stack.pop_n( 3 )
    
    if not isinstance(cls, basestring) :
        raise ValueError, "instance: The module.class name must be a string"
    
    if not isinstance(name, basestring) :
        raise ValueError, "instance: The instance name must be a string"
    
    if isinstance(args, basestring) and args.startswith("[") :
        args = eval( args )
    
    # make single argument into a tuple
    if not isinstance(args, (list, tuple)) :
        args = (args,)
    
    # use eval() to get an instance
    inst = eval( "%s%s" % (cls, str(tuple(args))), sys.modules )
    
    # determine which namespace will get it
    if name.count(":") == 1 :
        nspc, name = name.split(":")
    
    else :
        if cat.ns.targetNS :
            nspc = cat.ns.targetNS
        
        else :
            nspc = cat.ns.getUserNS()
    
    # save the instance in the specified namespace
    cat.ns.addInst( name, inst, nspc ) 

@define(ns, 'as_instance')
def asInstance( cat ) :
    '''
    as_instance : (obj:instance string:name -> --)
    
    desc:
        Takes the class instance at [-1] and enters it into the instances table
        with the name 'name'. The name may be of the form <namespace>:<name>.
        instance: the instance to be recorded
        name: the name of the instance
        
        Example: m 'mm as_instance
    tags:
        instance,class,save
    '''
    name, inst = cat.stack.pop_2()
    
    if name.count(":") == 1 :
        nspc, name = name.split(":")
    
    else :
        if cat.ns.targetNS :
            nspc = cat.ns.targetNS
        
        else :
            nspc = cat.ns.getUserNS()
    
    # save the instance in the specified namespace
    cat.ns.addInst( name, inst, nspc ) 

@define(ns, 'get_instance')
def get_instance( cat ) :
    '''
    get_instance : (string:arg -> instance:inst)
    
    desc:
        Pushes the named instance to the top of the stack.
        arg: the path to the instance. Takes the form: <namespace>:<instance name>
        inst: the instance object
        
        Example: 'TS:ts get_instance => <the instance called ts>
    tags:
        instance,namespace
    '''
    path     = cat.stack.pop()
    ns, inst = path.split( ":" )
    
    if not cat.ns.isNS(ns) :
        raise ValueError, "get_instance: no namespace called '$%s'" % ns
    
    if not cat.ns.isInst( inst, ns ) :
        raise ValueError, "get_instance: no instance called '%s' in namespasce '%s'" % (inst, ns)
    
    cat.stack.push( cat.ns.getInst(inst, ns)[1] )    

@define(ns, 'prompt')
def newPrompt( cat ) :
    '''
    prompt : (string:prompt -> --)
    
    desc:
        Sets the prompt string to the string on top of the cat.stack
        prompt: the new prompt
        
        Example: 'TimeStack prompt
    tags:
        console,REPL,prompt
    '''
    cat.ns.setVar( 'global:prompt', str(cat.stack.pop()) )

@define(ns, 'append_to_sys_path')
def append_sys_path( cat ) :
    '''
    append_to_sys.path : (string:absolute_file_path -> --)
    
    desc:
        Appends the absolute file path on top of the stack to sys.path
        absolute_file_path: the full (absolute) path to (and including) the file name
        
        Example: 'TimeStack.py append_to_sys_path
    tags:
        file,path,sys.path,append
    '''
    import sys
    
    path = cat.stack.pop()
    ix   = path.rindex( "/" )
    path = path[:ix]
    sys.path.append( path )

@define(ns, 'config_get')
def config_get( cat ) :
    '''
    config_get : (string:section_and_key --> string:key_value)
    
    desc:
        Pushes the value of the key associated with catlang.cfg onto the stack.
        section_and_key: a string of the form <section>:<key>
        key_value: the value of the key as a string
        
        Example: 'prompt:default config_get => "Cat>"
    tags:
        config,configuration,key,value,get
    '''
    sect, key = cat.stack.pop().split( ":" )
    cat.stack.push( cat.ns.config.get(sect, key) )

@define(ns, 'config_get_boolean')
def config_bool( cat ) :
    '''
    config_get_boolean : (string:section_and_key --> boolean:key_value)
    
    desc:
        Pushes the value of the key onto the stack.
        section_and_key: a string of the form <section>:<key>
        key_value: the value of the key as a boolean (True or False)
        
        Example: 'display:use_colour config_get_bool => True
    tags:
        config,configuration,key,value,get,boolean
    '''
    sect, key = cat.stack.pop().split( ":" )
    cat.stack.push( cat.ns.config.getboolean(sect, key) )

@define(ns, 'config_get_float')
def config_float( cat ) :
    '''
    config_get_float : (string:section_and_key --> float:key_value)
    
    desc:
        Pushes the value of the key onto the stack.
        section_and_key: a string of the form <section>:<key>
        key_value: the value of the key as a float
        
        Example: 'location:elevation config_get_float => 1829.0
    tags:
        config,configuration,key,value,get,float
    '''
    sect, key = cat.stack.pop().split( ":" )
    cat.stack.push( cat.ns.config.getfloat(sect, key) )

@define(ns, 'config_get_int')
def config_int( cat ) :
    '''
    config_get_int : (string:section_and_key --> int:key_value)
    
    desc:
        Pushes the value of the key onto the stack.
        section_and_key: a string of the form <section>:<key>
        key_value: the value of the key as an integer
        
        Example: 'test:size config_get_int => 42
    tags:
        config,configuration,key,value,get,int,integer
    '''
    sect, key = cat.stack.pop().split( ":" )
    cat.stack.push( cat.ns.config.getint(sect, key) )

@define(ns, "config_set")
def config_set( cat ) :
    '''
    config_set : (string:value string:section_and_key -> --)
    
    desc:
        Makes an entry in the configuration dict based on the section and key at [0]
        and the associated value at [-1]
        value: the value string
        section_and_key: a string of the form <section name>:<key name>
        
        Example: 'TimeStack> 'prompt:default config_set
    tags:
        meta,config,configuration,set,option,key,value
    '''
    sect, key = cat.stack.pop().split( ":" )
    
    if not cat.ns.config.has_section(sect) :
        cat.ns.config.add_section( sect )
    
    value = str( cat.stack.pop() )
    cat.ns.config.set( sect, key, value )

@define(ns, 'config_save')
def config_save( cat ) :
    '''
    config_save : (string:filename -> --)
    
    desc:
        Saves the current configuration dictionary as a file.
        filename: the name of the target file to receive the configuration info
        
        Example: 'new_catlang.cfg config_save
    tags:
        config,configuration,save
    '''
    fileName = cat.stack.pop()
    
    with open(fileName) as fd :
        cat.ns.config.write( fd )

@define(ns, "config_del_section")
def config_del_sect( cat ) :
    '''
    config_del_section : (string:sect_name -> --)
    
    desc:
        Deletes from the configuration dictionary the section whose name
        is on top of the stack.
        sect_name: the name of the section to be deleted
        
        Example: 'test config_del_section
    tags:
        config,configuration,delete,section
    '''
    name = cat.stack.pop()
    
    try :
        cat.ns.config.remove_section( name )
    
    except :
        raise ValueError, "config_del_section: no section called '%s'" % name

@define(ns, "config_del_key")
def config_del_key( cat ) :
    '''
    config_del_key : (string:sect_and_key -> --)
    
    desc:
        Deletes from the configuration dictionary the section and key whose name
        is on top of the stack.
        sect_and_key: the name of the section and key to be deleted. Must be of
                      the form: <section name>:<key>
        
        Example: 'test:size config_del_key
    tags:
        config,configuration,delete,key,option
    '''
    sect, name = cat.stack.pop().split( ":" )
    
    try :
        tf = cat.ns.config.remove_option( sect, name )
        
        if not tf :
            raise ValueError, "config_del_key: No key called '%s'" % name
    
    except :
        raise ValueError, "config_del_key: No section called '%s'" % sect


def _returnNS() :
    return ns
