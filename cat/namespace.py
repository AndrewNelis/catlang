# NameSpace class wraps low-level functionality
from termcolor import colored

class NameSpace:
    def __init__(self):
        self._ns = { '__words__' : { },
                     '__vars__'  : { },
                     '__inst__'  : { },
                     '__links__' : [ ],
                     '__loadList__' : [ ] }
    
    # general searching facility for internal dictionaries
    def _fetchFromDict( self, item, dict ) :
        if not isinstance(item, basestring) :
            return (False, None)
        
        if item in self._ns[dict] :
            return (True, self._ns[dict][item])
        
        else :
            return (False, None)
    
    # manipulate WORDS
    # note: a directory entry for words looks like this:
    #   <name of word> : (<function>, <documentation>)
    def addWord( self, word, value ) :
        self._ns['__words__'][word] = value
    
    def getWord( self, word ) :
        return self._fetchFromDict(word, '__words__')
    
    def delWord( self, word ) :
        if word in self._ns['__words__'] :
            del self._ns['__words__'][word]
    
    def hasWord( self, name ) :
        return self._fetchFromDict(name, '__words__')[0]
    
    def allWordNames( self ) :
        return self._ns['__words__'].keys()
    
    def updateWords( self, dict ) :
        self._ns['__words__'].update( dict )
    
    def delAllWords( self ) :
        self._ns['__words__'] = { }
    
    # manipulate VARIABLES
    def addVar(self, var, value ) :
        self._ns['__vars__'][var] = value
    
    def getVar( self, var ) :
        return self._fetchFromDict(var, '__vars__')
    
    def delVar( self, var ) :
        if var in self._ns['__vars__'] :
            del self._ns['__vars__'][var]
    
    def hasVar( self, name ) :
        return self._fetchFromDict( name, '__vars__' )[0]
    
    def allVarNames( self ) :
        return self._ns['__vars__'].keys()
    
    # manipulate INSTANCES
    def addInst( self, inst, value ) :
        self._ns['__inst__'][inst] = value
    
    def getInst( self, inst ) :
        return self._fetchFromDict(inst, '__inst__')
    
    def hasInst( self, name ) :
        return self._fetchFromDict(name, '__inst__')[0]
    
    def delInst( self, inst ) :
        if inst in self._ns['__inst__'] :
            del self._ns['__inst__'][inst]
    
    def allInstNames( self ) :
        return self._ns['__inst__'].keys()
    
    def allInst( self ) :
        return self._ns['__inst__']
    
    # manipulate LINKS
    def addLink( self, link ) :
        if link not in self._ns['__links__'] :
            self._ns['__links__'].append( link )
    
    def hasLink( self, linkName ) :
        return linkName in self._ns['__links__']
    
    def getLinks( self ) :
        return self._ns['__links__']
    
    def getLink( self, n ) :
        if len(self._ns['__links__']) > abs(n) :
            return self._ns['__links__'][n]
        
        else :
            raise IndexError, "Index '%d' to links is out of range"
   
    def popLink( self ) :
        return self._ns['__links__'].pop()
    
    def peekLink( self ) :
        return self._ns['__links__'][-1]
    
    def delLink( self, link ) :
        if link in self._ns['__links__'] :
            self._ns['__links__'].remove( link )
    
    def replaceLinks( self, newList ) :
        if isinstance(newList, (list, tuple)) :
            self._ns['__links__'] = list( newList )
        
        else :
            self._ns['__links__'] = [newList]
    
    def appendLinks( self, links ) :
        self._ns['__links__'].extend( links )
    
    def dedupLinks( self ) :
        lst = reduce( lambda y,x: y + [x] if x not in y else y, self.getLinks(), [] )
        self.replaceLinks( lst )
    
    # manipulate FILES in the loadList
    def addFile( self, name ) :
        if name not in self._ns['__loadList__'] :
            self._ns['__loadList__'].append( name )
    
    def getLoadList( self ) :
        return self._ns['__loadList__']
    
    def replaceLoadList( self, newList ) :
        if isinstance(newList, (list, tuple)) :
            self._ns['__loadList__'] = list( newList )
        
        else :
            self._ns['__loadList__'] = [newList]
    
    def delFile( self, fileName ) :
        if fileName in self._ns['__loadList__'] :
            self._ns['__loadList__'].remove( fileName )
    
    def hasFile( self, fileName ) :
        return fileName in self._ns['__loadList__']
    
    def allFileNames( self ) :
        return self._ns['__loadList__']
    
    def dedupFiles( self ) :
        lst = reduce( lambda y,x: y + [x] if x not in y else y, self.getLoadList(), [] )
        self.replaceLoadList( lst )
    
    # searching
    def searchFor( self, name, inObj='words' ) :
        if inObj == 'words' :
            return self.hasWord( name )
        
        elif inObj == 'vars' :
            return self.hasVar( name )
        
        elif inObj == 'instances' :
            return self.hasInst( name )
        
        elif inObj == 'links' :
            return self.hasLink( name )
        
        elif inObj == 'files' :
            return self.hasFile( name )
        
        else :
            raise ValueError, "'%s' is not one of 'words','vars','instances','links','files'" % inObj
    
    def getValueOf( self, name, inObj='words' ) :
        if inObj == 'words' :
            return self.getWord( name )
        
        elif inObj == 'vars' :
            return self.getVar( name )
        
        elif inObj == 'instances' :
            return self.getInst( name )
        
        else :
            raise ValueError, "'%s' is not one of 'words','vars','instances'" % inObj
    
    # special actions
    def as_wordDict(self):
        return self._ns['__words__']
    
    def as_varDict( self ) :
        return self._ns['__vars__']
    
    def dump( self, what, color ) :
        if what in ('__words__', '__vars__', '__inst__') :
            keys = self._ns[what].keys()
            keys.sort()
            
            if len(keys) == 0 :
                print colored("_EMPTY_", color )
            
            else :            
                for key in keys :
                    if what == '__words__' :
                        print colored("  %s: %s" % (key, self._ns[what][key][0]), color )
                    
                    else :
                        print colored( "  %s: %s" % (key, self._ns[what][key]), color )
        
        elif what in ('__links__', '__loadList__') :
            if len(self._ns[what]) == 0 :
                print colored( "_EMPTY_", color )
            
            else :
                print colored( self._ns[what], color )
        
        else :
            raise ValueError, "'%s' cannot be dumped" % what


def define(ns, words):
    """Decorator that inserts the wrapped function into a NameSpace (ns) as <word>"""
    def _decorator(func):
        if isinstance(words, basestring) :
            wordList = words.split(",")
        
        else :
            wordList = words
        
        for word in wordList :
            ns.addWord(word.strip(), (func, func.__doc__))
        
        return func

    return _decorator
