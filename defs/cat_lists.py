# lists

from cat.namespace import *
ns = NameSpace()

@define(ns, 'sort')
def _sort( cat ) :
    '''
    sort : (list:src -> list:src_sorted)
    
    desc:
        Sorts the list on top of the stack in place
        src: the list to sort
        src_sorted: the sorted (ascending order) list
        
        Example: ['z 'y 'x 'w] list sort => ['w, 'x, 'y, 'z]
    tags:
        sort,list
    '''
    obj = cat.stack.pop()
    
    if isinstance(obj, (list, tuple)) :
        cat.stack.push( sorted(obj) )
        
    elif isinstance(obj, basestring) :
        lst = list(obj)
        lst.sort()
        cat.stack.push( "".join(lst) )
    
    else :
        cat.stack.push( obj )

@define(ns, 'zip')
def _zip( cat ) :
    '''
    zip : (list:left list:right -> list:zipped)
    
    desc:
        Creates a list of paired objects from the two lists on
        top of the stack: [[left[0],right[0]], [left[1],right[1]], ...]
        left: list of lefthand members
        right: list of righthand members
        zipped: the list of pairs
        
        Example: ['a 'b 'c] list [1 2 3] list zip => [['a, 1], ['b, 2], ['c, 3]]
    tags:
        lists,zip
    '''
    r, l = cat.stack.pop_2()
    cat.stack.push( [list(x) for x in zip(l, r)] )

@define(ns, 'unzip')
def unzip( cat ) :
    '''
    unzip : (list:zipped -> list:left list:right)
    
    desc:
        Unzips the list on top of the stack to a pair of lists that
        are then pushed onto the stack. The first element of each
        of the pairs within the argument list goes into the left list
        and the second into the right list.
        zipped: the list of pairs
        left: the left member of a pair (pair[0])
        right: the rightmember of a pair (pair[1])
        
        Example: [['a, 1], ['b, 2], ['c, 3]] unzip => ['a, 'b, 'c] [1, 2, 3]
    tags:
        lists,unzip
    '''
    lst = cat.stack.pop()
    lst = zip(*lst)
    cat.stack.push( list(lst[0]) )
    cat.stack.push( list(lst[1]) )

@define(ns, 'enum' )
def _enum( cat ) :
    '''
    enum : (list:src int:start -> list:enum_src)
    
    desc:
        Returns an enumerated list on top of the stack based on the
        starting int at [0] and the list at [-1] on the stack
        src: the list to be enumerated
        start: the value at which to start the enumeration
        enum_src: the enumerated source: [[start,src[0]], [start+1,src[1]], ...]
        
        Example: ['a 'b 'c] list 3 enum => [[3, 'a], [4, 'b], [5, 'c]]
    tags:
        lists,enum,enumerate
    '''
    start, lst = cat.stack.pop_2()
    
    if isinstance(start, (basestring, float)) :
        start = int( start )
    
    elif not isinstance(start, (int, long) ) :
        raise ValueError, "enum: Starting value must be an integer"
    
    if isinstance(lst, basestring) :
        lst = eval( lst )
    
    if not isinstance( lst, (list, tuple) ) :
        raise ValueError, "enum: The list must be an iterable or convertable to one"
    
    cat.stack.push( [ [x,y] for x,y in enumerate(lst, start)] )

@define(ns, 'all' )
def _all( cat ) :
    '''
    all : (list:items -> bool:TF)
    
    desc:
        Returns true on top of the  stack if all of the elements of the
        list on top of the stack evaluate to True
        items: the  items to be tested for true/false ( false is 0 | '' )
        TF: True if all items in the list return True; otherwise False
        
        Example: [1 'a 3] list all => True
                 [1 2 0]  list all => False
    tags:
        lists,test,all
    '''
    iter = cat.stack.pop()
    
    if isinstance(iter, basestring) :
        iter = eval( iter )
    
    if isinstance(iter, (list, tuple)) :
        cat.stack.push( all(iter) )
    
    else :
        raise ValueError, "all: Argument must be an iterable"

