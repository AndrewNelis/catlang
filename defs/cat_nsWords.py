# namespace methods

from cat.namespace import *
ns = NameSpace()

@define(ns, 'create_ns')
def createNS( cat ) :
    '''
    create_ns : (string:name -> --)
    
    desc:
        Creates one or more namespaces from the string on top of the stack
        Note: name may also be of the form name1,name2,name3,... (e.g. 'flow,test)
              or a list  (e.g. ['flow 'test] list
    tags:
        namespace,create,new,ns
    '''
    names = cat.stack.pop_list()
    
    for name in names :
        if name in ['std', cat.ns.getUserNS()] :
            continue
        
        elif cat.ns.isNS(name) :
            raise ValueError, "createNS: The name '%s' is already in use" % name
        
        else :
            cat.ns.createNS( name )

@define(ns, 'set_ns')
def setNS( cat ) :
    '''
    set_ns : (string:ns|list:ns -> --)
    
    desc:
        sets the list of namespaces to be searched, as found in the currently active namespace,
        to the string on top of the stack. This is a replacement action.
        Note: ns may be of the form name1,name2,name3,...  (e.g. 'flow,predicates)
              or a list (e.g. ['predicates 'flow] list)
        ns: the namespace or list of namespaces to be used
    tags:
        namespaces,set,list,ns
    '''
    names  = cat.stack.pop_list()
    userNS = cat.ns.getUserNS()
    lst    = []
    
    for name in names :
        if name in [userNS, 'std'] or not cat.ns.isNS(name):
            continue
        
        lst.append( name )
    
    cat.ns.setUserLinksNS( lst )

@define(ns, 'is_ns')
def is_ns( cat ) :
    '''
    is_ns : (string:ns_name -> boolean:TorF)
    
    desc:
        Pushes True onto the stack if the word on top of the stack is the name of a namespace,
        otherwise False is pushed onto the stack.
        
        Example: 'user is_ns => True
    tags:
        namespaces,exists
    '''
    ns = cat.stack.pop()
    cat.stack.push( cat.ns.isNS(ns) )

@define(ns, 'rename_ns,mv')
def renameNS( cat ) :
    '''
    rename_ns : (string:old string:new -> --)
    mv        : (string:old string:new -> --)
    
    desc:
        renames an old namespace to a new name
        old: the current name of some namespace
        new: the new name for the namespace
    tags:
        namespaces,rename,mv,ns
    '''
    new, old  = cat.stack.pop_2()
    protected = ['std', 'user']
    
    if old in protected or new in protected :
        raise ValueError, "renameNS: Cannot rename 'user' or 'std'"
    
    cat.ns.renameNS( new, old )

@define(ns, 'copy_ns')
def copyNS( cat ) :
    '''
    copy_ns : (string:src string:dest -> --)
    
    desc:
        copy the src namespace to a new dest
        src: the name of an existing (source) namespace
        dest: the name of an existing (target) namespace
    tags:
        namespace,copy,ns
    '''
    dest, src = cat.stack.pop_2()
    
    if dest == src :
        return
    
    if dest in ['std', ''] :
        raise ValueError, "copyNS: Copying '%s' to '%s' is forbidden!" % (src, dest)
    
    cat.ns.copyNS( src, dest )

@define(ns, 'append_ns')
def appendNS( cat ) :
    '''
    append_ns : (string:src string:dest -> --)
    
    desc:
        append the src namespace to a dest one
        src: the name of an existing (source) namespace
        dest: the name of an existing (target) namespace
    tags:
        namespace,append,ns
    '''
    dest, src = cat.stack.pop_2()
    
    if dest == src :
        return
    
    if dest in ['std', ''] :
        raise ValueError, "appendNS: Appending '%s' to '%s' is forbidden!" % (src, dest)
    
    if not cat.ns.isNS(dest) :
        cat.ns.createNS( dest )
    
    cat.ns.appendNS( src, dest )

@define(ns, 'del_ns,rm')
def delNS( cat ) :
    '''
    del_ns : (string:name -> --)
    rm     : (string:name -> --)
    
    desc:
        Removes the named namespace dictionary
        names may be a string of the form:
            <simple name>
            <simple name>,<simple name>,...
        or a list of names: [<simple name>, <simple name>, ...)
        name: the name(s) of namespace(s) to be deleted
        
        Example: 'TS del_ns
                 ['Test, 'TS] list rm
    tags:
        namespace,delete,ns,rm
    '''
    names = cat.stack.pop_list()
    
    for ns in names :
        if cat.ns.isNS( ns ) :
            cat.ns.delNS( ns )
            cat.ns.removeAllLinkRefsNS( ns )

