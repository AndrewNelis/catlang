# cat.stack manipulations

from cat.namespace import *
ns = NameSpace()

@define(ns, 'clear')
def clear( cat ) :
    '''
    clear : (A -> --)
    
    desc:
        Removes all stack entries
        A: the stack contents
        
        Example: 1 2 3 clear => --
    tags:
        stack,clear
    '''
    cat.stack.clear()

@define(ns, 'pop,drop')
def pop( cat ) :
    '''
    pop  : (any:top_item -> --)
    drop : (any:top_item -> --)
    
    desc:
        Removes the top item from the cat.stack
        top_item: the top of the stack [0]
        
        Example: 1 2 pop => 1
    tags:
        stack,pop,drop,top
    '''
    cat.stack.pop()

@define(ns, 'popd,under')
def popd( cat ) :
    '''
    popd  : (any:b any:a -> any:a)
    under : (any:b any:a -> any:a)
    
    desc:
        Removes the item at [-1] on the stack
        b: object at [-]
        a: object at [0]
        
        Example: 'a 'b popd => 'b
    tags:
        stack,pop,under
    '''
    swap( cat )
    cat.stack.pop()

@define(ns, 'dup')
def dup( cat ) :
    '''
    dup : (any:a -> any:a any:a)
    
    desc:
        Duplicate the top item on the stack
        a: object on top of the stack [0]
        
        Example: 'x dup => 'x 'x
    tags:
        stack,duplicate,dup
    '''
    cat.stack.push( cat.stack.peek() )

@define(ns, 'swap')
def swap( cat ) :
    '''
    swap : (any:a any:b -> any:b any:a)
    
    desc:
        Swap the top two items on the stack
        a: object originally on stack at position [-1]
        b: object originally on stack at position [0]
        
        Example: 1 2 swap => 2 1
    tags:
        stack,swap
    '''
    a, b = cat.stack.pop_2()
    cat.stack.push( (a, b), multi=True )

@define(ns, 'flip')
def flip( cat ) :
    '''
    flip : (any:a any:b any:c -> any:c any:b any:a)
    
    desc:
        Swaps the elements on the stack at positions [0] and [-2] of the stack
        a: object on stack at original position [-2]
        b: object on stack at position [-1]
        c: object on stack at original position [0]
        
        Example: 1 2 3 flip => 3 2 1
    tags:
        stack,flip
    '''
    t, m, b = cat.stack.pop_n( 3 )
    cat.stack.push( (t, m, b), multi=True )

@define(ns, 'swapd')
def swapd( cat ):
    '''
    swapd : (any:c any:b any:a -> any:b any:c any:a)
    
    desc:
        Swap the items at [-1] and [-2] of the stack
        a: object at stack position [0]
        b: object originally at stack position [-1]
        c: object originally at stack position [-2]
        Note: same action as: [swap] dip
        
        Example: 1 2 3 swapd => 2 1 3
    tags:
        stack,swap
    '''
    a, b, c = cat.stack.pop_n( 3 )
    cat.stack.push( (b, c, a), multi=True )

@define(ns, 'dupd')
def dupd( cat ) :
    '''
    dupd : (any:b any:a -> any:b any:b any:a)
    
    desc:
        Duplicates the item at [-1] leaving item at [0] on top of the stack
        a: object at stack position [0]
        b: object originally at stack position [-1]
        Note: same action as: [dup] dip
        
        Example: 1 2 dupd => 1 1 2
    tags:
        stack,duplicate,dup
    '''
    a, b = cat.stack.pop_2()
    cat.stack.push( (b, b, a), multi=True )

@define(ns, 'size')
def size( cat ) :
    '''
    size: (A -> A int:size)
    
    desc:
        Pushes the size of the stack (i.e. number of items in the stack)
        onto the top of the stack
        A: the full stack contents
        size: number of items in the stack
        
        Example: 1 2 3 size        => 1 2 3 3
                 [1 2 3] list size => [1, 2, 3] 1
    tags:
        lists,stack,size,length
    '''
    cat.stack.push( cat.stack.length() )