@define(ns, 'any' )
def _any( cat ) :
    '''
    any : (list:items -> bool:TF)
    
    desc:
        Returns true on top of the stack if any element of the list
        on top of the stack is true
        items: the list of items to test for true condition (false is 0 | '')
        TF: true if at least one item is the list is true; false otherwise
        
        Example: ['a 2 0 ""] list any => True
                 [0 ""] list any      => False
    tags:
        lists,test
    '''
    iter = cat.stack.pop()
    
    if isinstance(iter, basestring) :
        iter = eval( iter )
    
    if isinstance(iter, (list, tuple)) :
        cat.stack.push( any(iter) )
    
    else :
        raise ValueError, "any: Expect an iterable (list) on top of the stack"

@define(ns, 'nil')
def nil( cat ) :
    '''
    nil : ( -> list:empty)
    
    desc:
        Pushes an empty list onto the stack
        empty: an empty list ( [] )
        
        Example: nil => []
    tags:
        lists,empty
    '''
    cat.stack.push( [] )

@define(ns, 'unit')
def unit( cat ) :
    '''
    unit : (any:item -> list:lst)

    desc:
        Creates a list containing one element taken from the top of the stack
        item: the item to be encapsulated in a list
        lst: the list of 1 element ([item])
    test:
        in:
            42 unit
        out:
            [42]
    tags:
        lists,unit
    '''
    cat.stack.push( [cat.stack.pop()] )

@define(ns, 'pair')
def pair( cat ) :
    '''
    pair : (any:b  any: a -> list:pair)
    
    desc:
        Makes a list of the top two cat.stack elements ([[-1] [0]])
        b: any object
        a: any object
        pair: the list of two objects ([b, a])
        
        Example: longitude latitude pair => [longitude latitude]
    tags:
        lists,pair,tuple
    '''
    t, n = cat.stack.pop_2()
    cat.stack.push( [n, t] )

@define(ns, 'triplet')
def triplet( cat ) :
    '''
    pair : (any:a any:b any:c -> list:triple[a, b, c])
    
    desc:
        Makes a list of the top three cat.stack elements [[-2] [-1] [0]]
        a: becomes first element of list (triple[0])
        b: becomes second member of the list (triple[1])
        c: becomes the third member of the list (triple[2])
        triple: the list of three elements([a, b, c])
        
        Example: longitude latitude elevation triplet => [longitude, latitude, elevation]
    tags:
        list,triplet
    '''
    t, n, nn = cat.stack.pop_n( 3 )
    cat.stack.push( [nn, n, t] )

@define(ns, 'n_tuple')
def nTuple( cat ) :
    '''
    n_tuple : (any:elt_n any:elt_n-1 ... any:elt_1 int:n -> list:ntuple)
    
    desc:
        Creates a list from n elements on the cat.stack
        element at [0] is the number of elements
        elements at [-1] through [-n] are made into a list
        elt_n: the n-th object on the stack [-n]
        
        Example: 'a 1 2 3 'b 5 n_tuple => ['a. 1, 2, 3, 'b]
    tags:
        ntuple,list
    '''
    n   = int( cat.stack.pop() )
    lst = cat.stack.pop_n( n )
    lst.reverse()
    cat.stack.push( lst )
    
@define(ns, 'range')
def _range( cat ) :
    '''
    range : ( int:n -> list:[0, 1, ... n-1] )
    
    desc:
        Using the integer on top of the stack, a list of sequential integers
        is pushed onto the stack according to the action of the standard
        Python range() function
        n: the ending barrier for the list
        
        Example: 5 range => [0, 1, 2, 3, 4]
    tags:
        range,lists,numeric_sequence
    '''
    rng = range( int(cat.stack.pop()) )
    cat.stack.push( rng )

@define(ns, 'len')
def count( cat ) :
    '''
    len : (list|string|dict:src -> list|string|dict:src int:length)
    
    desc:
        Returns the number of items in a list or of characters in a string or of keys
        in a dict. The list, string or dict is not destroyed.
        src: the source list, string, or dict
        len: the numeber of elements in the list, string, or dict
        
        Example: [1 2 3] list len  => 3
                 "test string" len => 11
    tags:
        lists,length,size,string,dict
    '''
    cat.stack.push( len(cat.stack.peek()) )

