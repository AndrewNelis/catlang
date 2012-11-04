# -*- coding: utf-8 -*-
from cat.namespace import *
ns = NameSpace()

@define(ns, '+,add')
def add(cat):
    """
    +   : (nbr:lhs nbr:rhs -> nbr:sum)
    add : (nbr:lhs nbr:rhs -> nbr:sum)

    desc:
        Adds top two numbers on the stack returning the sum on top of the stack
        Note that if instead of numbers one has other objects such as strings
        or lists, they will be concatenated.
        lhs: number on left of '+'
        rhs: number on right of '+'
        sum: the sum of the two arguments (lhs + rhs)

        Example: 1 2 add   => 3
                 1 2 3 + + => 6
                 13.5 2 +  => 15.5
    tags:
        mathematics,addition,sum,add
    """
    r, l = cat.stack.pop_2()
    return cat.stack.push(l + r)

@define(ns, '-,sub')
def sub(cat):
    """
    -   : (nbr:lhs nbr:rhs -> nbr:difference)
    sub : (nbr:lhs nbr:rhs -> nbr:difference)

    desc:
        Subtracts the number at [0] from that at [-1] returning
        the difference to the top of the stack.
        lhs: the number to the left of '-'
        rhs: the number to the right of '-'
        difference: the difference of the arguments (lhs - rhs)

        Example: 3 1 sub   => 2
                 3 2 1 - - => 2
    tags:
        mathematics,difference,subtraction,sub
    """
    a, b = cat.stack.pop_2()
    cat.stack.push(b - a)

@define(ns, '*,mul')
def mul(cat):
    """
    *   : (nbr:lhs nbr:rhs -> nbr:product)
    mul : (nbr:lhs nbr:rhs -> nbr:product)

    desc:
        Multiplies together the top two numbers on the stack. Result is placed
        on top of the stack. Note if the "number" 'lhs' is a string or a list
        it is replicated according to the standard Python rules.
        lhs: the number on the left of '*'
        rhs: the number on the right of '*'
        product: the result of applying '*' to the arguments (lhs * rhs)

        Example: 2 3 mul         => 6
                 5.2 3.6 9.8 * * => 183.456
    tags:
        mathematics,product,multiply,mul
    """
    a, b = cat.stack.pop_2()
    cat.stack.push(a * b)

@define(ns, '/,div')
def div(cat):
    """
    /   : (nbr:lhs nbr:rhs -> nbr:quotient)
    div : (nbr:lhs nbr:rhs -> nbr:quotient)

    desc:
        The number at [0] is divided into the number at [-1] and the
        quotient is pushed onto the stack.
        lhs: the number on the left of '/'
        rhs: the number on the right of '/'
        quotient: the result of applying '/' to the arguments (lhs / rhs)

        Example: 3.14 2 div   => 1.57
                 6.28 2 / 2 / => 1.57
    tags:
        mathematics,quotient,division,div
    """
    a, b = cat.stack.pop_2()
    cat.stack.push(b / a)

@define(ns, '++,inc' )
def inc( cat) :
    '''
    ++  : (nbr:val -> nbr:newVal)
    inc : (nbr:val -> nbr:newVal)
    
    desc:
        Increments the number on top ofthe stack by 1
        val: the value to be incremented
        newVal: result (val + 1)
        
        Example: 42 inc => 43
                 21 ++  => 22
                 -3 ++  => -2
    tags:
        mathematics,increment
    '''
    cat.stack[-1] += 1

@define(ns, '--,dec' )
def dec( cat ) :
    '''
    --  : (nbr:val -> nbr:newVal)
    dec : (nbr:val -> nbr:newVal)
    
    desc:
        Decrements the number on top ofthe stack by 1
        val: the number to be decremented
        newVal: result of decrementation (val - 1)
        
        Example: 123 dec => 122
                 321 --  => 320
                 -14 dec => -15
    tags:
        mathematics,decrement
    '''
    cat.stack[-1] -= 1

@define(ns, '%,mod' )
def mod( cat ):
    '''
    %   : (nbr:base nbr:modulus -> nbr:remainder)
    mod : (nbr:base nbr:modulus -> nbr:remainder)
   
    desc:
        Applies modulus function to top two members on stack. Number at [0]
        is the modulus.
        base: the base to which the modulus is to be applied
        modulus: the modulus
        remainder: the result (base % modulus)
        
        Example: 13 3 mod     => 1
                 32.77 24.0 % => 8.77
                 -15.5 3 mod  => 2.5
                 15.5 -3 mod  => -2.5
                 -15.5 -3 mod => -0.5
    tags:
        mathematics,modulus,remainder
    '''
    a, b = cat.stack.pop_2()
    cat.stack.push( b % a )

