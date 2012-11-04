# string manipulation

from cat.namespace import *
ns = NameSpace()

@define(ns, 'str_cat')
def strCat( cat ) :
    '''
    str_cat : (string:lhs string: rhs -> string:lhsrhs
    
    desc:
        Concatenates the two strings on top of the stack and pushes
        the result onto the stack.
        lhs: the left-hand string portion
        rhs: the right-hand string portion
        lhsrhs: the concatenated string
        
        Example: 'abc 'def str_cat => 'abcdef
    tags:
        string,concatenate,cat
    '''
    r, l = cat.stack.pop_2()
    cat.stack.push( str(l) + str(r) )

@define(ns, 'strlen')
def strLen( cat ) :
    '''
    strlen : (string:lhs -> string:lhs int:length
    
    desc:
        Pushes the length of the string on top of the stack onto the stack.
        lhs: the left-hand string portion
        length: the length of string
        
        Example: "this is a test" strlen => "this is a test" 14
    tags:
        string,length,len,strlen
    '''
    strng = cat.stack.peek()
    cat.stack.push( len(strng) )

@define(ns, 'split')
def split( cat ) :
    '''
    split : (string:target string:splitter -> list)
    
    desc:
        Splits a target string into segments based on the 'splitter' string
        target: the string to be split apart
        splitter: the string to be used to split the target. Note: the splitter
                    value "" (empty string) will split apart letters of a string
        
        Example: 'abcd "" split             => ['a, 'b, 'c, 'd]
                 "one if by land" " " split => ['one, 'if, 'by, 'land]
                 "tag1,tag2,tag3" ', split  => ['tag1, 'tag2, 'tag3]
    tags:
        string,split,list
    '''
    splitter, target = cat.stack.pop_2()
    
    if not isinstance(target, basestring) or not isinstance(splitter, basestring) :
        raise ValueError, "split: Both arguments must be strings"
    
    if len(splitter) == 0 :
        cat.stack.push( [x for x in target] )
    
    else :
        cat.stack.push( target.split(splitter) )

@define(ns, 'join')
def join( cat ) :
    '''
    join : (list:src string:connector -> string)
    
    desc:
        Joins together the elements of the list at [-1] using the connector
        string at [0].
        src: the list of values
        connector: the connector used to 'glue' the values together as a string
        
        Example: ['one 'if 'by 'land] list " " join => "one if by land"
    tags:
        string,list,join
    '''
    conn, lst = cat.stack.pop_2()
    
    if not isinstance(conn, basestring) :
        conn = str( conn )
    
    if not isinstance(lst, (list, tuple)) :
        lst = [lst]
    
    lst = [ str(x) for x in lst ]
    cat.stack.push( conn.join( lst ) )

@define(ns, 'count_str')
def count_str( cat ) :
    '''
    count_str : (string:target string:test -> string:target int)
    
    desc:
        Counts the number of non-overlapping occurrences of the test string at [0]
        found in the target string at [-1]
        target: the string to be searched
        test: the test string
        
        Example: "Hey nonny, nonny, ho" 'nonny count_str => 2
    tags:
        string,count
    '''
    test, target = cat.stack.pop_2()
    
    if not isinstance(test, basestring) or not isinstance(target, basestring) :
        raise ValueError, "count_str/strlen: Both target and test objects must be strings"
    
    cat.stack.push( target )
    cat.stack.push( target.count(test) )

@define(ns, 'subseq')
def subseq( cat ) :
    '''
    subseq : (list|string:src int:start int:end -> list|string: src list|string:result)
    
    desc:
        Pushes a segment of a list or a string onto the stack
        src: the list or string to be sliced
        start: the starting offset
        end: the end barrier
        result: the extracted sublist or substring
        
        Example: [1 2 3 4 5] list 2 5 subseq => [1, 2, 3, 4, 5] [3, 4, 5]
                 "Bovril prevents that sinking feeling" 7 15 subseq => "Bovril prevents that sinking feeling" 'prevents
    tags:
        list,string,slice,subsequence
    '''
    end, start = cat.stack.pop_2()
    lst        = cat.stack.peek()
    cat.stack.push( lst[int(start) : int(end)] )

@define(ns, 'to_str,as_string')
def to_str( cat ) :
    '''
    to_str : (any:obj -> string:str)
    
    desc:
        Coerces any value to a string if possible
        obj: the object to be "stringified"
        str: the resulting string
        
        Example: 123 to_str             => "123"
                 [1 2 3] list as_string => "[1, 2, 3]"
    tags:
        conversion,string
    '''
    cat.stack.push( str(cat.stack.pop()) )

@define(ns, 'bin_str')
def bin_str( cat ) :
    '''
    bin_str : (int:nbr -> string:ans)
  
    desc:
        Converts an integer into its binary string representation.
        int: the number to convert
        ans: the string representation in binary of the number
        
        Example: 123 bin_str => '0b1111011
    tags:
        string,mathematics,conversion,binary,number
    '''
    cat.stack.push( bin(int(cat.stack.pop())) )

@define(ns, 'format')
def format( cat ) :
    '''
    format : (list:args string:format -> string:ans)
    
    desc:
        Returns a string as formatted by the format statement on top of the based
        on the argument values in the LIST below the format.
        Uses Python format conventions.
        args: a list of formattable values
        format: the format string
        ans: the formatted string
        
        Example: [1 3.14 'xx] list "int=%d, float=%f, string=%s" format => "int=1, float=3.140000, string=xx"
    tags:
        string,format,conversion
    '''
    fmt, vals = cat.stack.pop_2()
    
    if not isinstance(vals, (list,tuple)) :
        vals = [vals]
    
    if not isinstance(fmt, basestring) :
        raise ValueError, "format: Format must be a string"
        
    cat.stack.push( fmt % tuple(vals) )