@define(ns, 'head')
def head( cat ) :
    '''
    head : ( list:src -> src[0] )
    
    desc:
        Replaces the list at [0] with its first member
        src: source list
        
        Example: [1 2 3] list head => 1
                 'abc head         => 'a
    tags:
        lists,head
    '''
    cat.stack.push( cat.stack.pop()[0] )

@define(ns, 'first')
def first( cat ) :
    '''
    first : (list:src -> list:src src[0])
    
    desc:
        The first member of the list at [0] is pushed onto the stack
        the source list is unaltered
        src: the source list
        
        Example: [1 2 3] list first => [1, 2, 3] 1
                 'abc first => 'abc 'a
    tags:
        lists,first
    '''
    cat.stack.push( cat.stack.peek()[0] )

@define(ns, 'rest,tail')
def rest( cat ) :
    '''
    rest : ( list:src -> list:src[1:] )
    tail : ( list:src -> list:src[1:] )
    
    desc:
        Removes the first member from the list on top of the stack
        src: the source list
        
        Example: [1 2 3] list rest    => [2, 3]
                 ['a 'b 'c] list tail => ['b, 'c]
                 'abc rest            => 'bc
    tags:
        lists,rest,remainder
    '''
    cat.stack.push( cat.stack.pop()[1:] )

@define(ns, 'rev')
def rev( cat ) :
    '''
    rev : (list:obj|string:obj -> list|string:reversed_obj)
    
    desc:
        Reverses the order of members of the object on top of the stack.
        The object may be a list or a string
        obj: the object to be reversed
        reversed_obj: the reversed list or string
        
        Example: [1 2 3] list rev => [3, 2, 1]
                 "Hello world!" rev => "!dlrow olleH"
    tags:
        lists,reverse,string
    '''
    val = cat.stack.pop()
    
    if isinstance(val, basestring) :
        cat.stack.push( val[::-1] )
    
    else :
        val.reverse()
        cat.stack.push( val )

@define(ns, 'cons')
def cons( cat ) :
    '''
    cons : (list:base any:item -> list:new)
    
    desc:
        Appends an item to the right end of a list
        base: the list to which to append an item
        item: item to append to the list
        new: list extended with item as its new last member
        
        Example: [1 2 3] list 4 cons => [1, 2, 3, 4]
                 1 2 cons            => [1, 2]
    tags:
        lists,cons,concatenate
    '''
    t   = cat.stack.pop()
    lst = cat.stack.peek()
    
    if isinstance(lst, (list, tuple)) :
        lst.append( t )
    
    else :
        lst = cat.stack.pop()
        cat.stack.push( [lst, t] )

@define(ns, 'uncons')
def uncons( cat ) :
    '''
    uncons : (list:base -> list:smaller any:item)
    
    desc:
        Returns the right end of the list, and the rest of a list
        base: the list whose rightmost member is to be removed
        smaller: the list without its former last member
        item: former last member of the list
        
        Example: [1 2 3] list uncons => [1, 2] 3
    tags:
        lists,unconcatenate
    '''
    x = cat.stack.pop()
    
    if isinstance(x, (list, tuple)) :
        y = x.pop()
        cat.stack.push( x )
        cat.stack.push( y )
    
    else :
        raise ValueError, "uncons: Argument on top of stack must be a list"

@define(ns, 'concat')
def concat( cat ) :
    '''
    cat : (list:left list:right -> list:joined)
    
    descr:
        Concatenates two lists (same as using "+")
        left: the list whose elements will for the left pare of the new list
        right: the list whose elements will form the right part of the new list
        joined: the new list = left + right
        
        Example: [1 2] list ['a 'b] list concat => [1, 2, 'a, 'b]
                 [1 2] list ['a 'b] list +      => [1, 2, 'a, 'b]
    tags:
        lists,concatenation
    '''
    r, l = cat.stack.pop_2()
    
    if not isinstance(r, (list, tuple)) :
        r = [ r ]
    
    if not isinstance(l, (list, tuple)) :
        l = [ l ]
    
    cat.stack.push( l + r )

