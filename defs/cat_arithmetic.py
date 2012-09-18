# -*- coding: utf-8 -*-
from cat.namespace import *
ns = NameSpace()

@define(ns, '+,add')
def add(cat):
    """
        add : (nbr:lhs nbr:rhs -> nbr:sum)

        desc:
            adds top two numbers on the stack returning the sum on top of the stack
            Note that if instead of numbers one has other objects such as strings
            or lists, they will be concatenated.
            lhs: number on left of '+'
            rhs: number on right of '+'
            sum: the sum of the two arguments (lhs + rhs)
        tags:
            mathematics,addition,sum,add
    """
    a, b = cat.stack.pop_2()
    return cat.stack.push(b + a)

@define(ns, '-,sub')
def sub(cat):
    """
    sub : (nbr:lhs nbr:rhs -> nbr:difference)

    desc:
        subtracts the number at [0] from that at [-1] returning
        the difference to the top of the stack.
        lhs: the number to the left of '-'
        rhs: the number to the right of '-'
        difference: the difference of the arguments (lhs - rhs)
    tags:
        mathematics,difference,subtraction,sub
    """
    a, b = cat.stack.pop_2()
    cat.stack.push(b - a)

@define(ns, '*,mul')
def mul(cat):
    """
    mul : (nbr:lhs nbr:rhs -> nbr:product)

    desc:
        multiplies together the top two numbers on the stack. Result is placed
        on top of the stack. Note if the "number" 'lhs' is a string or a list
        it is replicated according to the standard Python rules.
        lhs: the number on the left of '*'
        rhs: the number on the right of '*'
        product: the result of applying '*' to the arguments (lhs * rhs)
    tags:
        mathematics,product,multiply,mul
    """
    a, b = cat.stack.pop_2()
    cat.stack.push(a * b)

@define(ns, '/,div')
def div(cat):
    """
    div : (nbr:lhs nbr:rhs -> nbr:quotient)

    desc:
        The number at [0] is divided into the number at [-1] and the
        quotient is pushed onto the stack.
        lhs: the number on the left of '/'
        rhs: the number on the right of '/'
        quotient: the result of applying '/' to the arguments (lhs / rhs)
    tags:
        mathematics,quotient,division,div
    """
    a, b = cat.stack.pop_2()
    cat.stack.push(b / a)

@define(ns, '++,inc' )
def inc( cat) :
    '''
    inc : (nbr:val -> nbr:newVal)
    
    desc:
        increments the number on top ofthe stack by 1
        val: the value to be incremented
        newVal: result (val + 1)
    tags:
        mathematics,increment
    '''
    cat.stack[-1] += 1

@define(ns, '--,dec' )
def dec( cat ) :
    '''
    dec : (nbr:val -> nbr:newVal)
    
    desc:
        decrements the number on top ofthe stack by 1
        val: the number to be decremented
        newVal: result of decrementation (val - 1)
    tags:
        mathematics,decrement
    '''
    cat.stack[-1] -= 1

@define(ns, '%,mod' )
def mod( cat ):
    '''
    mod : (nbr:base nbr:modulus -> nbr:remainder)
    
    desc:
        applies modulus function to top two members on stack. Number at [0]
        is the modulus.
        base: the base to which the modulus is to be applied
        modulus: the modulus
        remainder: the result (base % modulus)
    tags:
        mathematics,modulus,remainder
    '''
    a, b = cat.stack.pop_2()
    cat.stack.push( b % a )

@define(ns, 'pwr,**' )
def pwr( cat ) :
    '''
    pwr : (nbr:base nbr:expt -> nbr:result)
    
    desc:
        base**expt is pushed onto the stack
        base: the base number to be exponentiated
        expt: the power to which to raise the base
        result: base**expt
    tags:
        mathematics,exponentiation,power
    '''
    expt, base = cat.stack.pop_2()
    
    if isinstance(base, basestring) :
        base = eval( base )
    
    if not isinstance(base, (int, long, float)) :
        raise ValueError, "pwr: The base must be a number"
    
    if isinstance(expt, basestring) :
        expt = eval( expt )
    
    if not isinstance(expt, (int, long, float)) :
        raise ValueError, "pwr: The exponent must be a number"
    
    cat.stack.push( base ** expt )