@define(ns, '+rot,rot_up')
def rot_up( cat ) :
    '''
    +rot    : (any:a any:b any:c -> any:c any:a any:b)
    +rot_up : (any:a any:b any:c -> any:c any:a any:b)
    
    desc:
        Rotates the top three elements upward one position circularly:
            [-2] [-1] [0] -> [0] [-1] [-2]
        a: item originally at stack position [-2]
        b: item originally at stack position [-1]
        c: item originally at stack position [0]
        
        Example: 1 2 3 +rot => 3 1 2
    tags:
        stack,rotate
    '''
    if cat.stack.length() < 3 :
        raise Exception, "+rot: Expect at least three elements on the cat.stack"
    
    t, m, b = cat.stack.pop_n( 3 )
    cat.stack.push( (t, b, m), multi=True )

@define(ns, '-rot,rot_down')
def rot_down( cat ) :
    '''
    -rot     : (any:a any:b any:c -> any:b any:c any:a)
    rot_down : (any:a any:b any:c -> any:b any:c any:a)
    
    desc:
        Rotates the top three elements downward one position circularly
            [-2] [-1] [0] -> [-1] [0] [-2]
        a: item originally at stack position [-2]
        b: item originally at stack position [-1]
        c: item originally at stack position [0]
        
        Example: 1 2 3 -rot => 2 3 1
    tags:
        stack,rotate
    '''
    if cat.stack.length() < 3 :
        raise Exception, "-rot: Expect at least three elements on the cat.stack"
    
    t, m, b = cat.stack.pop_n( 3 )
    cat.stack.push( (m, t, b), multi=True )

@define(ns, 'eval,apply')
def _eval( cat ) :
    '''
    eval  : ( function:exec_func -> any:ans )
    apply : ( function:exec_func -> any:ans )
    
    desc:
        Applies a function to the stack (i.e. executes a "program" or a string)
        exec_func: the function to evaluate
        ans: the result of the evaluation
        
        Example: 2 [inc dup] apply   => 3 3
                 2 3 [add 2 **] eval => 25
                 "2 3 4 + *" eval    => 14
    tags:
        functions,eval,apply
    '''
    cat.eval( cat.stack.pop() )

@define(ns, 'dip')
def dip( cat ) :
    '''
    dip: (any:arg any:saved function:exec_func -> any:result any:saved)
    
    desc:
        Evaluates a function, temporarily removing the item below the function 'exec_func'.
        This makes the item now on top of the stack the argument to the function.
        After evaluation of the function the removed item is restored to the top of the stack
        arg: the argument of the exec_func
        saved: the item to be saved (removed and then replaced after function execution)
        exec_func: the function to be executed
        result: the result, if any, of executing the function
        
        Example: 2 42 [3 * dec] dip => 5 42
    tags:
        functions,dip
    '''
    func, second = cat.stack.pop_2()
    cat.stack.push( func )
    _eval( cat )
    cat.stack.push( second )

@define(ns, 'quote')
def quote( cat ) :
    '''
    quote: (any:obj -> function:quoted)
    
    desc:
        Creates a constant generating function from the top value on the stack
        obj: object to be 'quoted'
        quoted: a pseudo-function that generates the value represented by obj
        
        Example: 3.14159 quote 'pi ! => --
    tags:
        functions,quote,generator
    '''
    t = cat.stack.pop()
    cat.stack.push( lambda : cat.stack.push(t) )

@define(ns, 'compose')
def compose( cat ) :
    '''
    compose: (function:left function:right -> function:composite)
    
    desc:
        Creates a function by composing (concatenating) two existing functions
        left: the function that executes after 'right' using 'right's' results as an argument
        right: the function that executes first operating on the stack and producing output
                for the 'left' function
        composite: a function (lambda) object that is the composition of the 'left' and 'right' functions
        
        Example: [dup inc] [swap] compose
    tags:
        functions,compose
    '''
    f1, f2 = cat.stack.pop_2()
    cat.stack.push( lambda : cat.eval2(f2, f1) )