@define(ns, 'get_at')
def get_at( cat ) :
    '''
    get_at : (list:base int:index -> list:base any:item_n)
    
    desc:
        Returns the n-th item in a list. The list is not consumed.
        base: the basis list
        index: the zero-based offset into the list (0..len(base))
        item_n: item = base[index]
        
        Example: ['a 'b 'c] list 1 get_at => ['a, 'b, 'c] 'b
    tags:
        lists,index,get
    '''
    ix  = int( cat.stack.pop() )
    lst = cat.stack.peek()
    cat.stack.push( lst[ix] )

@define(ns, 'set_at')
def set_at( cat ) :
    '''
    set_at : (list:base any:value int:index -> list:new)
    
    desc:
        Sets an item in a list: list[index] = value
        base: the source list
        value: the replacement value
        index: the offset into the list at which replacement is to be effected
        new: the base list with its index-th element set to 'value'
        
        Example: [1 2 3 4 5] list 'q 2 set_at => [1, 2, 'q, 4, 5]
    tags:
        lists,index,set
    '''
    ix, val = cat.stack.pop_2()
    lst     = cat.stack.peek()
    lst[int(ix)] = val

@define(ns, 'swap_at')
def swap_at( cat ) :
    '''
    swap_at : (list:base any:value int:index -> list:new any:swappedOutVal)
    
    desc:
        Swaps an item with an item in the list
        base: the list to be manipulated
        value: the value to be swapped for a specified one in the base list
        index: the offset into the list locating value to be swapped out
        new: base list with new value
        swappedOutValue: the value at base[index]
        
        Example: [1 2 'q 3 4] list 2.5 2 swap_at => [1, 2, 2.5, 3, 4] 'q
    tags:
        lists,index,swap
    '''
    n     = int( cat.stack.pop() )
    obj   = cat.stack.pop()
    lst   = cat.stack.peek()
    x     = lst[n]
    lst[n] = obj
    cat.stack.push( x )

@define(ns, 'empty')
def empty( cat ) :
    '''
    empty : (list|string|dict:base -> list|string|dict:base bool:TF)

    desc:
        Pushes True onto the stack if the list, string. or dict is empty
        base: the list, string or dict to be tested
        TF: True if the list, string, or dict is empty; False otherwise
        
        Example: [1 2 3] list empty => False
                 "ab cd" empty      => False
                 [] empty           => True
                 "" empty           => True
    tags:
        list,string,conditional,dict
    '''
    lst = cat.stack.peek()
    cat.stack.push( len(lst) == 0 )

@define(ns, 'explode')
def explode( cat ) :
    '''
    explode : (list:base -> base[0] base[1] ... base[n])
    
    desc:
        Pushes elements of the list onto the stack in left-to-right order
        base: the list to 'explode'
        base[i]: the i-th element of the base list
        
        Example: [1 2 3] list explode => 1 2 3
                 'abcd explode        => 'a 'b 'c 'd
    tags:
        lists,explode,string
    '''
    obj = cat.stack.pop()
    
    if isinstance( obj, (basestring, list, tuple) ) :
        for elt in obj :
            cat.stack.push( elt )
    
    else :
        raise ValueError, "explode: cannot explode object"

@define(ns, 'list_to_str')
def list_to_str( cat ) :
    '''
    list_to_str : (list:base string:separator -> string:strung_out_list)
    
    desc:
        Creates a string by concatenating the string representations of items
        in the list on top of the stack separated by the separator string
        separator: string
        base: the list to be converted to a string
        separator: the string (often a 1-character string)
                    used to 'glue' the list elements together
        
        Example: ['a 'b 'c] list '& list_to_str         => "a&b&c"
                 ['Princess 'Edna] list " " list_to_str => "Princess Edna"
    tags:
        string,list,conversion,join
    '''
    sep, lst = cat.stack.pop_2()
    cat.stack.push( sep.join([str(x) for x in lst]) )

@define(ns, 'list_to_hash,list_to_dict')
def list_to_hash( cat ) :
    '''
    list_to_hash : (list:base -> dict:newDict)
    list_to_dict : (list:base -> dict:newDict)
    
    desc:
        Converts a list of pairs to a hash_list (dictionary) and
        leaves the new hash list on top of the stack
        base: a list of pairs where each item (pair) consists of two members:
                [key, value]. (See 'zip' word)
        newDict: a dictionary (hash_list) populated from the base list
        
        Example: [['a 1] list ['b 2] list ['c 3] list] list list_to_hash => {'a': 1, 'c': 3, 'b': 2}
    tags:
        hash,hash_list,list,dictionary,hash_table
    '''
    top = cat.stack.pop()
    
    if isinstance(top, (list, tuple)) :
        cat.stack.push( dict(top) )
    
    else :
        raise ValueError, "list_to_hash: Expect a list on top of the stack"

