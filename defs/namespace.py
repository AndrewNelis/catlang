"""
    Backup of namespace methods.

    Currently unused.
"""


# namespace methods
def createNS(self, stack):
    '''
    createNS : (string:name -> --)

    desc:
        Creates one or more namespaces from the string on top of the stack
        Note: name may also be of the form name1,name2,name3,... (e.g. 'flow,test)
                or a list  (e.g. ['flow 'test] list

    tags:
        custom,namespace
    '''
    names = stack.pop_list()

    for name in names:
        if name == '':
            continue

        if name in ['', 'std', self.userNS]:
            continue

        elif name in self.NSdict.keys():
            raise ValueError("createNS: The name '%s' is already in use" % name)

        else:
            self.NSdict[name] = {'__vars__': {}, '__links__': [], '__inst__': {}}


def setNS(self, stack):
    '''
    setNS : (string:ns|list:ns -> --)

    desc:
        sets the list of namespaces to be searched to the string on top of the stack
        Note: ns may be of the form name1.name2,name3,...  (e.g. 'flow,predicates)
                or a list (e.g. ['predicates 'flow] list)

    tags:
        custom,namespaces
    '''
    items = stack.pop_list()

    lst = []

    for name in items:
        if name == self.userNS:
            continue

        if name in self.NSdict:
            lst.append(name)

    self.NSdict[self.userNS]['__links__'] = lst


def renameNS(self, stack):
    '''
    renameNS : (string:old string:new -> --)

    desc:
        renames an old namespace to a new name

    tags:
        custom,namespaces
    '''
    new, old = stack.pop2()
    protected = ['std', 'user']

    if old in protected or new in protected:
        raise ValueError("renameNS: Cannot rename 'user' or 'std'")

    elif new in self.NSdict.keys():
        raise ValueError("renameNS: The name '%s' is already in use" % new)

    if old in self.NSdict:
        temp = self.NSdict[old].copy()
        del self.NSdict[old]
        self.NSdict[new] = temp

    if old == self.userNS:
        self.userNS = new


def copyNS(self, stack):
    '''
    copyNS : (string:src string:dest -> --)

    desc:
        copy the src namespace to a new dest

    tags:
        custom,namespace
    '''
    dest, src = stack.pop2()

    if dest in ['std', self.userNS, '']:
        raise ValueError("copyNS: Copying '%s' to '%s' is forbidden!" % (src, dest))

    if src not in self.NSdict.keys():
        raise ValueError("copyNS: No source namespace called '%s'" % src)

    self.NSdict[dest] = self.NSdict[src]


def appendNS(self, stack):
    '''
    appendNS : (string:src string:dest -> --)

    desc:
        append the src namespace to a dest one

    tags:
        custom,namespace
    '''
    dest, src = stack.pop2()

    if dest in ['std', '']:
        raise ValueError, "appendNS: Appending '%s' to '%s' is forbidden!" % (src, dest)

    if dest not in self.NSdict:
        self.NSdict[dest] = {'__vars__': {}, '__links__': [], '__inst__': {}}

    if src not in self.NSdict.keys():
        raise ValueError("appendNS: No namespace called '%s'" % src)

    funcs = self.NSdict[src].items()

    for key, val in funcs:
        if key not in ['__vars__', '__links__', '__inst__']:
            self.NSdict[dest][key] = val

        elif isinstance(self.NSdict[dest][key], dict):
            self.NSdict[dest][key].update(val)

        else:
            l = self.NSdict[dest][key] + val
            self.NSdict[dest][key] = reduce(lambda x, y: x if y in x else x + [y], l, [])


def delNS(self, stack):
    '''
    delNS : (string:name -> --)

    desc:
        Removes the named namespace dictionary

    tags:
        custom,namespaces
    '''
    names = stack.pop_list()

    for ns in names:
        if ns in ['', self.userNS, 'std', 'user']:
            continue

        if ns in self.NSdict:
            del self.NSdict[ns]


def listNS(self, stack):
    '''
    listNS : (-- -> --)

    desc:
        Lists the names of the available namespaces

    tags:
        custom,namespaces
    '''
    names = self.NSdict.keys()
    names.remove('std')
    names.sort()
    self._printList(stack, names)


def getNS(self, stack):
    '''
    getNS : (-- -> list:names)

    desc:
        Pushes a list of the names of the available namespaces onto the stack

    tags:
        custom,namespaces
    '''
    names = self.NSdict.keys()
    names.remove('std')
    names.sort()
    stack.push(names)


