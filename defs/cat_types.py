# types

from cat.namespace import *
ns = NameSpace()

@define(ns, 'typename')
def typename( cat ) :
    '''
    typename : (any:obj -> string:type_name)
    
    desc:
        Returns the name of the type of an object.
        Consumes the argument.
        obj: object to be typed
        type_name: the Python type
        
        Example 123 typename => <type 'int'>
    tags:
        types
    '''
    cat.stack.push( type(cat.stack.pop()) )

@define(ns, 'typeof')
def typeof( cat ) :
    '''
    typeof : (any:oibj -> any:obj type:obj_type)
    
    desc:
        Returns a type tag for an object.
        Does not consume the argument.
        obj: the object to be typed
        obj_type: standard Python type for the object
        
        Example 'abc typeof => 'abc <type 'str'>
    tags:
        types
    '''
    cat.stack.push( type(cat.stack.peek()) )

@define(ns, 'int_type')
def int_type( cat ) :
    '''
    int_type : (-- -> type:int_type)
    
    desc:
        Pushes a value representing the type of an int
        int_type: Python type of an integer
        
        Example: int_type => <type 'int'>
    tags:
        types,int
    '''
    cat.stack.push( type(1) )

@define(ns, 'string_type')
def string_type( cat ) :
    '''
    string_type : ( -> type:string_type)
    
    desc:
        Pushes a value representing the type of a string
        string_type: the Python type of a string
        
        Example: string_type => <type 'str'>
    tags:
        types
    '''
    cat.stack.push( type("1") )

@define(ns, 'float_type')
def float_type( cat ) :
    '''
    float_type : ( -> type:float_type)
    
    desc:
        Pushes a value representing the type of a float
        float_type: Python type of a floating point number
        
        Example: float_type => <type 'float'>
    tags:
        types
    '''
    cat.stack.push( type(1.0) )

@define(ns, 'bool_type')
def bool_type( cat ) :
    '''
    bool_type : ( -> type:bool_type)
    
    desc:
        Pushes a value representing the type of a boolean
        bool_type: Python type of a boolean
        
        Example: bool_type => <type 'bool'>
    tags:
        types
    '''
    cat.stack.push( type(True) )

@define(ns, 'list_type')
def list_type( cat ) :
    '''
    list_type : ( -> type:list_type)
    
    desc:
        Pushes a value representing the type of a list
        list_type: the Python type of a list
        
        Example: list_type => <type 'list'>
    tags:
        types
    '''
    cat.stack.push( type([]) )

@define(ns, 'function_type')
def function_type( cat ) :
    '''
    function_type : ( -> type:function_type)
    
    desc:
        Pushes a value representing the type of a Python function
        function_type: the Python type of a function
        
        Example: function_type => <type 'function'>
    tags:
        types
    '''
    cat.stack.push( type(lambda x: x) )

@define(ns, 'datetime_type')
def datetime_type( cat ) :
    '''
    datetime_type : ( -> type:datetime_type)
    
    desc:
        Pushes a value representing the type of a datetime.datetime instance
        datetime_type: Python type of a datetime
        
        Example: datetime_type => <type 'datetime.datetime'>
    tags:
        types
    '''
    import datetime

    now = datetime.datetime.now()
    cat.stack.push( type(now) )

@define(ns, 'type_eq')
def type_eq( cat ) :
    '''
    type_eq : (any:lhs any:rhs -> any:lhs any:rhs bool:TF)
    
    desc:
        Returns True if either type is assignable to the other
        The pair of types is not consumed
        lhs: a type
        rhs: a type
        TF: true if the types are the same; False otherwise
        
        Example: 123 321 type_eq => True
    tags:
        types
    '''
    r, l = cat.stack.peek_n( 2 )
    cat.stack.push( type(l) == type(r) )

@define(ns, 'stack_types')
def stack_types( cat ) :
    '''
    stack_types : ( -> list:types)
    
    desc:
        Displays a list of types represented by elements on the cat.stack
        in the same order as the element on the cat.stack with the deepest
        item first and the top item last
        types: a list of Python types, one for each object on the stack
        
        Example: 1 'zz 2.34 [3 2 1] list stack_types
    tags:
        types,stack,display,console
    '''
    typeList = []
    
    for item in cat.stack.to_list() :
        typeList.append( type(item) )
    
    cat.output( str(typeList), cat.ns.info_colour )

def _returnNS() :
    return ns