@define(ns, 'py_list')
def pyList( cat ) :
    '''
    py_list : (string|any:arg -> list:new)
    
    desc:
        Converts a string to a list
        string formats:
            "1,2,3,4,'x'"
            "zzz"
            "[1,2,3,4,'x']"
            "(1,2,3,4,'x')"
        other format:
            any (e.g. 3.14)
        arg: list or string to be expanded into a list
        new: the list created from the source string or list
        
        Example: "1,2,3,4,'x'" py_list   => ['1, '2, '3, '4, 'x]
                 'zzz py_list            => ['z, 'z, 'z]
                 "[1,2,3,4,'x']" py_list => [1, 2, 3, 4, 'x']
                 "(1,2,3,4,'x')" py_list => [1, 2, 3, 4, 'x']
    tags:
        string,list
    '''
    lst = cat.stack.pop()
    
    if isinstance(lst, (list, tuple)) :
        lst = list( lst )
    
    elif isinstance(lst, basestring) :
        if lst[0] in "[(" :
            lst = list( eval(lst) )
        
        elif lst.count(",") > 0 :
            lst = [x for x in lst.split(",")]
        
        else :
            lst = list( lst )
    
    else :
        lst = [lst]
    
    cat.stack.push( lst )

@define(ns, 'as_list,to_list')
def as_list( cat ) :
    '''
    as_list : (any:item -> list:new)
    to_list : (any:item -> list:new)
    
    desc:
        Casts a variant to a (Python) list (like 'unit' word).
        item: the item to be cast to a list
        new: the list so created
        
        Example: 23 as_list   => [23]
                 'abc as_list =>['abc]
    tags:
        list,conversion
    '''
    obj = cat.stack.pop()
    
    if isinstance(obj, (list, tuple)) :
        cat.stack.push( list(obj) )
    
    elif isinstance(obj, basestring) :
        if obj[0] in '[(' :
            cat.stack.push( list(eval(obj)) )
    
    else :
        cat.stack.push( [obj] )

@define(ns, 'stack_to_list')
def stackToList( cat ) :
    '''
    stack_to_list : (A -> A list:A)
    
    desc:
        Copies the entire stack into a list and pushes it onto the stack
        A: contents of the stack
        
        Example: 1 2 3 stack_to_list             => 1 2 3 [1, 2, 3]
                 1 2 3 stack_to_list [clear] dip => [1, 2, 3]
    tags:
        lists,stack
    '''
    cat.stack.push( cat.stack.to_list() )

@define(ns, 'hash_to_list,dict_to_list')
def hash_to_list( cat ) :
    '''
    hash_to_list : (dict:hash_list -> list:zip_list)
    dict_to_list : (dict:hash_list -> list:zip_list)
    
    desc:
        Converts a hash_list to a list of pairs
        hash_list: a dictionary (hash_list)
        zip_list: a list of pairs: [[key1, value1],[key2, value2], ...]
        
        Example: step 1: [['a 1] list ['b 2] list ['c 3] list] list list_to_hash => {'a': 1, 'c': 3, 'b': 2}
                 step 2: hash_to_list => [['a', 1], ['c', 3], ['b', 2]]
    tags:
        hash,dictionary,hash_table,list,zip
    '''
    dict = cat.stack.pop()
    cat.stack.push( [list(i) for i in dict.items()] )