@define(ns, 'rnd,round' )
def _round( cat ) :
    '''
    rnd : (float:nbr int:dp -> float:rounded)
    
    desc:
        rounds the floating point number at [-1] to the number of
        decimal places specified by the integer at [0]
        nbr: the floating point number to be rounded
        dp: number of decimal places to which to round it
        rounded: the result
    tags:
        mathematics,round
    '''
    dp, nbr = cat.stack.pop_2()
    
    if not isinstance(nbr, float) :
        nbr = float( nbr )
    
    dp = int( dp )
    
    cat.stack.push( round(nbr, dp) )

@define(ns, 'abs' )
def _abs( cat ) :
    '''
    abs : (nbr:src -> nbr:ans)
    
    desc:
        replaces the number on top of the stack with its absolute value
        src: number to be modified
        ans: result of applying |src|
    tags:
        mathematics,absolute,value
    '''
    nbr = cat.stack.pop()
    
    if isinstance(nbr, basestring) :
        nbr = eval( nbr )
    
    if isinstance(nbr, (int, long, float)) :
        cat.stack.push( abs(nbr) )
    
    else :
        raise ValueError, "abs: Argument is not a number"
    
@define(ns, 'chr' )
def _chr( cat ) :
    '''
    chr : (int:val -> string:char)
    
    desc:
        converts the integer on top of the stack to a single character string
        val: the integer value to convert
        char: the matching character
    tags:
        string,int
    '''
    val = cat.stack.pop()
    
    if isinstance(val, basestring) and val.isdigit() :
        val = int( val )
    
    if isinstance(val, float) :
        val = int( val )
    
    if isinstance(val, (int, long)) :
        cat.stack.push( chr(val) )
    
    else :
        raise ValueError, "chr: Cannot convert argument to an integer"

@define(ns, 'ord' )
def _ord( cat ) :
    '''
    ord : (string:chr -> int:val)
    
    desc:
        takes the single character string (or first character of a longer string)
        and pushes the integer code for that character onto the stack
        chr: string of one character
        val: its integer representation
    tags:
        string,mathematics
    '''
    obj = cat.stack.pop()
    
    if isinstance(obj, (list, tuple)) :
        obj = obj[0]
    
    if not isinstance(obj, basestring) :
        obj = str(obj)
    
    cat.stack.push( ord(obj[0]) )

@define(ns, 'hash' )
def _hash( cat ) :
    '''
    hash : (any:obj -> int:hash_value)
    
    desc:
        pushes the hash value of the object on top of the stack onto the stack
        obj: the object to be "hashed"
        hash_value: the integer hash value for the object at [0]
    tags:
        mathematics,hash,unique
    '''
    cat.stack.push( hash(cat.stack.pop()) )

@define(ns, 'id' )
def _id( cat ) :
    '''
    id : (any:obj -> any:obj int:id)
    
    desc:
        calculates a unique integer id for the object on top of
        the stack and then pushes this id onto the stack. This id
        is unique as long as the session lasts. A new session will
        produce a different id.
        obj: the object for which a unique (session-based) integer is required
        id: the integer id for the object
    tags:
        mathematics,id,unique
    '''
    cat.stack.push( id(cat.stack.peek()) )

@define(ns, '>>,right_shift' )
def right_shift( cat ) :
    '''
    >>          : (int:base int:n -> int:shifted)
    right_shift : (int:base int:n -> int:shifted)
    
    descr:
        performs a right shift of n bits on a base integer
        base: the number to be shifted
        n: number of bits to shift
        shifted: the result of the shift
    tags:
        mathematics,shift
    '''
    n, val = cat.stack.pop_2()
    cat.stack.push( int(val) >> n )

@define( ns,'<<,left_shift' )
def left_shift( cat ) :
    """'
    <<         : (int:base int:n -> int:shifted)
    left_shift : (int:base int:n -> int:shifted)
    
    descr:
        performs a left shift of n bits on a base integer
        base: the number to be shifted
        n: number of bits to shift
        shifted: the result of the shift
    tags:
        mathematics,shift
    """
    n, val = cat.stack.pop_2()
    cat.stack.push( int(val) << n )

