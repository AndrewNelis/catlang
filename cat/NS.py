from cat.namespace import NameSpace
from sets import Set
import sys, os, ConfigParser

class NS:
    '''Creates and manipulates namespaces
    Loads cat (built-in) definitions into a standard namespace ('std')
    Creates an initial 'user' namespace
    '''
    # names the built-in words (functions) imported by defs/__init__.py
    defns = ['cat_arithmetic', 'cat_nsWords',  'cat_stack', 'cat_debug', 'cat_control',
             'cat_lists',  'cat_conditionals', 'cat_meta',  'cat_strings','cat_misc',
             'cat_io', 'cat_time', 'cat_types','cat_basic_tests', 'cat_user']
    
    def __init__( self, catEval, userWords = None ) :
        '''creates all necessary structures for namespaces'''
        self.cat      = catEval
        self.targetNS = ''
        self.config   = ConfigParser.ConfigParser()
        
        # read the configuration file
        cfg_file = os.getcwd() + "/Cat/catlang.cfg"
        self.config.readfp( open(cfg_file) )
        
        if self.config.getboolean('display', 'use_colour' ) :
            self.info_colour = self.config.get( 'display', 'info' )
        
        else :
            self.info_colour = None
        
        # create two standard namespaces
        self._nsDict = { 'std' : NameSpace(),
                         'user' : NameSpace() }
        
        # add any user defined words to the 'user' namespace
        if isinstance(userWords, dict) :
            self._nsDict['user'].updateWords( userWords )
        
        # fill 'std' with words by importing definition files
        levels = __import__( 'defs' )
        
        for defn in self.defns :
            item               = sys.modules["defs." + defn]
            self._nsDict[defn] = item._returnNS()
            self._nsDict['std'].addLink(defn)
        
        # at this point, no more links will be added to the 'std' namespace
        # the current user namespace is always the last link in 'std'
        self._nsDict['std'].addLink( 'user' )
        
        # prime the 'global' directory with a few values
        self._nsDict['std'].addVar( 'prompt',  self.config.get('prompt', 'default') )
    
    def _searchLinks(self, item, startNS='std', kind='words', viewed=[] ):
        '''Recursive search of the links for a specified item. Search is depth-first.
        :param item: the item to be found (or not)
        :type item: string
        :param startNS: the namespace in which to start the search
        :type startNS: string
        :param kind: the kind of object being sought
        :type kind: string (one of 'words', 'vars', 'instances')
        :param viewed: a list of links already viewed (to avoid circularity)
        :type viewed: a list
        :rtype: a tuple of the form (bool:<true or false>, any:<value>, string:<namespace>)
        '''
        if startNS not in self._nsDict :
            raise ValueError, "No namespace called '%s'" % startNS
        
        if self._nsDict[startNS].searchFor( item, kind ) :
            return (True, self._nsDict[startNS].getValueOf(item, kind)[1], startNS)
        
        # item not in the 'kind' dictionary of this namespace
        # iterate through the links (if any)
        for nmsp in self._nsDict[startNS].getLinks() :
            if nmsp not in viewed :
                viewed.append( nmsp )
                val = self._searchLinks( item, nmsp, kind, viewed )
                
                if val[0] :
                    return val
        
        return (False, None, None)

    # namespace methods
    def _checkNS( self, ns, extra=[] ) :
        '''checks for valid namespace
        :param ns: the namespace name
        :type ns: string  (If None, the current user namespace is used)
        :param extra: additional namespaces to be excluded
        :type extra: list of strings
        :rtype: ns
        '''
        if ns == None :
            ns = self.getUserNS()
        
        if not isinstance(ns, basestring) :
            raise ValueError, "Namespace name must be a string"
        
        if not self.isNS(ns) or ns in extra or ns in self.defns :
            raise ValueError, "Namespace '%s' is not available" % ns
        
        return ns
    
    def createNS( self, nsName ) :
        '''Create a namespace for user use
        :param nsName: the name of the new namespace
        :type nsName: string
        :rtype: none
        '''
        if not isinstance(nsName, basestring) :
            raise ValueError, "Namespace name must be a string"
        
        if nsName == 'std' :
            raise ValueError, "cannot create a shadow standard functions namespace"
        
        if nsName in self._nsDict :
            raise ValueError, "The namespace '%s' already exists" % nsName
        
        self._nsDict[nsName] = NameSpace()
    
    def setUserLinksNS( self, nsNames, ns=None ) :
        '''
        Replaces all existing links in the specified namespace with those
        supplied as a comma-separated list of existing link names.
        :param nsNames: list of namespaces to be linked to the specified namespace
        :type nsNames: string
        :param ns: target namespace whose links are to be replaced
        :type ns: string (default is None => 'user')
        '''
        ns = self._checkNS( ns, ['std'] )
        self._nsDict[ns].replaceLinks( nsNames )
    
    def renameNS( self, newNS, oldNS=None ) :
        '''Renames the oldNS to newNS
        :param oldNS: name of an existing namespace
        :type oldNS: string
        :param newNS: the new namespace name
        :type newNS: string
        :rtype: none
        '''
        oldNS = self._checkNS( oldNS, ['std', 'user'] )
        newNS = self._checkNS( newNS, ['std', 'user'] )
        
        if self.isNS(newNS) :
            raise ValueError, "renameNS: namespace '%s' is already in existence" % newNS
        
        self._nsDict[newNS] = self._nsDict[oldNS]
        del self._nsDict[oldNS]
    
    def changeUserNS( self, nsName=None ) :
        '''Change the current user namespace name
        :param nsName: the name of the new current namespace
        :type nsName: string  (if the argument is None, the standard user namespace, 'user', is used)
        :rtype: none
        '''
        nsName = self._checkNS( nsName, ['std'] )        
        self._nsDict['std'].popLink()
        self._nsDict['std'].addLink( nsName )
    
    def getUserNS( self ) :
        '''Returns the current user namespace name
        :rtype: string
        '''
        return self._nsDict['std'].peekLink()
    
    def delNS( self, ns  ) :
        '''Deletes the given namespace
        :param name: the name of the namespace to be deleted
        :type name: string
        '''
        ns = self._checkNS( ns, ['std', 'user'] )
        del self._nsDict[ns]
    
    def isNS( self, ns ) :
        '''Tests to see if the argument is already defined as a namespace
        :param ns: the namespace name
        :type ns: string
        :rtype: boolean
        '''
        if ns == None :
            return True
        
        return ns in self._nsDict
    
    def copyNS( self, src, dest ) :
        '''Copy the src namespace to the dest namespace
        :param src: the source namespace name
        :type src: string
        :param dest: the name of the destination namespace
        :type dest: string
        :rtype: none
        '''
        src  = self._checkNS( src, ['std'] )
        dest = self._checkNS( dest, ['std'] )
        
        if not self.isNS(src) :
            raise ValueError, "No source namespace (%s) to copy" % src
        
        if self.isNS(dest) :
            raise ValueError, "Destination namespace name '%s' already in use" % dest
        
        self._nsDict[dest] = { }.update( self._nsDict[src] )
    
    def appendNS( self, src=None, dest=None ) :
        '''Appends the name of the source namespace (src) to the links of
        the destination namespace (dest).
        :param src: name of the source namespace
        :type src: string
        :param dest: name of the destination namespace
        :type dest: string
        :rtype: none
        '''
        if src == dest :
            return
        
        src  = self._checkNS( src, ['std'] )
        dest = self._checkNS( dest, ['std'] )
        self._nsDict[dest].addLink( src )
    
    def hasNS( self, ns, targetNS=None ) :
        '''Checks the targetNS namespace links for specified link name (namespace name)
        :param ns" the namespace name to be checked in the links
        :type ns: string
        :param targetNS: the namespace whose links are to be checked
        :type targetNS" string
        :rtype: boolean
        '''
        tgt = self._checkNS( targetNS )
        return self._nsDict[tgt].hasLink()
    
    def getLinksNS( self, ns=None ) :
        '''Lists all the namespaces linked into the specified namespace
        :param: ns: the namespace whose links are to be found
        :type ns: string
        :rtype: list of strings
        '''
        ns = self._checkNS( ns, ['std'] )
        return self._nsDict[ns].getLinks()
    
    def listAllNS( self ) :
        '''Lists all available namespaces
        :rtype: list of strings
        '''
        lst = [ ]
        
        for nsName in self._nsDict :
            if nsName not in self.defns and nsName != 'std' :
                lst.append( nsName )
        
        return lst
    
    def removeAllLinkRefsNS( self, nspc ) :
        '''Removes ns from links in all namespaces
        :param nspc: name of ns to be delinked
        :type nspc: string
        :rtype: none
        '''
        exclude = self.defns + ['std']
        include = Set(self._nsDict.keys()) - Set(exclude)
        
        for ns in include :
            self._nsDict[ns].delLink( nspc )
        
    # word methods
    def addWord( self, name, definition, descrip='', ns=None ) :
        """Called to *define* new words
        :param name: the name of the new word
        :type name: string
        :param definition: the definition of the word
        :type definition: a list of predefined words
        :param descrip: the description (doc) of the word
        :type descrip: string
        :param ns: the namespace to take the word (if None, the current user namespace is used)
        :type ns: string (if None, the current user namespace is used)
        :rtype: none
        """
        ns = self._checkNS( ns, ['std'] )
        self._nsDict[ns].addWord( name, (definition, descrip) )
    
    def getWord( self, name, ns='std' ) :
        '''Returns the word info associated with the name
        :param name: the name of the word sought
        :type name: string
        :param ns: the target namespace
        :type ns: string (if None, the current user namespace is used)
        :rtype: a tuple of the form (bool:<found>, list|function:<definition>, string:<namespace name>)
        '''
        # note that the 'std' namespace list ('__links__') has as its last element the
        # current user namespace and so it is searched automatically just like
        # the other links associated with 'std'
        ns = self._checkNS( ns )
        return self._searchLinks( name, ns, 'words', [] )
    
    def isWord( self, name, ns='std' ) :
        '''
        Searches the user namespace and namespaces linked to it for the existence of
        a word called 'name'.
        :param name: the name of the word sought
        :type name: string
        :param ns: the name of the namespace to search
        :type ns: string  (if None, the current user namespace is used)
        :rtype: tuple of the form (True, namespace_name) | (False, None)
        '''
        # note that the 'std' namespace list ('__links__') has as its last element the
        # current user namespace and so it is searched automatically just like
        # the other links associated with 'std'
        val = self._searchLinks( name, ns, 'words', [] )
        
        if val[0] :
            return val[0:3:2]
        
        else :
            return (False, None)
    
    def delWord( self, name, ns=None  ) :
        '''Deletes a word from a namespace.
        Words in the 'std' namespace are protected from deletion
        :param name: the name of the word to be deleted
        :type name: string
        :param ns: the target namespace
        :type ns: string (if None, the current user namespace is used)
        :rtype: none
        '''
        ns = self._checkNS( ns, ['std'] )
        self._nsDict[ns].delWord( name )
    
    def delAllWords( self, ns=None ) :
        '''Removes all words from the specified namespace
        :param ns: name of the namespace to be purged
        :type ns: string
        :rtype: none
        '''
        ns = self._checkNS( ns, ['std'] )
        self._nsDict[ns].delAllWords()
            
    def allWordNames( self, ns=None ) :
        '''Returns a sorted list of all word names in a specified namespace
        :param ns: the namespace name
        :type ns: string
        :rtype: list of strings
        '''
        ns = self._checkNS( ns, ['std'] )
        return self._nsDict[ns].allWordNames()
    
    def copyWord( self, name, from_=None, to=None ) :
        '''Copies the word 'name' in namespace 'frmo_' to the currently active user's namespace
        :param word: the name of the word to copy
        :type word: string
        :param from_: the name of the namespace in which the word resides
        :type from_: string (if 'None' then the default user namespace is used)
        :param to: the namespace into which to copy the word
        :type to: string (if 'None' then the default user namespace is used)
        '''
        from_ = self._checkNS( from_ )
        to    = self._checkNS( to )
        
        if not self.isWord( name, from_ ) :
            raise ValueError, "There is no word '%s' in namespace '%s'" % (name, from_)
        
        word = self._nsDict[from_].getWord( name )
        self._nsDict[to].addWord( name, word[1] )
    
    def getWordAnyNS( self, word ) :
        '''Returns word definition if it exists in any namespace
        :param word: name of the word sought
        :type word: string
        :rtype: a tuple of the form (bool:<found?>, tuple:<word def>, string:<namespace>)
        '''
        for ns in self._nsDict :
            if self.isWord( word, ns )[0] :
                return self._searchLinks( word, ns, 'words', [] )
        
        return (False, None, None )
    
    def allDefinedWords( self ) :
        '''Returns a list of all words currently defined in the entire system, other than built-ins
        :rtype: list of lists of strings (word names). Each inner list element [0] is the namespace name
        '''
        nameList = []
        search   = []
        exclude  = self.defns + ['std']
        
        for ns in self._nsDict:
            if ns not in exclude :
                search.append( ns )
        
        for ns in search :
            nameList.append( [ns] + self.allWordNames(ns) )
        
        return nameList
    
    def builtinWords( self ) :
        '''
        '''
        wordList = self._nsDict['std'].allWordNames()
        links    = self._nsDict['std'].getLinks()
        
        for link in links[:-1] :    # because the last link is the current user namespace
            wordList += self._nsDict[link].allWordNames()
        
        wordList.sort()
        return wordList
    
    def allWordNamesInNS( self, ns=None ) :
        '''
        '''
        ns = self._checkNS( ns, ['std'] )
        wordList = self._nsDict[ns].allWordNames()
        links = self._nsDict[ns].getLinks()
        
        for link in links :
            wordList += self._nsDict[link].allWordNames()
        
        wordList.sort()
        return wordList
    
    # var methods
    def addVar( self, varName, val, ns=None ) :
        '''
        stores val into the __vars__ dictionary in some namespace under key name varName
        
        varName may take the form:
            <simple name>
            <namespace>:<simple name>
        
        Note that the namespace 'global' is reserved for saving global variables
        :param varName: name of the variable to be added
        :type varName: string
        :param ns: the target namespace
        :type ns: string (if None, the current user namespace is used)
        :rtype: none
        '''
        if varName.count(":") == 1 :
            ns, var = varName.split( ":" )
            
            if ns.lower() == 'global' :
                self._nsDict['std'].addVar( var, val )
                return
            
            else :
                varName = var
        
        ns = self._checkNS( ns )
        self._nsDict[ns].addVar( varName, val )
    
    def getVar( self, varName, ns=None, triplet=False ) :
        '''
        returns the value associated with user variable named in what from the user's '__var__' dict
        Note that 'what' may be of the form:
            <simple name>
            <namespace>:<simple name>
                <namespace> may also be the special case 'global' to access global variables
        :param varName: the name of the variable
        :type varName: string
        :param ns: the name of the target namespace
        :type ns: string (if None, the current user namespace is used)
        :rtype: a tuple of the form (bool:<found?>, any:<value or None>)
        '''
        if varName.count(":") == 1 :
            ns, var = varName.split( ":" )
            
            if ns.lower() == 'global' :
                search = self._nsDict['std'].getVar( var )
                
                if triplet :
                    return search
                
                else :
                    return search[0:2]
            
            else :
                varName = var
        
        ns     = self._checkNS( ns )
        search = self._searchLinks( varName, ns, 'vars', [] )
        
        if triplet :
            return search
        
        else :
            return search[0:2]
    
    def isVar( self, name, ns='std' ) :
        '''
        Searches the user namespace and namespaces linked to it for the existence of
        a variable called 'name'.
        :param name: the name of the word sought
        :type name: string
        :param ns: the name of the namespace to search
        :type ns: string  (if None, the current user namespace is used)
        :rtype: tuple of the form (True, namespace_name) | (False, None)
        '''
        # note that the 'std' namespace list ('__links__') has as its last element the
        # current user namespace and so it is searched automatically just like
        # the other links associated with 'std'
        ns  = self._checkNS( ns )
        val = self._searchLinks( name, ns, 'vars', [] )
        
        if val[0] :
            return val[0:3:2]
        
        else :
            return (False, None)
    
    def delVar( self, name, ns=None  ) :
        '''Delete a variable from a specified namespace.
        Global variables are deleted from 'std' vars.
        :param name: the name of the variable to delete
        :type name: string
        :param ns: the name of the target namesapce
        :type ns: string (if None, the current user namespace is used)
        :rtype: none
        '''
        if name.count(":") == 1 :
            ns, name = name.split( ":" )
            
            if ns.lower() == 'global' :
                self._nsDict['std'].delVar( name )
                return
        
        ns = self._checkNS( ns, ['std'] )
        self._nsDict[ns].delVar( name )
    
    def allVarNamesAnyNS( self ) :
        '''Returns a list of all variable names in the namespace, ns
        :param ns: name of namespace
        :type ns: string  (if None, the current user namespace is used)
        :rtype: a list of variable names
        '''
        exclude  = self.defns + ['std']
        include  = Set(self._nsDict.keys()) - Set(exclude)
        varsDict = {}
        
        for ns in include :
            varsDict[ns] = self._nsDict[ns].allVarNames()
        
        return varsDict
    
    def allVarNames( self, ns=None ) :
        '''Returns a list of all variable names in the namespace, ns
        :param ns: name of namespace
        :type ns: string  (if None, the current user namespace is used)
        :rtype: a list of variable names
        '''
        ns = self._checkNS( ns )
        return self._nsDict[ns].allVarNames()
    
    def getVarAnyNS( self, word, triplet=False ) :
        '''Returns word definition if it exists in any namespace
        :param word: name of the word sought
        :type word: string
        :rtype: a tuple of the form (bool:<found?>, tuple:<word def>, string:<namespace>)
        '''
        for ns in self._nsDict :
            if self.isVar( word, ns ) :
                return self.getVar( word, ns, triplet )
        
        return (False, None, None )
    
    # instance methods
    def addInst( self, name, value, ns=None ) :
        '''Add an instance to a namespace
        :param name: the name of the instance
        :type name: string
        :param value: the instance
        :type value: instance of something
        :param ns: the target namespace name
        :type ns: string (if None, the current user namespace is used)
        '''
        ns = self._checkNS( ns, ['std'] )
        self._nsDict[ns].addInst( name, value )
    
    def getInst( self, name, ns=None ) :
        '''Retrieves an instance from a namespace by its name
        :param name: the name of the instance to be rtrieved
        :type name: string
        :param ns: the name of the target namespace
        :type ns: string  (if None, the current user namespace is used)
        :rtype: a tuple of the form (bool:<found?>, instance:<the instance itself>, string:<namespace>)
        '''
        ns = self._checkNS( ns, ['std'] )
        return self._searchLinks( name, ns, 'instances', [] )
    
    def isInst( self, name, ns=None  ) :
        '''
        Searches the user namespace and namespaces linked to it for
        an instance called 'name'.
        :param name: the name of the instance sought
        :type name: string  (if None, the current user namespace is used)
        :rtype: tuple of the form (True, namespace) | (False, None)
        '''
        ns  = self._checkNS( ns, ['std'] )
        val = self._searchLinks( name, ns, 'instances', [] )
        
        if val[0] :
            return val[0:3:2]
        
        else :
            return (False, None)
    
    def delInst( self, name, ns=None  ) :
        '''deletes an instance.
        :param name: the name of the instance to be deleted
        :type name: string
        :param ns: the name of the target namespace
        :type ns: string  (if None, the current user namespace is used)
        :rtype: none
        '''
        ns  = self._checkNS( ns, ['std'] )
        val = self._searchLinks( name, ns, 'instances', [] )
        
        if val[0] :
            self._nsDict[val[2]].delInst(name)
    
    def allInst( self, ns=None ) :
        '''Returns a list of all instances in the namespace, ns
        :param ns: name of namespace
        :type ns: string  (if None, the current user namespace is used)
        :rtype: a list of instances
        '''
        ns = self._checkNS( ns )
        return self._nsDict[ns].allInst()
    
    def instNames( self, ns=None ) :
        '''Returns a list of all instance names in the namespace, ns
        :param ns: name of namespace
        :type ns: string  (if None, the current user namespace is used)
        :rtype: a list of instance names
        '''
        ns = self._checkNS( ns )
        return self._nsDict[ns].allInstNames()
    
    def allInstNamesAnyNS( self ) :
        '''Returns a list of lists giving all instance names with the
        associated namespace name
        :rtype: dict where the namespace is a key and the value is a list of instances
        '''
        exclude  = self.defns + ['std']
        include  = Set(self._nsDict.keys()) - Set(exclude)
        instDict = {}
        
        for ns in include :
            instDict[ns] = self._nsDict[ns].allInstNames()
        
        return instDict
        
    def getInstAnyNS( self, word ) :
        '''Returns instance definition if it exists in any namespace
        :param word: name of the word sought
        :type word: string
        :rtype: a tuple of the form (bool:<found?>, tuple:<word def>, string:<namespace>)
        '''
        for ns in self._nsDict :
            if ns == 'std' :
                continue
            
            # use 'try' because isInst will raise an exception for 'std' or 'cat_*' namespaces
            try :
                if self.isInst( word, ns ) :
                    return self.getInst( word, ns )
            
            except :
                continue
        
        return (False, None, None )
    
    # link methods
    def addLink( self, name, ns=None ) :
        '''Adds a link to another namespace to the specified one.
        :param name: the name of the namespace
        :type name: string
        :param ns: the name of the target namespace
        :type ns: string  (if None, the current user namespace is used)
        :rtype: none
        '''
        ns = self._checkNS( ns, ['std'] )
        self._nsDict[ns].addLink( name )
    
    def getLinks( self, ns=None ) :
        '''Returns a list of links in the target namespace.
        :param ns: the target namespace
        :type ns: string  (if None, the current user namespace is used)
        :rtype: a list of name strings
        '''
        ns = self._checkNS( ns, ['std'] )
        return self._nsDict[ns].getLinks()
    
    def delLink( self, name, ns=None ) :
        '''Removes a link name from a target namespace
        :param name: the name of the link to be removed
        :type name: string
        :param ns: the name of the target namespace
        :type ns: string  (if None, the current user namespace is used)
        :rtype: none
        '''
        ns = self._checkNS( ns, ['std'] )
        self._nsDict[ns].delLink( name )
    
    def delAllLinks( self, ns=None ) :
        '''Deleta ll links in the namespace
        :pasram ns: the namespace name
        :type ns: string
        :rtype: none
        '''
        ns = self._checkNS( ns, ['std'] )
        self._nsDict[ns].replaceLinks( [] )
    
    def dedupLinks( self, ns=None ) :
        '''Removes duplicate namespace names from the links list
        :param ns: the namespace whose link list is to be deduplicated
        :type ns: string
        :rtype: none
        '''
        ns = self._checkNS( ns )
        self._nsDict[ns].dedupLinks()
    
    # file methods
    def addFile( self, name, ns=None ) :
        '''Adds the name of a loaded file to the namespace
        :param name: name of file that was loaded into the namespace
        :type name: string
        :param ns: the name of the target namespace
        :type ns: string  (if None, the current user namespace is used)
        :rtype: none
        '''
        ns = self._checkNS( ns, ['std'] )
        self._nsDict[ns].addFile( name )
    
    def delFile( self, name, ns=None ) :
        '''Removes a file name from the list of files loaded into a namespace.
        :param name: the name of the file
        :type name: string
        :param ns: the name of the target namespace
        :type ns: string  (if None, the current user namespace is used)
        :rtype: none
        '''
        ns = self._checkNS( ns, ['std'] )
        self._nsDict[ns].delFile( name )
    
    def hasFile( self, name, ns=None ) :
        '''
        '''
        ns = self._checkNS( ns, ['std'] )
        return self._nsDict[ns].hasFile( name )
    
    def allFileNames( self, ns=None ) :
        '''Returns a list of all file names in the namespace, ns
        :param ns: name of namespace
        :type ns: string  (if None, the current user namespace is used)
        :rtype: a list of file names
        '''
        ns = self._checkNS( ns, ['std'] )
        return self._nsDict[ns].allFileNames()

    def dedupFiles( self, ns=None ) :
        '''Removes duplicate file names from the files list
        :param ns: the namespace whose file list is to be deduplicated
        :type ns: string
        :rtype: none
        '''
        ns = self._checkNS( ns )
        self._nsDict[ns].dedupFiles()
    
    # execute a word
    def exeqt(self, word ) :
        '''Executes the cat word if it is known to be an executable
        :param word: the cat word
        :type word: string
        :rtype: none
        '''
        wrd = self.getWord( word )
        
        if wrd[0] :
            func = wrd[1][0]
            
            if callable(func) :
                func( self.cat )
            
            else :
                raise ValueError, "cannot execute '%s' (not a built-in)" % word
        
        else :
            raise valueError, "The word '%s' is undefined" % word

    # support routines
    def _formatList( self, theList, across=4 ) :
        '''Formats the list
        :param theList: the list to be formatted for printing
        :type theList: a list
        :param across: the number of list items to be printed across
        :type across: integer
        :rtype: string
        '''
        txt = ""
        
        if len(theList) == 0 :
            return "  _none_\n"
        
        theList = [str(x) for x in theList]
        longest = max( [len(x) for x in theList] )
        i       = 0
           
        for item in theList :
            l        = longest + 2 - len( item )
            fragment = item + " " * l
            txt     += fragment
            i       += 1
            
            if i == across :
                txt += "\n"
                i    = 0
        
        if i > 0 :
            txt += "\n"
        
        return txt
    
    def _printList( self, theList, across=4 ) :
        '''Print the elements in theList'''
        cat.output( self._formatList(theList, across), self.info_colour )
    
    def _dumpList( self, theList, indent=0 ) :
        '''Dump a list'''
        if type(theList) not in [ListType, TupleType] :
            theList = [ theList ]
        
        txt = ""
        
        for item in theList :
            txt += str(item) + "\n"
        
        return txt

    # debugging tools
    def getAllNamespaces( self ) :
        '''Returns all namespace names as as list'''
        keys = self._nsDict.keys()
        keys.sort()
        return keys
    
    def dumpAll( self, what, ns=None ) :
        '''Dumps the contents of the specified dictionary/list of the named namespace
        :param what: the dictionary/list to be dumped
        :type what: string. One of:
                        'words'
                        'vars'
                        'instances'
                        'links'
                        'files'
        :param ns: the name of the target namespace
        :type ns: string
                    if None, the current user namespace is used
                    if 'all' all namespaces are used
        :rtype: none
        '''
        allDicts = ['words', 'vars', 'instances', 'links', 'files']
        
        if ns == 'all' :
            keys = self._nsDict.keys()
            keys.sort()
        
        else :
            keys = [self._checkNS(ns)]
        
        mapping = { 'words'     : '__words__',
                    'vars'      : '__vars__',
                    'instances' : '__inst__',
                    'links'     : '__links__',
                    'files'     : '__loadList__'
                  }
        
        if what == 'all' :
            dicts = allDicts
        
        else :
            if what not in allDicts :
                raise ValueError, "DumpAll: unidentified argument '%s'" % what
            
            dicts = [what]
        
        for item in dicts:
            for ns in keys :
                self.cat.output( "\nDumping  %s in '%s':" % (item, ns), self.info_colour )
                self._nsDict[ns].dump(mapping[item], self.info_colour)
            
            self.cat.output( "" )
