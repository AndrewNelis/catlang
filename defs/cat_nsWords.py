# namespace methods

from cat.namespace import *
ns = NameSpace()

@define(ns, 'createNS')
def createNS( cat ) :
    '''
    createNS : (string:name -> --)
    
    desc:
        Creates one or more namespaces from the string on top of the stack
        Note: name may also be of the form name1,name2,name3,... (e.g. 'flow,test)
              or a list  (e.g. ['flow 'test] list
    
    tags:
        level2,namespace,create,new
    '''
    names = cat.stack.pop_list()
    
    for name in names :
        if name in ['std', cat.ns.getUserNS()] :
            continue
        
        elif cat.ns.isNS(name) :
            raise ValueError, "createNS: The name '%s' is already in use" % name
        
        else :
            cat.ns.createNS( name )

@define(ns, 'setNS')
def setNS( cat ) :
    '''
    setNS : (string:ns|list:ns -> --)
    
    desc:
        sets the list of namespaces to be searched, as found in the currently active namespace,
        to the string on top of the stack. This is a replacement action.
        Note: ns may be of the form name1,name2,name3,...  (e.g. 'flow,predicates)
              or a list (e.g. ['predicates 'flow] list)
        ns: the namespace or list of namespaces to be used
    tags:
        namespaces,set,list
    '''
    names  = cat.stack.pop_list()
    userNS = cat.ns.getUserNS()
    lst    = []
    
    for name in names :
        if name in [userNS, 'std'] or not cat.ns.isNS(name):
            continue
        
        lst.append( name )
    
    cat.ns.setUserNS( lst )

@define(ns, 'renameNS,mv')
def renameNS( cat ) :
    '''
    renameNS : (string:old string:new -> --)
    mv       : (string:old string:new -> --)
    
    desc:
        renames an old namespace to a new name
        old: the current name of some namespace
        new: the new name for the namespace
    tags:
        namespaces,rename,mv
    '''
    new, old  = cat.stack.pop_2()
    protected = ['std', 'user']
    
    if old in protected or new in protected :
        raise ValueError, "renameNS: Cannot rename 'user' or 'std'"
    
    cat.ns.renameNS( new, old )

@define(ns, 'copyNS')
def copyNS( cat ) :
    '''
    copyNS : (string:src string:dest -> --)
    
    desc:
        copy the src namespace to a new dest
        src: the name of an existing (source) namespace
        dest: the name of an existing (target) namespace
    tags:
        namespace,copy
    '''
    dest, src = cat.stack.pop_2()
    
    if dest == src :
        return
    
    if dest in ['std', ''] :
        raise ValueError, "copyNS: Copying '%s' to '%s' is forbidden!" % (src, dest)
    
    cat.ns.copyNS( src, dest )

@define(ns, 'appendNS')
def appendNS( cat ) :
    '''
    appendNS : (string:src string:dest -> --)
    
    desc:
        append the src namespace to a dest one
        src: the name of an existing (source) namespace
        dest: the name of an existing (target) namespace
    tags:
        namespace,append
    '''
    dest, src = cat.stack.pop_2()
    
    if dest == src :
        return
    
    if dest in ['std', ''] :
        raise ValueError, "appendNS: Appending '%s' to '%s' is forbidden!" % (src, dest)
    
    if not cat.ns.isNS(dest) :
        cat.ns.createNS( dest )
    
    cat.ns.appendNS( src, dest )

@define(ns, 'delNS,rm')
def delNS( cat ) :
    '''
    delNS : (string:name -> --)
    
    desc:
        Removes the named namespace dictionary
        names may be a string of the form:
            <simple name>
            <simple name>,<simple name>,...
        or a list of names: (<simple name>, <simple name>, ...)
        name: the name(s) of namespace(s) to be deleted
    tags:
        namespace,delete
    '''
    names = cat.stack.pop_list()
    
    for ns in names :
        if cat.ns.isNS( ns ) :
            cat.ns.delNS( ns )
            cat.ns.removeAllLinkRefsNS( ns )