@define(ns, '/%,%/,divmod' )
def _divmod( cat ) :
    '''
    divmod : (nbr:base nbr:modulus -> nbr:quotient nbr:remainder)
    /%     : (nbr:base nbr:modulus -> nbr:quotient nbr:remainder)
    %/     : (nbr:base nbr:modulus -> nbr:quotient nbr:remainder)
    
    desc:
        applies divmod function to top two members on stack. Number on top
        is the modulus. Returns quotient, remainder on stack (remainder on top).
        base: the number to be "divmodded"
        modulus: the modulus value
        quotient: the quotient
        remainder: the remainder
    tags:
        mathematics,quotient,remainder,modulus
    '''
    a, b = cat.stack.pop_2()
    cat.stack.push( divmod(b, a), multi=True )

@define(ns, 'even')
def _even( cat ) :
    '''
    even : ( int:value -> bool:TF )
    
    desc:
        if the integer on top of the stack is even True is pushed onto the stack;
        otherwise False
        value: the integer to test for evenness
        TF: true if value is even; otherwiser false
    tags:
        mathematics,parity
    '''
    cat.stack.push( (cat.stack.pop() % 2) == 0 )

@define(ns, 'to_bool,as_bool')
def to_bool( cat ) :
    '''
    to_bool : (any:obj -> bool:TF)
    as_bool : (any:obj -> bool:TF)
    
    desc:
        Coerces any value to a boolean
        obj: object to coerce
        TF: True if object satisfies Python test for true; False otherwise
    tags:
        conversion,boolean
    '''
    cat.stack.push( bool(cat.stack.pop()) )

@define(ns, 'neg')
def _neg( cat ) :
    '''
    neg : (nbr:value -> -nbr:negated)
    
    desc:
        Negates top value.
        value: object to be negated
        negated: the result of the negation operation
    tags:
        mathematics,negation
    '''
    arg = cat.stack.pop()
    
    if isinstance(arg, (float, int, long)) :
        cat.stack.push( -arg )
    
    elif isinstance(arg, bool) :
        cat.stack.push( not arg )
    
    else :
        raise Exception, "neg: Cannot negate %s (only numbers and booleans)" % str(arg)

@define(ns, 'int_to_byte')
def int_to_byte( cat ) :
    '''
    int_to_byte : (nbr:value -> byte:int_val)
    
    desc:
        Converts an integer into a byte, throwing away sign and ignoring higher bits
        value: and int or a float to be converted to a byte (8-bit) value
        int_val: the low 8 bits of the value
    tags:
        mathematics,conversion,byte
    '''
    cat.stack.push( int(cat.stack.pop()) & 0377 )

@define(ns, 'min')
def _min( cat ) :
    '''
    min : (any:a any:b -> any:min_val )
    
    desc:
        pushes the minimum of the two arguments on top of the stack.
        Numbers: the smaller number
        Strings: the shorter string
        Lists: the shorter list
        a: a value
        b: a value
        min_val: the minimum of the two values
    tags:
        mathematics,string,list,minimum,extrema
    '''
    t = cat.stack.pop()
    
    if isinstance(t, (list, tuple)) :
        cat.stack.push( min(*t) )

    else :
        u = cat.stack.pop()
        cat.stack.push( min(t, u) )

@define(ns, 'max')
def _max( cat ) :
    '''
    max : (any:a any:b ->any:max_val )
    
    desc:
        pushes the larger of the two arguments on top of the stack.
        Numbers: the larger number
        Strings: the longer string
        Lists: the longer list
        a: an object
        b: an object
        max_val: the max of the two values
    tags:
        mathematics,string,list,maximum,extrema
    '''
    t = cat.stack.pop()
    
    if isinstance(t, (list, tuple)) :
        cat.stack.push( max(*t) )

    else :
        u = cat.stack.pop()
        cat.stack.push( max(t, u) )

@define(ns, 'as_int,int,to_int')
def as_int( cat ) :
    '''
    as_int : (any:obj -> int:value)
    to_int : (any:obj -> int:value)
    int    : (any:obj -> int:value)
    
    desc:
        casts a variant to an int
        If the object is a list or tuple, its length is used
        obj: the object to cast
        int: the result of the cast
    tags:
        conversion,int
    '''
    obj = cat.stack.pop()
    
    if isinstance(obj, (list, tuple)) :
        cat.stack.push( len(obj) )
    
    else :
        cat.stack.push( int(obj) )