def loadNS(self, stack):
    '''
    loadNS : (string:fileName string:nameSpaceName -> --)

    desc:
        Loads the named file of definitions into the specified namespace
        If the namespace does not exist it is created
        If the namespace exists it is added to


    tags:
        custom,namespaces
    '''
    nsName = stack.pop()

    if nsName not in self.NSdict:
        self.NSdict[nsName] = {'__vars__': {}, '__links__': [], '__inst__': {}}

    self._load(stack, True, nsName)


def wordsNS(self, stack):
    '''
    wordsNS : (string:nsName -> --)

    desc:
        Displays on the console the names of all words in a given namespace
        Note: namespace name may be of the form: nsName1,nsName2,...  (e.g. 'test,flow)
                or a list  (e.g. ['test 'flow] list)

    tags:
        custom,namespaces,console
    '''
    nsNames = stack.pop_list()

    for nsName in nsNames:
        if nsName in self.NSdict:
            keys = self.NSdict[nsName].keys()
            keys.sort()

            if '__vars__' in keys:
                keys.remove('__vars__')
                keys.remove('__links__')
                keys.remove('__inst__')

            stack.output("For namespace %s:" % nsName, 'green')
            self._printList(stack, keys)

        else:
            stack.output("No namespace called '%s'" % nsName, 'green')


def purgeNS(self, stack):
    '''
    purgeNS : (string:nsNames -> --)

    desc:
        Removes all definitions from the namespace
        Note: nsNames may be of the form nsName1,nsName2,nsName3,...  (e.g. 'geometry,flow)
                or a list (e.g. ['geometry 'flow] list)

    tags:
        custom,namespaces
    '''
    items = stack.pop_list()

    for ns in items:
        if ns in ['', 'std']:
            continue

        if ns in self.NSdict:
            self.NSdict[ns] = {}


def focusNS(self, stack):
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

    if not isinstance(name, basestring):
        raise ValueError("focusNS: New target namespace name must be a string")

    if name not in self.NSdict:
        raise ValueError("focusNS: No namespace called '%s'" % name)

    self.userNS = name


def showUserNS(self, stack):
    '''
    showUserNS : (-- -> --)
    pwd        : (-- -> --)

    desc:
        pushes the current user namespace onto the stack

    tags:
        custom,namespaces
    '''
    stack.output("  " + self.userNS, 'green')


def getUserNS(self, stack):
    '''
    getUserNS : ('A -> 'A string:namespace)

    desc:
        pushes the name of the currently active namespace onto the stack

    tags:
        custom,namespaces
    '''
    stack.push(self.userNS)


def linkToNS(self, stack):
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
    names = stack.pop_list()

    for name in names:
        if name == self.userNS:
            continue

        if name not in self.NSdict:
            raise ValueError("appendNS: No namespace called '%s'" % name)

        self.NSdict[self.userNS]['__links__'].append(name)


def unlinkNS(self, stack):
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
    names = stack.pop_list()

    for name in names:
        if name in ['std', self.userNS, 'user', '']:
            continue

        if name not in self.NSdict:
            continue

        if name in self.NSdict[self.userNS]['__links__']:
            self.NSdict[self.userNS]['__links__'].remove(name)


def removeWordNS(self, stack):
    '''
    removeWordNS : (string:word string:namespace -> --)

    desc:
        removes the word(s) from the specified namespace
        Note: the word may be of the form word1,word2,...  (e.g. 'dupd,swapd)
                or a list  (e.g. ['dupd 'swapd] list)

    tags:
        custom,namespaces
    '''
    ns = stack.pop()
    names = stack.pop_list()

    if ns not in self.NSdict:
        raise ValueError("removeWordNS: No namespace called '%s'" % ns)

    for word in names:
        if word in ['__vars__', '__links__', '__inst__', '']:
            continue

        if word in self.NSdict[ns]:
            del self.NSdict[ns][word]


def showLinkedNS(self, stack):
    '''
    showLinkedNS : (-- -> --)

    desc:
        lists all the active namespaces (those linked to the user's current namespace)

    tags:
        custom,namespaces
    '''
    stack.output("Linked namespaces:", 'green')
    self._printList(stack, self.NSdict[self.userNS]['__links__'])


def purgeLinksNS(self, stack):
    '''
    purgeLinksNS : (-- -> --)

    desc:
        removes all links from the active user namespace

    tags:
        custom,namespaces
    '''
    self.NSdict[self.userNS]['__links__'] = []