@define(ns, 'showAllNS')
def showAllNS( cat ) :
    '''
    showAllNS : (-- -> --)
    
    desc:
        Shows the names of ALL the available namespaces
    tags:
        namespace,names,display
    '''
    names = cat.ns.listAllNS()
    names.sort()
    cat.output( cat.ns._formatList(names), 'green' )

@define(ns, "showLinksNS")
def showNSLinks( cat ) :
    '''
    showLinksNS : (-- -> --)
    
    desc:
        Displays all namespace links in the currently active namespace
    tags:
        namespaces,links,display
    '''
    links = cat.ns.getLinksNS()
    links.sort()
    cat.output( cat.ns._formatList(links), 'green' )

@define(ns, 'getAllNS')
def getNS( cat ) :
    '''
    getAllNS : (-- -> list:names)
    
    desc:
        Pushes a list of the names of the available namespaces onto the stack
        names: the list of namespace names
    tags:
        namespace,names,list
    '''
    names = cat.ns.listAllNS()
    names.sort()
    cat.stack.push( names )

@define(ns, 'loadNS')
def loadNS( cat ) :
    '''
    loadNS : (string:fileName string:namespaceName -> --)
    
    desc:
        Loads the named file of definitions into the specified namespace
        If the namespace does not exist it is created
        If the namespace exists it is added to
        fileName: the path to the file of cat definitions to be loaded
        namespaceName: the name of the namespace into  which to load the defintions
    tags:
        namespaces,definitions,cat
    '''
    nsName          = cat.stack.pop()
    cat.ns.targetNS = nsName
    
    if not cat.ns.isNS(nsName) :
        cat.ns.createNS(nsName)
    
    load = cat.ns.getWord('load')[1][0]
    load( cat, True, nsName )
    cat.ns.targetNS = ''

@define(ns, 'wordsInNS')
def wordsInNS( cat ) :
    '''
    wordsNS : (string:nsName -> --)
    
    desc:
        Displays on the console the names of all words in a given namespace
        Note: namespace name may be of the form: nsName1,nsName2,...  (e.g. 'test,flow)
              or a list  (e.g. ['test 'flow] list)
        nsname: name of namespace whose words are to be displayed
    tags:
        namespace,console,words,display
    '''
    nsNames = cat.stack.pop_list()
    
    for nsName in nsNames :
        keys = cat.ns.allWordNames( nsName )
        keys.sort()
        cat.output( "For namespace %s:" % nsName, 'green' )
        cat.output(cat.ns._formatList(keys), 'green' )

@define(ns, 'linksInNS')
def linksInNS( cat ) :
    '''
    linksNS : (string:nsName -> --)
    
    desc:
        Displays on the console the names of all links in a given namespace
        Note: namespace name may be of the form: nsName1,nsName2,...  (e.g. 'test,flow)
              or a list  (e.g. ['test 'flow] list)
        nsname: name of namespace whose links are to be displayed
    tags:
        namespace,console,links,display
    '''
    nsNames = cat.stack.pop_list()
    
    for nsName in nsNames :
        keys = cat.ns.getLinksNS( nsName )
        keys.sort()
        cat.output( "For namespace %s:" % nsName, 'green' )
        cat.output(cat.ns._formatList(keys), 'green' )

@define(ns, 'showLinkedInNS,ls')
def showLinkedNS( cat ) :
    '''
    showLinkedInNS : (-- -> --)
    ls             : (-- -> --)
    
    desc:
        lists all the active namespaces (those linked to the user's current namespace)
    tags:
        namespace,links,display
    '''
    cat.output( "Linked namespaces:", 'green' )
    links = cat.ns.getLinks()
    links.sort()
    cat.output( cat.ns._formatList(links), 'green' )

@define(ns, 'purgeNS')
def purgeNS( cat ) :
    '''
    purgeNS : (string:nsNames -> --)
    
    desc:
        Removes all definitions from the namespace
        Note: nsNames may be of the form nsName1,nsName2,nsName3,...  (e.g. 'geometry,flow)
              or a list (e.g. ['geometry 'flow])
        nsNames: the name(s) of the namespaces to be purged of their words
    tags:
        namespace,purge,words,delete
    '''
    items = stack.pop_list()
    
    for ns in items :
        if ns != 'std' and ns not in cat.ns.defns :
            cat.ns.delAllWords( ns )