@define(ns, 'pwr,**' )
def pwr( cat ) :
    '''
    **  : (nbr:base nbr:expt -> nbr:result)
    pwr : (nbr:base nbr:expt -> nbr:result)
    
    desc:
        base**expt is pushed onto the stack
        base: the base number to be exponentiated
        expt: the power to which to raise the base
        result: base**expt
        
        Example: 2 12 pwr     => 4096
                 3 3 **       => 27
                 2.75 3.14 ** => 23.960984522805955
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
    rnd   : (float:nbr int:dp -> float:rounded)
    round : (float:nbr int:dp -> float:rounded)
    
    desc:
        Rounds the floating point number at [-1] to the number of
        decimal places specified by the integer at [0]
        nbr: the floating point number to be rounded
        dp: number of decimal places to which to round it
        rounded: the result
        
        Example: 3.14159265 3 rnd  => 3.142
                 2.7182845 3 round => 2.718
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
        
        Example: -123 abs      => 123
                 -12.3 abs     => 12.3
                 "23.45"       => 23.45
                 [1,-2,3] list => [1, 2, 3]
    tags:
        mathematics,absolute,value
    '''
    nbr = cat.stack.pop()
    
    if isinstance(nbr, basestring) :
        nbr = eval( nbr )
    
    if isinstance(nbr, (int, long, float)) :
        cat.stack.push( abs(nbr) )
    
    elif isinstance(nbr, (list,tuple) ) :
        cat.stack.push( [abs(x) for x in nbr] )
    
    else :
        raise ValueError, "abs: Cannot take absolute value of '%r'" % nbr
    
@define(ns, 'chr' )
def _chr( cat ) :
    '''
    chr : (int:val -> string:char)
    
    desc:
        Converts the integer on top of the stack to a single character string
        val: the integer value to convert
        char: the matching character
        
        Example: 122 chr => 'z
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
        Takes the single character string (or first character of a longer string)
        and pushes the integer code for that character onto the stack
        chr: string of one character
        val: its integer representation
        
        Example: 'z ord => 122
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
        Pushes the hash value of the object on top of the stack onto the stack
        obj: the object to be "hashed"
        hash_value: the integer hash value for the object at [0]
        
        Example: "Delbert Nordstrom" hash => -1053843652458427105
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
        
        Example: 'test id => a session dependent long
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
        Performs a right shift of n bits on a base integer
        base: the number to be shifted
        n: number of bits to shift
        shifted: the result of the shift
        
        Example: 12 1 >>          => 6
                 16 3 right_shift => 2
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
        Performs a left shift of n bits on a base integer
        base: the number to be shifted
        n: number of bits to shift
        shifted: the result of the shift
        
        Example: 1 3 <<         => 8
                 6 1 left_shift => 12
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
        Applies divmod function to top two members on stack. Number on top
        is the modulus. Returns quotient, remainder on stack (remainder on top).
        base: the number to be "divmodded"
        modulus: the modulus value
        quotient: the quotient
        remainder: the remainder
        
        Example: 14 3 /%          => 4 2     (top of stack on right)
                 24.0 3.7 %/      => 3.0 2.1 (top of stack on right)
                 24.0 17.0 divmod => 1.0 7.0 (top of stack on right)
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
        If the integer on top of the stack is even True is pushed onto the stack;
        otherwise False
        value: the integer to test for evenness
        TF: True if value is even; otherwiser False
        
        Example: 3 even => False
    tags:
        mathematics,parity
    '''
    cat.stack.push( (cat.stack.pop() % 2) == 0 )

@define(ns, 'to_bool,as_bool,bool')
def to_bool( cat ) :
    '''
    to_bool : (any:obj -> bool:TF)
    as_bool : (any:obj -> bool:TF)
    bool    : (any:obj -> bool:TF)
    
    desc:
        Coerces any value to a boolean
        obj: object to coerce
        TF: True if object satisfies Python test for true; False otherwise
        
        Example: 0 to_bool => False
                 1 as_bool => True
                 "" bool   => False
    tags:
        conversion,boolean
    '''
    cat.stack.push( bool(cat.stack.pop()) )

@define(ns, 'neg')
def _neg( cat ) :
    '''
    neg : (nbr:value -> -nbr:negated)
    
    desc:
        Negates value at [0]
        value: object to be negated
        negated: the result of the negation operation
        
        Example: 3.14 neg => -3.14
                 42 neg   => -42
                 true neg => False
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
        
        Example: 1023 int_to_byte => 0377
    tags:
        mathematics,conversion,byte
    '''
    cat.stack.push( int(cat.stack.pop()) & 0377 )