@define(ns, 'show_all_ns')
def showAllNS( cat ) :
    '''
    show_all_ns : (-- -> --)
    
    desc:
        Shows the names of ALL the available namespaces
        
        Example: show_all_ns
    tags:
        namespace,names,display,ns,show
    '''
    names = cat.ns.listAllNS()
    names.sort()
    cat.output( cat.ns._formatList(names), cat.ns.info_colour )

@define(ns, "show_linked_ns")
def showNSLinks( cat ) :
    '''
    show_linked_ns : (-- -> --)
    
    desc:
        Displays all namespace links in the currently active namespace
        
        Example: show_linked_ns
    tags:
        namespace,link,display,ns
    '''
    links = cat.ns.getLinksNS()
    links.sort()
    cat.output( cat.ns._formatList(links), cat.ns.info_colour )

@define(ns, 'get_all_ns')
def getNS( cat ) :
    '''
    get_all_ns : (-- -> list:names)
    
    desc:
        Pushes a list of the names of the available namespaces onto the stack
        names: the list of namespace names
        
        Example: get_all_ns => ['user, 'TS]
    tags:
        namespace,names,list,ns
    '''
    names = cat.ns.listAllNS()
    names.sort()
    cat.stack.push( names )

@define(ns, 'load_ns')
def loadNS( cat ) :
    '''
    load_ns : (string:fileName string:namespaceName -> --)
    
    desc:
        Loads the named file of definitions into the specified namespace
        If the namespace does not exist it is created
        If the namespace exists it is added to
        fileName: the path to the file of cat definitions to be loaded
        namespaceName: the name of the namespace into  which to load the definitions
        
        Example: global:CatDefs 'standard-core.cat + 'core load_ns
    tags:
        namespace,definition,cat,ns,load
    '''
    nsName          = cat.stack.pop()
    cat.ns.targetNS = nsName
    
    if not cat.ns.isNS(nsName) :
        cat.ns.createNS(nsName)
    
    load = cat.ns.getWord('load')[1][0]
    load( cat, True, nsName )
    cat.ns.targetNS = ''

@define(ns, 'words_in_ns')
def wordsInNS( cat ) :
    '''
    words_in_ns : (string:nsName -> --)
    
    desc:
        Displays on the console the names of all words in a given namespace
        Note: namespace name may be of the form: nsName1,nsName2,...  (e.g. 'test,flow)
              or a list  (e.g. ['test 'flow] list)
        nsname: name of namespace whose words are to be displayed
        
        Example: 'TS words_in_ns
    tags:
        namespace,console,words,display,ns
    '''
    nsNames = cat.stack.pop_list()
    i_c     = cat.ns.info_colour
    
    for nsName in nsNames :
        keys = cat.ns.allWordNames( nsName )
        keys.sort()
        cat.output( "For namespace '%s':" % nsName, i_c )
        cat.output(cat.ns._formatList(keys, across=3), i_c )

@define(ns, 'links_in_ns')
def linksInNS( cat ) :
    '''
    links_in_ns : (string:nsName -> --)
    
    desc:
        Displays on the console the names of all links in a given namespace
        Note: namespace name may be of the form: nsName1,nsName2,...  (e.g. 'test,flow)
              or a list  (e.g. ['test 'flow] list)
        nsname: name of namespace whose links are to be displayed
        
        Example 'user,TS links_in_ns
    tags:
        namespace,console,link,display,ns
    '''
    nsNames = cat.stack.pop_list()
    i_c     = cat.ns.info_colour
    
    for nsName in nsNames :
        keys = cat.ns.getLinksNS( nsName )
        keys.sort()
        cat.output( "For namespace '%s':" % nsName, i_c )
        cat.output(cat.ns._formatList(keys), i_c )

@define(ns, 'show_linked_in_ns,ls')
def showLinkedNS( cat ) :
    '''
    show_linked_in_ns : (-- -> --)
    ls                : (-- -> --)
    
    desc:
        lists all the active namespaces (those linked to the user's current namespace)
        
        Example: show_linked_in_ns
                 ls
    tags:
        namespace,link,display,ns,ls
    '''
    cat.output( "Linked namespaces:", cat.ns.info_colour )
    links = cat.ns.getLinks()
    links.sort()
    cat.output( cat.ns._formatList(links), cat.ns.info_colour )