@define(ns, 'focusNS,cd')
def focusNS( cat ) :
    '''
    focusNS : (string:name -> --)
    cd      : (string:name -> --)
    
    desc:
        Changes the working (active) namespace to the one given by
        the string on top of the stack
        name: the name of a namespace that will become the currently active one
    tags:
        namespace,focus,user
    '''
    name = cat.stack.pop()
    
    if not isinstance(name, basestring) :
        raise ValueError, "focusNS: New target namespace name must be a string"
    
    if not cat.ns.isNS(name) :
        raise ValueError, "focusNS: No namespace called '%s'" % name
    
    cat.ns.changeUserNS( name )

@define(ns, 'showUserNS,pwd')
def showUserNS( cat ) :
    '''
    showUserNS : (-- -> --)
    pwd        : (-- -> --)
    
    desc:
        Displays the current user namespace
    tags:
        namespace,active,user,display
    '''
    cat.output( "  " + cat.ns.getUserNS(), 'green' )

@define(ns, 'getUserNS')
def getUserNS( cat ) :
    '''
    getUserNS : (-- ->  string:namespace)
    
    desc:
        Pushes the name of the currently active namespace onto the stack
        namespace: the name of the currently ative namespace
    tags:
        namespace,user,active
    '''
    cat.stack.push( cat.ns.getUserNS() )

@define(ns, 'linkToNS,ln')
def linkToNS( cat ) :
    '''
    linkToNS : (string:namespaceName -> --)
    ln       : (string:namespaceName -> --)
    
    desc:
        appends the namespace name on top of the stack to the active namespace's link list
        Note: name may be of the form: nsName1,nsName2,...  (e.g. 'math,geometry)
              or a list (e.g. ['math 'shuffle] list)
        namespaceName: the name of the namespace to be appended to currently active one
    tags:
        namespace,append,link
    '''
    names  = cat.stack.pop_list()
    userNS = cat.ns.getUserNS()
    
    for name in names :
        if name in ('std', userNS) or name in cat.ns.defns :
            continue
        
        cat.ns.addLink( name )

@define(ns, 'unlinkNS')
def unlinkNS( cat ) :
    '''
    unlinkNS : (string:name -> --)
    rm       : (string:name -> --)
    
    desc:
        removes the namespace whose name is on top of the stack
        from the list of namespaces associated with the
        currently active user namespace. The name may be of the form
        'name1,name2,... or a list of names
        name: the name(s) of namespace(s) to be unlinked from the currently active one
    tags:
        namespace,remove,unlink
    '''
    names  = cat.stack.pop_list()
    userNS = cat.ns.getUserNS()
    
    for name in names :
        if name.count(":") == 1 :
            ns, name = name.split(":")
        
            if ns in ['std', userNS, 'user'] or ns in cat.ns.defns :
                continue
        
        else :
            ns = None
        
        cat.ns.delLink( name, ns )

@define(ns, 'removeWordNS')
def removeWordNS( cat ) :
    '''
    removeWordNS : (string:word string:namespace -> --)
    
    desc:
        Removes the word(s) from the specified namespace
        Note: the word may be of the form word1,word2,...  (e.g. 'dupd,swapd)
              or a list  (e.g. ['dupd 'swapd] list)
        word: the name of the word to be removed
        namespace: the name of the namespace from which the word is to be removed
    tags:
        namespace,word,remove,delete
    '''
    ns    = cat.stack.pop()
    names = cat.stack.pop_list()
    
    for word in names :
        if word.count(":") == 1 :
            nspc, name = word.split(":")
        
        else :
            nspc = ns
        
        cat.ns.delWord( name, nspc )

@define(ns, 'purgeLinkedNS')
def purgeLinksNS( cat ) :
    '''
    purgeLinksNS : (-- -> --)
    
    desc:
        Removes all links from the active user namespace
    tags:
        namespace,purge,links
    '''
    cat.ns.delAllLinks()

def _returnNS() :
    return ns