@define(ns, 'bin_op')
def bin_op( cat ) :
    '''
    bin_op : (list:lhs list:rhs function:operation -> list:res)
    
    desc:
        Puts the i-th argument from each list on the stack, then
        applies the function originally on top of the stack to the two arguments
        and appends the result left on top of the stack to a list
        The result list is finally returned on top of the stack
        lhs: a list of items serving as the lefthand side of the binary operation
        rhs: a list of items serving as the righthand side of the binary operation
        operation: a function creating a new value from elements of the two source lists
                    lhs[k] <bin_op> rhs[k] where k in range(min(len(lhs),len(rhs)))
        res: the resulting list of values
        
        Example: [1 2 3] list [3 2 1] list [mul] bin_op => [3, 4, 3]
                 [1 2 3] list [3 2 1] list [lt] bin_op  => [True, False, False]
    tags:
        lists,mathematics,binary
    '''
    f, r, l = cat.stack.pop_n( 3 )
    
    if len(l) != len(r) :
        raise ValueError, "bin_op: Lists must be of the same length"
    
    with cat.new_stack() :
        result = [ ]
        n      = len( r )
        
        for i in range(n) :
            cat.stack.push( l[i] )
            cat.stack.push( r[i] )
            cat.eval( f )
            
            if cat.stack.length() > 0 :
                result.append( cat.stack.pop() )
            
            else :
                result.append( None )
    
    cat.stack.push( result )

@define(ns, 'hash_list,dict')
def hash_list( cat ) :
    '''
    hash_list : (-> dict:hash_list)
    dict      : (-> dict:hash_list)
    
    desc: 
        Makes an empty hash list (dictionary)
        hash_list: the new dictionary (hash_list)
        
        Example: hash_list => { }
                 dict      => { }
    tags:
        hash,dictionary,hash_table,hash_list,lists
    '''
    cat.stack.push( {} )

@define(ns, 'hash_get,dict_get')
def hash_get( cat ) :
    '''
    hash_get : (dict:hash_list any:key -> dict:hash_list any:value)
    dict_get : (dict:hash_list any:key -> dict:hash_list any:value)
    
    desc:
        Gets a value from a hash list using a key
        hash_list: a dictionary (or hash_list)
        key: the key into the dictioonary
        value: the value associated with the key
        
        Example: step 1: [['a 1] list ['b 2] list ['c 3] list] list list_to_hash => {'a': 1, 'c': 3, 'b': 2}
                 step 2: 'b hash_get => 2
    tags:
        hash,dictionary,hash_table
    '''
    key  = cat.stack.pop()
    dict = cat.stack.peek()
    
    if key in dict :
        cat.stack.push( dict[key] )
    
    else :
        raise KeyError, "hash_get: No hash list entry for key " + str(key)

@define(ns, 'hash_set,dict_set')
def hash_set( cat ) :
    '''
    hash_set : (hash_list any:value any:key -> hash_list)
    dict_set : (hash_list any:value any:key -> hash_list)
    
    desc:
        Associates the second value with a key (the top value) and adds it to the
        hash list (dict). If the key is already present it is overwritten.
        hash_list: a dictionary (or hash_list)
        key: the key into the dictioonary
        value: the value associated with the key
        
        Example: step 1: [['a 1] list ['b 2] list ['c 3] list] list list_to_hash => {'a': 1, 'c': 3, 'b': 2}
                 step 2: 4 'd hash_set => {'a': 1, 'c': 3, 'b': 2, 'd' : 4}
    tags:
        hash,dictionary,hash_table,set
    '''
    key, val  = cat.stack.pop_2()
    dict      = cat.stack.peek()
    dict[key] = val

@define(ns, 'hash_add,dict_add')
def hash_add( cat ) :
    '''
    hash_add : (dict:hash_list any:value any:key -> dict:hash_list)
    dict_add : (dict:hash_list any:value any:key -> dict:hash_list)
    
    desc:
        Associates the second value with a key (the top value) in a hash list if the
        key is not already present.
        hash_list: a dictionary
        value: the value to be associated with the key in the dictionary
        key: the key under which the value is added to the dictionary
        
        Example: step 1: [['a 1] list ['b 2] list ['c 3] list] list list_to_hash => {'a': 1, 'c': 3, 'b': 2}
                 step 2: 4 'd hash_add => {'a': 1, 'c': 3, 'b': 2, 'd' : 4}
    tags:
        hash,dictionary,hash_table,add
    '''
    key, val  = cat.stack.pop_2()
    dict      = cat.stack.peek()
    
    if key not in dict :
        dict[key] = val
    
    else :
        cat.stack.push( (val, key), multi=True )
        raise Warning, "hash_add: Key already present in hash list. Use 'hash_set' to replace"