@define(ns, 'min')
def _min( cat ) :
    '''
    min : (nbr:a nbr:b -> nbr:min_val )
    min : (any:a -> any:min_val )
    
    desc:
        Pushes the minimum of the two arguments on top of the stack.
        Numbers: the smaller number
        List: the min element of the list (single argument)
        String: the letter having the smallest ordinal value (single argument)
        
        a: number or list or string
        b: number
        max_val: the min of the (two) values
        
        Example: 5 3 min              => 3
                 [3 1 4 5 2] list min => 1
                 'abc Min             => 'a
    tags:
        mathematics,string,list,minimum,extrema
    '''
    t = cat.stack.pop()
    
    if isinstance(t, (list, tuple, basestring)) :
        cat.stack.push( min(t) )

    else :
        u = cat.stack.pop()
        cat.stack.push( min(t, u) )

@define(ns, 'max')
def _max( cat ) :
    '''
    max : (nbr:a nbr:b ->nbr:max_val )
    max : (any:a ->any:max_val )
    
    desc:
        Pushes the larger of the two arguments on top of the stack back onto the stack.
        Numbers: the larger number
        List: the max element of the list (single argument)
        String: the letter having the largest ordinal value (single argument)
        
        a: number or list or string
        b: number
        max_val: the max of the (two) values
        
        Example: 5 3 max              => 5
                 [3 1 4 5 2] list max => 5
                 'abc max             => 'c
    tags:
        mathematics,string,list,maximum,extrema
    '''
    t = cat.stack.pop()
    
    if isinstance(t, (list, tuple, basestring)) :
        cat.stack.push( max(t) )
    
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
        Casts a variant to an int
        If the object is a list or tuple, its length is used
        obj: the object to cast
        value: the result of the cast
        
        Example: 3.14 as_int        => 3
                 2.718 to_int       => 2
                 5 int              => 5
                 [9 8 7 6] list int => 4
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
        value: the result of the cast
        
        Example: 23 as_float    => 23.0
                 12.34 to_float => 12.34
                 '44.23 float   => 44.23
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
        
        Example: 3 1 &       => 1
                 7 6 bit_and => 6
    tags:
        mathematics,bit_wise,and,bit
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
        
        Example: 2 1 |      => 3
                 6 2 bit_or => 6
    tags:
        mathematics,bit_wise,or,bit
    '''
    r, l = cat.stack.pop_2()
    cat.stack.push( int(l) | int(r) )

@define(ns, 'bit_xor,^')
def bit_xor( cat ) :
    '''
    ^       : (int:lhs int:rhs -> int:result)
    bit_xor : (int:lhs int:rhs -> int:result)
    
    desc:
        Performs bit-wise logical or on top two stack elements
        lhs: the left hand side of '^'
        rhs: the right hand side of '^'
        result: the result of applying '^'
        
        Example: 3 2 ^         => 1
                 12 10 bit_xor => 6
    tags:
        mathematics,bit_wise,xor,exclusive_ok,bit
    '''
    r, l = cat.stack.pop_2()
    cat.stack.push( int(l) ^ int(r) )

@define(ns, 'bit_not,~')
def bit_not( cat ) :
    '''
    ~       : (int:val -> int:complement)
    bit_not : (int:val -> int:complement)
    
    desc:
        Performs bit-wise logical negation on top stack element as an integer.
        Zeros to the left of the most significant bit are ignored.
        val: the integer to which to apply negation
        result: the result of applying negation
        
        Example: 5 ~       => 2
                 7 bit_not => 0
    tags:
        mathematics,bit_wise,negation,not,bit
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
        Returns True if values at [0] and [-1] are both True, otherwise returns False
        lhs: left hand side of '&&'
        rhs: right hand side of '&&'
        result: result of applying '&&' to arguments
        
        Example: True True &&   => True
                 True False and => False
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
        
        Example: True False ||  => True
                 False False or => False
    tags:
        boolean,logical,or
    '''
    a, b = cat.stack.pop_2()
    cat.stack.push( a or b )

@define(ns, 'not,¬')
def _not( cat ) :
    '''
    ¬   : (bool:arg -> bool:arg)
    not : (bool:arg -> bool:arg)
    
    desc:
        Returns True if the top value on the stack is False and vice versa
        arg: logical value to negate
        
        Example: True ¬    => False
                 False not => True
    tags:
        boolean,logical,not
    '''
    cat.stack[-1] = not cat.stack[-1]


def _returnNS() :
    return ns

