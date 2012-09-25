# debugging

from cat.namespace import *
ns = NameSpace()

@define(ns, 'dump_ns')
def dumpNS( cat ) :
    '''
    dumpNS : (string:what string:ns -> --)
    
    desc:
        Dumps the specified items of a namespace
        what: the element to dump. One of:
                'all'   -- dumps all of the below
                'words' -- lists all words (w/o documentation)
                'links' -- lists all linked-in namespaces
                'inst'  -- lists all instances
                'files' -- lists all files loaded
                'vars'  -- lists all user-defined variables
        ns: the namespace of interest
                if 'all' -- all namespaces are dumped
                if 'this' -- the current namespace is dumped
                otherwise the named namespace is dumped (providing it exists)
    tags:
        debug
    '''
    nspc, what = cat.stack.pop_2()
    
    if nspc == 'this' :
        nspc = cat.ns.getUserNS()
    
    cat.ns.dumpAll( what, nspc )

@define(ns, 'dump_stack')
def dumpStack( cat ) :
    '''
    #dump : (-- -> --)
    
    desc:
        Non-destructively dumps the entire contents of the stack to the console
        Most useful if stack output in the REPL is turned off
    tags:
        debug,console,stack,dump
    '''
    cat.output( str(cat.stack), cat.ns.info_colour )

@define(ns, 'pdb')
def _pdb( cat ) :
    '''
    pdb : (-- -> --)
    
    desc:
        Enters pdb
        Set breakpoints when pdb has been entered
    tags:
        custom,system,debugging.pdb
    '''
    import pdb
    
    pdb.set_trace()

@define(ns, 'trace')
def trace( cat ) :
    '''
    trace: (-- -> --)
    
    desc:
        toggles the global traceing flag to enable simple tracing of function
        execution.
    tags:
        custom,debugging,trace
    '''
    cat.toggle_trace()


def _returnNS() :
    return ns