@define(ns, 'hash_contains,dict_contains')
def hash_contains( cat ) :
    '''
    hash_contains : (dict:hash_list any:key -> dict:hash_list bool:TF)
    dict_contains : (dict:hash_list any:key -> dict:hash_list bool:TF)
    
    desc:
        Returns True if hash list contains key; otherwise, False
        hash_list: a dictionary (aka hash_list)
        key: the key to search for
        TF: True if the dictionary has the key; False otherwise
        
        Example: step 1: [['a 1] list ['b 2] list ['c 3] list] list list_to_hash => {'a': 1, 'c': 3, 'b': 2}
                 step 2: 'b hash_contains => True
    tags:
        hash,dictionary,hash_table,member,contains,test,key
    '''
    key  = cat.stack.pop()
    dict = cat.stack.peek()
    cat.stack.push( key in dict )

@define(ns, 'map')
def map( cat ):
    '''
    map : (list:base function:transform -> list:new)
    
    desc:
        Creates a list from another by transforming each value using the supplied function
        base: the source list
        transform: the transformation function taking each list element in turn
                    and transforming it into a new element (or none)
        new: the list resulting from the transform function
        
        Example: [1 3 5] list [math.sqrt] map => [1.0, 1.7320508075688772, 2.23606797749979]
    tags:
        lists,map,function
    '''
    func, elements = cat.stack.pop_2()
    
    # Evaluate the function with each of the elements.
    results  = []
    
    # Push the value onto the stack and evaluate the function.
    for element in elements :
        cat.stack.push( element )
        cat.eval( func )
        results.append( cat.stack.pop() )
    
    cat.stack.push( results )

@define(ns, 'filter')
def filter( cat ) :
    '''
    filter : ( list:base function:test -> list:new )
    
    desc:
        Applies the function on the top of the stack to each element of the list
        immediately below it. If the result of the function is True (or non-zero)
        the corresponding element in the list (the argument to the function) is
        pushed onto a new list. When all elements of the argument list have been
        examined the results list being created is pushed onto the stack.
        base: the source list
        test: a function returning true or false depending on the element from the base list
        new: a list of elements from the base list whose test function returned True
        
        Example: [1 2 3] list [dec gtz] filter => [2, 3]
    tags:
        lists,functions,filter
    '''
    func, elements  = cat.stack.pop_2()
    results         = []
    
    for element in elements :
        cat.stack.push( element )
        cat.eval( func )
        
        if cat.stack.pop() :
            results.append( element )
    
    cat.stack.push( results )

@define(ns, 'fold,reduce')
def fold( cat ) :
    '''
    fold   : (list:base any:init func:transform -> any:result)
    reduce : (list:base any:init func:transform -> any:result)
    
    desc:
        Also known as a reduce function, this combines adjacent values in a list
        using an initial value and a binary function.
        base: the list to be 'reduced'
        init: the initial value required by the 'transform' function
        transform: the function applied to two variables: transform(init,base[k])
        result: the result of the reduction
    test:
        in:
            [1 2 3 4] list 0 [add] fold
        out:
            10
    test:
        in:
            [1 2 3 4] list 0 [popd] reduce
        out:
            1
    tags:
        lists,reduce

    '''
    f, init, a = cat.stack.pop_n( 3 )
    
    for x in a :
        cat.stack.push( init )
        cat.stack.push( x )
        cat.eval( f )
        init = cat.stack.pop()
    
    cat.stack.push( init )

@define(ns, 'list')
def _list( cat ) :
    '''
    list : (function:generator -> list:result)
    
    desc:
        Creates a list from a function
        generator: a function that when executed will generate a list
        result: the list so created
    
    Example: [ 0 [inc] 5 repeat ] list => [5]
             [1 2 3] list              => [1, 2, 3]
    tags:
        lists,generator
    '''
    func = cat.stack.pop()
    
    with cat.new_stack() :
        cat.eval( func )
        newlst = cat.stack.to_list()

    cat.stack.push( newlst )