@define(ns, 'papply')
def papply( cat ) :
    '''
    papply : (any:arg function:exec_func -> function:partial)
    
    desc:
        Partial application: binds the top argument to the top value in the stack
        arg:  the argument to be bound with the 'exec_func'
        exec_func: function to apply after the arg
        partial: the resulting composition
        
        Example: 1 [<=] papply => [1 <=]
    tags:
        functions,papply
    '''
    swap( cat )
    quote( cat )
    swap( cat )
    compose( cat )

@define(ns, '!,save_var')
def saveVar( cat ) :
    '''
    !        : (any:obj string:userVarName -> )
    save_var : (any:obj string:userVarName -> )
    
    desc:
        Saves the value at [-1] to the user symbol table with the name
        provided by the string at [0]. Variable names may NOT duplicate any
        defined words (built-in or user-defined)
        obj: the object to be saved
        userVarName: the name under which the object will be found
        
        Example: 3.14159265 'pi !
    tags:
        variables,user
    '''
    varName, value = cat.stack.pop_2()
    cat.ns.addVar( varName, value )

@define(ns, '@,get_var')
def fetchVar( cat ) :
    '''
    @       : (string:userVarName -> any:val)
    get_var : (string:userVarName -> any:val)
    
    desc:
        Pushes the value of the named user-variable onto the stack
        Note: the userVarName by itself (no quotes or @) will push its value onto the stack
        userVarName: the name under which the object has been stored
        val: the object
        
        Example: pi ! => 3.14159265
                 pi   => 3.14159265
    tags:
        custom,variables,user
    '''
    name         = cat.stack.pop()
    defined, val = cat.ns.getVar( name )
    
    if defined :
        cat.stack.push( val )
    
    else :
        raise KeyError, "@: No variable called " + name

@define(ns, '->aux')
def push_to_aux( cat ) :
    '''
    ->aux : (any:item -> --)
    
    desc:
        Pushes the item onto the auxiliary stack
        item: the object to be moved to the auxiliary stack
        
        Example: 42 ->aux
    tags:
        custom,auxiliary,stack,push
    '''
    cat.stack.push_aux( cat.stack.pop() )

@define(ns, '<-aux')
def pop_from_aux( cat ) :
    '''
    <-aux : (-- -> any:item_from_aux_stack[0])
    
    desc:
        Pushes the item on top of the auxiliary stack onto the regular stack
        item: the object moved from the auxiliary stack
        
        Example: <-aux => 42
    tags:
        custom,auxiliary,stack,pop
    '''
    cat.stack.push( cat.stack.pop_aux() )

@define(ns, 'n->aux')
def push_n_to_aux( cat ) :
    '''
    n->aux : (any:item any:... int:n -> --)
    
    desc:
        Pushes n items onto the auxiliary stack
        item: the objects to be moved to the auxiliary stack
        n: number of items below to move to the auxiliary stack
        
        Example 1 2 3 2 n->aux => 1
    tags:
        custom,auxiliary,stack,push,multi
    '''
    n     = cat.stack.pop()
    items = cat.stack.pop_n( n )
    cat.stack.push_aux( items, multi=True )

@define(ns, 'n<-aux')
def pop_n_from_aux( cat ) :
    '''
    n<-aux : (int:n -> any:item_from_aux_stack[0] any:item_from_aux_stack[-1] ...)
    
    desc:
        Pushes the top n items on the auxiliary stack onto the regular stack
        n: number of items to move from auxiliary stack to the regular stack
        item_from_aux_stack[0]: an object moved from the auxiliary stack[0]
        item_from_aux_stack[-1]: an object moved from the auxiliary stack[-1]
        etc
        
        Example 2 n<-aux => 2 3
    tags:
        custom,auxiliary,stack,pop
    '''
    n = cat.stack.pop()
    cat.stack.push( cat.stack.pop_aux(n), multi=True )

def _returnNS() :
    return ns