@define(ns, 'purge_ns')
def purgeNS( cat ) :
    '''
    purge_ns : (string:nsNames -> --)
    
    desc:
        Removes all definitions from the namespace
        Note: nsNames may be of the form nsName1,nsName2,nsName3,...  (e.g. 'geometry,flow)
              or a list (e.g. ['geometry 'flow])
        nsNames: the name(s) of the namespaces to be purged of their words
        
        Example: 'TS purge_ns
    tags:
        namespace,purge,words,delete,ns
    '''
    items = cat.stack.pop_list()
    
    for ns in items :
        if ns != 'std' and ns not in cat.ns.defns :
            cat.ns.delAllWords( ns )

@define(ns, 'focus_ns,cd')
def focusNS( cat ) :
    '''
    focus_ns : (string:name -> --)
    cd       : (string:name -> --)
    
    desc:
        Changes the working (active) namespace to the one given by
        the string on top of the stack
        name: the name of a namespace that will become the currently active one
        
        Example: 'TS focus_ns
                 'user cd
    tags:
        namespace,focus,user,ns,cd
    '''
    name = cat.stack.pop()
    
    if not isinstance(name, basestring) :
        raise ValueError, "focusNS: New target namespace name must be a string"
    
    if not cat.ns.isNS(name) :
        raise ValueError, "focusNS: No namespace called '%s'" % name
    
    cat.ns.changeUserNS( name )

@define(ns, 'show_user_ns,pwd')
def showUserNS( cat ) :
    '''
    show_user_ns : (-- -> --)
    pwd          : (-- -> --)
    
    desc:
        Displays the current user namespace
        
        Example: show_user_ns
                 pwd
    tags:
        namespace,active,user,display,ns,pwd
    '''
    cat.output( "  " + cat.ns.getUserNS(), cat.ns.info_colour )

@define(ns, 'get_user_ns,cwd')
def getUserNS( cat ) :
    '''
    get_user_ns : (-- -> string:namespace)
    cwd         : (-- -> string:namespace)
    
    desc:
        Pushes the name of the currently active namespace onto the stack
        namespace: the name of the currently ative namespace
        
        Example: get_user_ns => 'user
                 cdw         => 'work_2
    tags:
        namespace,user,active,ns,cwd
    '''
    cat.stack.push( cat.ns.getUserNS() )

@define(ns, 'link_to_ns,ln')
def linkToNS( cat ) :
    '''
    link_to_ns : (string:namespaceName -> --)
    ln         : (string:namespaceName -> --)
    
    desc:
        appends the namespace name on top of the stack to the active namespace's link list
        Note: name may be of the form: nsName1,nsName2,...  (e.g. 'math,geometry)
              or a list (e.g. ['math 'shuffle] list)
        namespaceName: the name of the namespace to be appended to currently active one
        
        Example: 'TS ln
                 'work_1,work_2 link_to_ns
    tags:
        namespace,append,link,ns,ln
    '''
    names  = cat.stack.pop_list()
    userNS = cat.ns.getUserNS()
    
    for name in names :
        if name in ('std', userNS) or name in cat.ns.defns :
            continue
        
        cat.ns.addLink( name )

@define(ns, 'unlink_ns')
def unlinkNS( cat ) :
    '''
    unlink_ns : (string:name -> --)
    rm        : (string:name -> --)
    
    desc:
        Removes the namespace whose name is on top of the stack
        from the list of namespaces associated with the
        currently active user namespace. The name may be of the form
        'name1,name2,... or a list of names
        name: the name(s) of namespace(s) to be unlinked from the currently active one
        
        Example: 'work_1,work_2 unlink_ns
                 'TS rm
    tags:
        namespace,remove,unlink,ns,rm
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

@define(ns, 'remove_word_ns')
def removeWordNS( cat ) :
    '''
    remove_word_ns : (string:word string:namespace -> --)
    
    desc:
        Removes the word(s) from the specified namespace
        Note: the word may be of the form word1,word2,...  (e.g. 'dupd,swapd)
              or a list  (e.g. ['dupd 'swapd] list)
        word: the name of the word to be removed
        namespace: the name of the namespace from which the word is to be removed
        
        Example: 'swons,dip2 'TS remove_word
    tags:
        namespace,word,remove,delete,ns
    '''
    ns    = cat.stack.pop()
    names = cat.stack.pop_list()
    
    for word in names :
        if word.count(":") == 1 :
            nspc, name = word.split(":")
        
        else :
            nspc = ns
        
        cat.ns.delWord( name, nspc )

@define(ns, 'purge_linked_ns')
def purgeLinksNS( cat ) :
    '''
    purge_linked_ns : (-- -> --)
    
    desc:
        Removes all links from the active user namespace
        
        Example: purge_linked_ns
    tags:
        namespace,purge,link,ns
    '''
    cat.ns.delAllLinks()

def _returnNS() :
    return ns
