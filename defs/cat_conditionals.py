# conditionals

from cat.namespace import *
ns = NameSpace()

@define(ns, 'eq,==')
def eq( cat ) :
    """
    eq : (any:lhs any:rhs -> bool:TF)
    == : (any:lhs any:rhs -> bool:TF)
    
    desc:
        Returns True if top two items on cat.stack have the same value; otherwise False
        lhs: left hand comparand
        rhs: right hand comparand
        TF: True of the two comparands are equal; False otherwise
        
        Example: 1 2 ==   => False
                 'a 'b == => False
                 23 23 eq => True
    tags:
        conditional,comparison,equality
    """
    a, b = cat.stack.pop_2()
    cat.stack.push( a == b )

@define(ns, 'neq,!=')
def neq( cat ) :
    """
    neq : (any:lhs any:rhs -> bool:TF)
    !=  : (any:lhs any:rhs -> bool:TF)
    
    desc:
        Returns True if top two items on cat.stack have differning values; otherwise False
        lhs: left hand comparand
        rhs: right hand comparand
        TF: True of the two comparands are not equal; False otherwise
        
        Example: 1 2 !=   => True
                 2 2 !=   => False
                 'a 'b ne => True
    tags:
        conditional,comparison,inequality
    """
    a, b = cat.stack.pop_2()
    cat.stack.push( a != b )

@define(ns, 'gt,>')
def gt( cat ) :
    """
    gt : (any:lhs any:rhs -> bool:TF)
    >  : (any:lhs any:rhs -> bool:TF)
    
    desc:
        Returns True if the value at [-1] is greater than the one at [0];
        otherwise False
        lhs: left hand comparand
        rhs: right hand comparand
        TF: True of lhs is greater than rhs; False otherwise
        
        Example: 1 2 >   => False
                 2 1 gt  => True
                 'a 'b > => False
    tags:
        conditional,comparison,greater_than
    """
    a, b = cat.stack.pop_2()
    cat.stack.push( b > a )

@define(ns, 'lt,<')
def lt( cat ) :
    """
    lt : (any:lhs any:rhs -> bool:TF)
    <  : (any:lhs any:rhs -> bool:TF)
    
    desc:
        Returns True if the object at [-1] is less than the one at [0];
        otherwise False
        lhs: left hand comparand
        rhs: right hand comparand
        TF: True of lhs is less than rhs; False otherwise
        
        Example: 1 2 <   => True
                 2 1 lt  => False
                 'a 'b < => True
    tags:
        conditional,comparison,less_than
    """
    a, b = cat.stack.pop_2()
    cat.stack.push( b < a )

@define(ns, 'gteq,>=')
def gteq( cat ) :
    """
    gteq : (any:lhs any:rhs -> bool:TF)
    >=   : (any:lhs any:rhs -> bool:TF)
    
    desc:
        Returns True if the object at [-1] is greater than or equal to the one at [0];
        otherwise False
        lhs: left hand comparand
        rhs: right hand comparand
        TF: True of lhs is greater than or equal to rhs; False otherwise
        
        Example: 3 4 >=     => False
                 3 3 gteq   => True
                 4 2 >=     => True
                 'a 'b gteq => False
    tags:
        conditional,comparison,less_than,equals
    """
    a, b = cat.stack.pop_2()
    cat.stack.push( b >= a )

@define(ns, 'lteq,<=')
def lteq( cat ) :
    """
    lteq : (any:lhs any:rhs -> bool:TF)
    <=   : (any:lhs any:rhs -> bool:TF)
    
    desc:
        returns True if the object at [-1] is less than or equal to the one at [0];
        otherwise False
        lhs: left hand comparand
        rhs: right hand comparand
        TF: True of lhs is less than or equal to rhs; False otherwise
    
        Example: 2 3 <=     => True
                 3 3 <=     => True
                 4 3 <=     => False
                 'a 'b lteq => True
    tags:
        conditional,comparison,less_than,equals
    """
    a, b = cat.stack.pop_2()
    cat.stack.push( b <= a )

@define(ns, 'true')
def true( cat ) :
    '''
    true: ( -> bool)
    
    desc:
        Pushes the boolean value True on the stack
    
        Example: true => True
    tags:
        conditional,boolean.true
    '''
    cat.stack.push( True )

@define(ns, 'false')
def false( cat ) :
    '''
    false: ( -> bool)
    
    desc:
        Pushes the boolean value False on the stack
    
        Example: false => False
    tags:
        conditional,boolean,false
    '''
    cat.stack.push( False )

@define(ns, 'eqz')
def eqz( cat ) :
    '''
    eqz : (nbr:value -> bool:TF)

    desc:
        Returns true if the top value is zero
        value: the value to be compared against zero
        TF: True if the value equals zero; False otherwise
    test:
        in:
            5 eqz
        out:
            False
    test:
        in:
            0 eqz
        out:
            True
    tags:
        conditional,mathematics,equals,predicate,zero
    '''
    cat.stack.push( cat.stack.pop() == 0 )

@define(ns, 'gtz')
def gtz( cat ) :
    '''
    gtz : (nbr:value -> bool:TF)

    desc:
        Returns true if the top value is greater than zero
        value: the value to be compared against zero
        TF: True if the value is greater than zero; False otherwise
    test:
        in:
            5 gtz
        out:
            True
    test:
        in:
            -1 gtz
        out:
            False
    tags:
        conditional,mathematics,greater_than,zero,predicate
    '''
    cat.stack.push( cat.stack.pop() > 0 )

@define(ns, 'gez')
def gez( cat ) :
    '''
    gez : (nbr:value -> bool:TF)

    desc:
        Returns true if the top value is greater than zero
        value: the value to be compared against zero
        TF: True if the value is greater than or equal to zero; False otherwise
    test:
        in:
            5 gez
        out:
            True
    test:
        in:
            -1 gez
        out:
            False
    test:
        in:
            0 gez
        out:
            True
    tags:
        conditional,mathematics,greater_than,equals,zero,predicate
    '''
    cat.stack.push( cat.stack.pop() >= 0 )

@define(ns, 'ltz')
def ltz( cat ) :
    '''
    ltz : (nbr:value -> bool:TF)

    desc:
        Returns true if the top value is less than zero
        value: the value to be compared against zero
        TF: True if the value is less than zero; False otherwise
    test:
        in:
            5 ltz
        out:
            False
    test:
        in:
            -1 ltz
        out:
            True
    tags:
        conditional,mathematics,predicate,zero,less_than,less
    '''
    cat.stack.push( cat.stack.pop() < 0 )

@define(ns, 'lez')
def lez( cat ) :
    '''
    lez : (nbr:value -> bool:TF)

    desc:
        Returns true if the top value is less than or equal to zero
        value: the value to be compared against zero
        TF: True if the value is less than or equal to zero; False otherwise
    test:
        in:
            5 lez
        out:
            False
    test:
        in:
            -1 lez
        out:
            True
    test:
        in:
            0 lez
        out:
            True
    tags:
        conditional,mathematics,predicate,less_than,less,equal,zero
    '''
    cat.stack.push( cat.stack.pop() < 0 )

@define(ns, 'nez')
def neqz( cat ) :
    '''
    nez : (nbr:value -> bool:TF)

    desc:
        Returns true if the top value is not zero
        value: the value to be compared against zero
        TF: True if the value is not equal to zero; False otherwise
    test:
        in:
            5 nez
        out:
            True
    test:
        in:
            0 nez
        out:
            False
    tags:
        conditional,mathematics,predicate,not_equal,zero
    '''
    cat.stack.push( cat.stack.pop() != 0 )

def _returnNS() :
    return ns