@define(ns, 'hex_str')
def hex_str( cat ) :
    '''
    hex_str : (int:val -> string:str)
    
    desc:
        Converts a number into a hexadecimal string representation.
        val: the number to be "hexified"
        str: the resulting string representing the value of the number
             in hexadecimal notation
        
        Example: 123 hex_str => '0x7b
    tags:
        string,mathematics,conversion,hexadecimal,hex
    '''
    cat.stack.push( hex(int(cat.stack.pop())) )

@define(ns, 'new_str')
def new_str( cat ) :
    '''
    new_str : ( string:src int:n -> string:new_str )
    
    desc:
        Create a new string on top of the stack from a string and a count
        src: the string to be replicated
        n: number of replications
        new_str: the resulting string
        
        Example: "xY" 3 new_str => 'xYxYxY
    tags:
        string
    '''
    n, c = cat.stack.pop_2()
    s = eval( "'%s' * %d" % (str(c), int(n)) )
    cat.stack.push( s )

@define(ns, 'index_of')
def index_of( cat ) :
    '''
    index_of : (string:target string:test -> int:index)
    
    desc:
        Returns the zero-based index of the starting position of a test string in
        a target string or the index of the test object in a list.
        Returns -1 if not found.
        target: the string to be searched
        test: the search string
        index: the offset into the target string where the test string starts
                (-1 => failure)
        
        Example: "Bovril prevents that sinking feeling" 'prevents index_of => 7
                 ['a 'b 'c 'd] list 'c index_of                            => 2
                 ['a 'b 'c 'd] list 'q index_of                            => -1
    tags:
        string,search,index_of,index,find,substring
    '''
    tst,tgt  = cat.stack.pop_2()
    
    if isinstance(tgt, (list, tuple)) :
        try :
            cat.stack.push( tgt.index(tst) )
        
        except :
            cat.stack.push( -1 )
    
    else :
        cat.stack.push( str(tgt).find(tst) )

@define(ns, 'rindex_of')
def rindex_of( cat ) :
    '''
    rindex_of : (string:target string:test -> int:index)
    
    desc:
        Returns the index of the last position of a test string in a target string
        or the last index of the test object in a list. Returns -1 if not found.
        The source string/list is not disturbed
        target: the string/list to be searched
        test: the search string
        index: the offset into the string or list where the test object is to be
               found (-1 => failure)
        
        Example: "Oh what is that that you are reading?" 'that rindex_of           => 16
                 "Oh what is that that you are reading?" " " split 'that rindex_of => 4
                 "Oh what is that that you are reading?" 'thet rindex_of           => -1
    tags:
        string,search,find,subsequence,right
    '''
    tst, tgt = cat.stack.pop_2()
    
    if isinstance(tgt, (tuple, list)) :
        n = len(tgt)
        tgt.reverse()
        
        try :
            ix = tgt.index(tst)
        
        except :
            cat.stack.push( -1 )
            return
        
        cat.stack.push( n - ix - 1 )
    
    else :
        cat.stack.push( str(tgt).rfind(tst) )

@define(ns, 'replace_str')
def replace_str( cat ) :
    '''
    replace_str : (string:target string:test string:replace -> string:str)
    
    desc:
        Replaces a test string within a target string with a replacement string
        target: the string to suffer replacement action
        test: the string within the target string to be replaced
        replace: the replacement string
        str: the string with replacements
        
        Example: "Bovril prevents that sinking feeling" 'Bovril "Old Sloshingfroth Beer" replace_str =>
                    "Old Sloshingfroth Beer prevents that sinking feeling"
    tags:
        string,replace
    '''
    rpl, tst, tgt = cat.stack.pop_n( 3 )
    cat.stack.push( str(tgt).replace(str(tst), str(rpl)) )

@define(ns, 'str_to_list')
def str_to_list( cat ) :
    '''
    str_to_list : (string:src -> list:lst)
    
    desc:
        Explodes the string on top of the stack into a list of individual letters
        src: the source string
        lst: the list of constituent letters
        
        Example: "Just an abc" explode => 'J 'u 's 't " " 'a 'n " "c 'a 'b 'c
    tags:
        string,list,explode
    '''
    s = cat.stack.pop()
    cat.stack.push( [x for x in str(s)] )

@define(ns, 'oct_str')
def oct_str( cat ) :
    """
    oct_str : (int:src -> string:str)
    
    desc
        Pushes the octal string representation of the number on top of the stack
        onto the stack
        src: the integer to be converted to an octal string
        str: the resulting string representation of the value in octal
        
        Example: 123 oct_str => '0173
    tags:
        string,conversion,octal,integer
    """
    cat.stack.push( oct(int(cat.stack.pop())) )

@define(ns, 'str_as_hex')
def str_as_hex( cat ) :
    """
    str_as_hex : (string:src -> string:str_as_hex)
    
    desc
        Pushes the hex character representation of the string onto the stack
        src: the string to be converted to a string of hex characters
        str_as_hex: the resulting string representation of the source as hex digits
        
        Example: "Hello, world!" str_as_hex => '48.65.6c.6c.6f.2c.20.77.6f.72.6c.64.21
    tags:
        string,conversion,hex
    """
    s  = cat.stack.pop()
    ss = [hex(ord(x)) for x in s ]
    sss = ".".join( ss )
    cat.stack.push( sss.replace("0x", "") )

def _returnNS() :
    return ns
