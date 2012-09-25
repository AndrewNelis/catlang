# level1 definitions (control, iteration)

from cat.namespace import *
import re
ns = NameSpace()

@define(ns, 'if')
def _if( cat ) :
    '''
    if : (bool:condition [true_func] [false_func] -> any:ans)
    
    desc:
        Executes one predicate or another whether the condition is true
        condition: the logical condition that 'if' will test
        true_func: the function to be executed if the condition is True
        false_func: the function to be executed if the condition is False
        ans: the result of the functions (may be no value pushed onto the stack)
    tags:
        control,function,condition,if
    '''
    ffalse, ftrue, cond = cat.stack.pop_n(3)
    
    if cond:
        cat.stack.push( ftrue )
    
    else:
        cat.stack.push( ffalse )
    
    cat.eval( 'apply' )

@define(ns, 'while')
def _while( cat ) :
    '''
    while : (func:exec_func func:test_cond -> any:ans)
    
    desc:
        executes a block of code (function) repeatedly until the condition returns false
        Example:  0 4 [swap inc swap] [dec gez] while -> 4 -1
        exec_func: the function to execute repeatedly
        test_cond: the test condition
        ans: the result of executing the exec_func (may result in nothing pushed onto the stack)
    tags:
        control,iteration,while
    '''
    b, f = cat.stack.pop_2()
    
    while True :
        cat.eval( b )
        
        if not cat.stack.pop() :
            break
        
        else :
            cat.eval( f )

@define(ns, 'repeat')
def repeat( cat ) :
    '''
    repeat : (func:exec_func int:n -> any:ans)

    desc:
        Executes a loop a fixed number of times
        Semantics: $A [$B] $c repeat == $A $c eqz [] [$B $c dec] if
        exec_func: the function to be repeated
        n: number of times to repeat the function
        ans: the result of executing exec_func (may have no staak effect)
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
        control,iteration,repeat
    '''
    n, f = cat.stack.pop_2()
    n    = abs( int(n) )
    
    while n > 0 :
        cat.eval( f )
        n -= 1

@define(ns, 'foreach,for_each,for')
def foreach( cat ) :
    '''
    foreach : (list:args func:exec_func -> any:ans)

    desc:
        Executes a function with each item in the list, and consumes the list.
        Semantics: $A $b [$C] foreach == $A $b empty not [uncons pop [$C] foreach] [pop] if }
        args: a list of arguments
        exec_func: the function to be applied to each element of the argument list
        ans: result of the exec_func (may be no stack effect)
    test:
        in:
            0 [1 2 3 4] list [add] foreach
        out:
            10
    
    tags:
        control,iteration,for
    '''
    f, a = cat.stack.pop_2()
    
    for x in a :
        cat.stack.push( x )
        cat.eval( f )

@define(ns, 'pass')
def _pass( cat ) :
    '''
    pass : (-- -> --)
    
    desc:
        Does nothing (no-op)
    
    tags:
        control
    '''
    return

@define(ns, 'halt')
def halt( cat ) :
    '''
    "halt : (A int:error_code -> A )
    
    desc:
        Halts the program with an error code by raising an exception
        error_code: an arbitrary integer error code
    tags:
        control,exception,halt
    '''
    n = int( cat.stack.pop() )
    raise Exception, "halt: Program halted with error code %d" % n

@define(ns, 'dispatch1')
def dispatch1( cat ) :
    '''
    dispatch1 : (list:functions any:arg -> any:ans)
    
    desc:
        dynamically dispatches a function depending on the object on top of the stack
        E.g. (3 [[dup] 1 [drop] 2 [swap] 3] list 1 dispatch1 -> 3 3)
        functions: the list of "indexed" functions to be executed
        arg: the selector "index"
        ans: the result of executing the function associated with the selector arg
    tags:
        control,functions,dispatch
    '''
    obj, lst = cat.stack.pop_2()
    
    for i in range(len(lst) / 2) :
        t = lst[2 * i + 1]
        f = lst[2 * i]
        
        if t == obj :
            cat.eval( f )
            return
    
    raise Exception, "dispatch1: Could not dispatch function"

@define(ns, 'dispatch2')
def dispatch2( cat ) :
    '''
    dispatch2 : (list:functions any:arg -> any:ans)
    
    desc:
        dynamically dispatches a function depending on the object on top of the stack
        E.g. (3 [1 [dup] 2 [drop] 3 [swap]] list 1 dispatch2 -> 3 3)
        functions: the list of "indexed" functions to be executed
        arg: the selector "index"
        ans: the result of executing the function associated with the selector arg
    tags:
        control,functions
    '''
    obj, lst = cat.stack.pop_2()
    
    for i in range(len(lst) / 2) :
        f= lst[2 * i + 1]
        t = lst[2 * i]
        
        if t == obj :
            cat.eval( f )
            return
    
    raise Exception, "dispatch2: Could not dispatch function"

@define(ns, 'try_catch')
def try_catch( cat ) :
    '''
    "try_catch : (func:try_func func:catch_action -> --)
    
    desc:
        evaluates a function, and catches any exceptions and executes the catch function
        try_func: the function to be executed
        catch_func: the function executed if try_func raises and exception
    tags:
        control,exception,try,catch
    '''
    c, t = cat.stack.pop_2()
    
    try :
        cat.eval( t )
    
    except Exception, msg :
        cat.output( str(msg), cat.ns.config.get('display', 'error') )
        cat.eval( c )

@define(ns, 'raise,throw')
def _raise( cat ) :
    '''
    raise : (string:message -> --)
    throw : (string:message -> --)
    
    desc:
        Raises a standard Python exception
        message: the user-defined message related to the exception
    tags:
        control,exception,raise
    '''
    msg = cat.stack.pop()
    raise Exception, "cat exception: " + str(msg)


def _returnNS() :
    return ns