@define(ns, 'as_float,float,to_float')
def as_float( cat ) :
    '''
    as_float : (any:obj -> float:value)
    to_float : (any:obj -> float:value)
    float    : (any:obj -> float:value)
   
    desc:
        Casts a variant to a float
        obj: the object to cast
        int: the result of the cast
    tags:
        conversion,float
    '''
    cat.stack.push( float(cat.stack.pop()) )

@define(ns, 'bit_and,&')
def bit_and( cat ) :
    '''
    &       : (int:lhs int:rhs -> int:result)
    bit_and : (int:lhs int:rhs -> int:result)
    
    desc:
        Performs bit-wise logical and on top two stack elements
        lhs: the left hand side of '&'
        rhs: the right hand side of '&'
        result: the result of applying '&'
    tags:
        mathematics,bit_wise,and
    '''
    r, l = cat.stack.pop_2()
    cat.stack.push( int(l) & int(r) )

@define(ns, 'bit_or,|')
def bit_or( cat ) :
    '''
    |      : (int:lhs int:rhs -> int:result)
    bit_or : (int:lhs int:rhs -> int:result)
    
    desc:
        Performs bit-wise logical or on top two stack elements
        lhs: the left hand side of '|'
        rhs: the right hand side of '|'
        result: the result of applying '|'
    tags:
        mathematics,bit_wise,or
    '''
    r, l = cat.stack.pop_2()
    cat.stack.push( int(l) | int(r) )

@define(ns, 'bit_xor,^')
def bit_xor( cat ) :
    '''
    ^       : (int:lhs int:rhs -> int:result)
    bit_xor : (int:lhs int:rhs -> int:result)
    
    desc:
        performs bit-wise logical or on top two stack elements
        lhs: the left hand side of '^'
        rhs: the right hand side of '^'
        result: the result of applying '^'
    tags:
        mathematics,bit_wise,xor,exclusive_ok
    '''
    r, l = cat.stack.pop_2()
    cat.stack.push( int(l) ^ int(r) )

@define(ns, 'bit_not,~')
def bit_not( cat ) :
    '''
    ~       : (int:val -> int:complement)
    bit_not : (int:val -> intcomplement)
    
    desc:
        performs bit-wise logical negation on top stack element as an integer
        val: the integer to which to apply negation
        result: the result of applying negation
    tags:
        mathematics,bit_wise,negation,not
    '''
    def bitLen( anInt ) :
        length = 0
        
        while anInt :
            anInt >>= 1
            length += 1
        
        return length
    
    n      = int( cat.stack.pop() )
    length = bitLen( n )
    value  = ~n & (2**length - 1)
    cat.stack.push( value )

@define(ns, 'and,&&')
def _and( cat ) :
    '''
    and : (bool:lhs bool:rhs -> bool:result)
    &&  : (bool:lhs bool:rhs -> bool:result)
    
    desc:
        Returns True if both of the top two values on the stack are True
        lhs: left hand side of '&&'
        rhs: right hand side of '&&'
        result: result of applying '&&' to arguments
    tags:
        boolean,logical,and
    '''
    a, b = cat.stack.pop_2()
    cat.stack.push( a and b )

@define(ns, 'or,||')
def _or( cat ) :
    '''
    or : (bool:lhs bool:rhs -> bool:result)
    || : (bool:lhs bool:rhs -> bool:result)
    
    "desc:
        Returns True if either of the top two values on the stack are True
        lhs: left hand side of '||'
        rhs: right hand side of '||'
        result: result of applying '||' to arguments
    tags:
        boolean,logical,or
    '''
    a, b = cat.stack.pop_2()
    cat.stack.push( a or b )

@define(ns, 'not,¬')
def _not( cat ) :
    '''
    not : (bool:arg -> bool:arg)
    
    desc:
        Returns True if the top value on the stack is False and vice versa
        arg: logical value to negate
    tags:
        boolean,logical,not
    '''
    cat.stack[-1] = not cat.stack[-1]


def _returnNS() :
    return ns