@define(ns, 'cross_prod')
def cross_prod( cat ) :
    '''
    cross_prod : (list:lhs list:rhs -> list:cross_product)
    
    desc:
        Computes the standard 3-D vector cross product
        lhs: the lefthand vector of exactly 3 elements
        rhs: the righthand vector of exactly 3 elements
        cross_product: a vector of exactly 3 elements
        
        Example: [1 2 3] list [2 3 4] list cross_prod => [-1, 2, -1]
    tags:
        list,vectors,cross_product
    '''
    r, l = cat.stack.pop_2()
    
    if len(l) != 3 or len(r) != 3 :
        raise ValueError, "cross_prod: Both vectors must each be of length 3"
    
    a1, a2, a3 = l
    b1, b2, b3 = r
    c = [ a2 * b3 - b2 * a3, a3 * b1 - b3 * a1, a1 * b2 - b1 * a2 ]
    cat.stack.push( c )

@define(ns, 'dot_prod')
def dotProduct( cat ) :
    '''
    dot_prod : (list:l1 list:l2 -> float:dprod)
    
    desc:
        Computes the dot product of two lists
        If the lists are of unequal length, the length of the shorter list is used
        l1: first list of numbers
        l2: second list of numbers
        dprod: the dot product
        
        Example: [1 2 3] list [4 5 6] list dot_prod => 32.0
    tags:
        list,vector,product,dot_product,dot
    '''
    l1, l2 = cat.stack.pop_2()
    n      = min( len(l1), len(l2) )
    sum    = 0.0
    
    for i in range(n) :
        sum += l1[i] * l2[i]
    
    cat.stack.push( sum )

@define(ns, 'powers')
def powers( cat ) :
    '''
    powers : ( int:base int:max_exponent -> list:powers)
    
    desc:
        Pushes a list of powers of a base number onto the stack in descending order of exponent.
        I.e. x 3 powers -> [x**3, x**2, x**1, x**0] for some value x
        base: the number tht serves as the base for exponentiation
        max_exponent: how high the powers are to go (inclusive)
        powers: powers in descending order
        
        Example: 5 4 powers => [625, 125, 25, 5, 1]
    tags:
        mathematics,polynomials,lists,powers
    '''
    n, x = cat.stack.pop_2()
    
    if not isinstance(n, (int, long)) :
        raise ValueError, "powers: Exponent must be an integer"
    
    if not isinstance(x, (int, long, float)) :
        raise ValueError, "powers: Base must be a number"
    
    l    = [x**i for i in range(n + 1)]
    l.reverse()
    cat.stack.push( l )

@define(ns, 'poly')
def poly( cat ):
    '''
    poly : (list:coeffs nbr:x -> nbr:value)
    
    desc:
        Calculate the value of a polynomial with coefficients 'a' at point x.
        The polynomial is a[0] + a[1] * x + a[2] * x^2 + ...a[n-1]x^(n-1)
        the result is
            a[0] + x*(a[1] + x*(a[2] +...+ x*(a[n-1])...)
        This implementation is also known as Horner's Rule.
        coeffs: a list of coefficients [c0, c1, ...]. low to high degree order
        x: the point at which to evaluate the polynomial
        value: the result of the polynomial evaluation
        
        Example: [1 -2 1] list 3 poly => 4
    tags:
        mathematics,polynomials,evaluation,Horner,rule
    '''
    x, a = cat.stack.pop_2()
    
    n = len( a ) - 1
    p = a[n]
    
    for i in range( 1, n + 1 ) :
        p = p * x + a[n - i]
    
    cat.stack.push( p )

@define(ns, 'in_list')
def in_list( cat ) :
    '''
    in_list : (list:haystack any:needle -> boolean:TorF
    
    desc:
        Searches a list for a value. Returns true or false on top of the stack.
        haystack: the list to be searched
        needle: the item to be found in the 'haystack'
        TorF: true is pushed onto the stack if the needle is found in the haystack
              false is pushed onto the stack if the needle is not found in the haystack
        
        Example: ['a 'b 'c 'd] list 'c in_list => True
                 ['a 'b 'c 'd] list  3 in_list => False
    tags:
        list,search,find,contains
    '''
    needle, haystack = cat.stack.pop_2()
    cat.stack.push( needle in haystack )

def _returnNS() :
    return ns
