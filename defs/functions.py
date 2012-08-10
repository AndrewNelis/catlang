"""

    Builtin function definitions.


    Note that many words are defined like:

        @define('int')
        def _int(...):
            ...

    with the leading underscore so that we don't overwrite builtins.
"""

import sys

from cat.namespace import define


@define('+')
@define('add')
@define('str_cat')
def add(cat):
    """
        add : (nbr nbr -> nbr)

        desc:
            adds top two numbers on the stack returning the sum on top of the stack
            Note that if instead of numbers one has other objects such as strings
            or lists, they will be concatenated.

        tags:
            level0,mathematics
    """
    a, b = cat.pop_2()
    return cat.push(b + a)


@define('-')
def sub(cat):
    """
    sub : (nbr nbr -> nbr)

    desc:
        subtracts the number at [0] from that at [-1] returning
        the difference to the top of the stack.

    tags:
        level0,mathematics
    """
    a, b = cat.pop_2()
    cat.push(b - a)


@define('*')
def mul(cat):
    """
    mul : (nbr nbr -> nbr)

    desc:
        multiplies together the top two numbers on the stack. Result is placed
        on top of the stack. Note if the lower "number" is a string or a list
        it is replicated according to the standard Python rules.

    tags:
        level0,mathematics
    """
    a, b = cat.pop_2()
    cat.push(a * b)


@define('/')
def div(cat):
    """
    div : (nbr nbr -> nbr)

    desc:
        The number at [0] is divided into the number at [-1] and the
        quotient is pushed onto the stack.

    tags:
        level0,mathematics
    """
    a, b = cat.pop_2()
    cat.push(b / a)


@define('+rot')
def _rotUp(stack):
    '''
    +rot : (any:a any:b any:c -> any:c any:a any:b)

    desc:
        rotates the top three elements upward one position circularly

    tags:
        level0,stack
    '''
    if stack.length() < 3:
        raise Exception("+rot: Expect at least three elements on the stack")

    t, m, b = stack.pop_n(3)
    stack.push((t, b, m), multi=True)


@define('-rot')
def _rotDown(stack):
    '''
    -rot : (any:a any:b any:c -> any:b any:c any:a)

    desc:
        rotates the top three elements downward one position circularly

    tags:
        level0,stack
    '''
    if stack.length() < 3:
        raise Exception("-rot: Expect at least three elements on the stack")

    t, m, b = stack.pop_n(3)
    stack.push((m, t, b), multi=True)


@define('not')
def _not(stack):
    '''
    not : (bool -> bool)

    desc:
        returns True if the top value on the stack is False and vice versa

    tags:
        level0,boolean
    '''
    stack.stack[-1] = not stack.stack[-1]


@define('while')
def _while(stack):
    '''
    while : (func func:test -> any|none)

    desc:
        executes a block of code (function) repeatedly until the condition returns false
        Example: func test while

    tags:
        level1,control
    '''
    b, f = stack.pop_2()

    while (stack.eval(b), stack.pop())[1]:
        stack.eval(f)


@define('list')
def _list(cat):
    '''
    list : ([...] -> list)

    desc:
        creates a list from a function

    tags:
        level0,lists
    '''

    func = cat.pop()
    with cat.new_stack():
        cat.eval(func)
        lst = cat.to_list()
    cat.push(lst)


@define('#types')
def _type(stack):
    '''
    #types : (-> list)

    desc:
        prints a list of types represented by elements on the stack
        in the same order as the element on the stack with the deepest
        item first and the top item last

    tags:
        custom,types,stack
    '''
    typeList = []

    for item in stack.stack:
        typeList.append(type(item))

    stack.output(str(typeList), 'green')


@define('int')
def _int(cat):
    '''
    int : (obj -> int)

    desc:
        casts the object on top of the stack to an integer

    tags:
        level1,math,conversion
    '''
    cat.stack.push(int(cat.stack.pop()))


@define('float')
def _float(cat):
    '''
    float : (obj -> float)

    desc:
        casts the object on top of the stack to as floating point number

    tags:
        level1,math,conversion
    '''
    cat.stack.push(float(cat.stack.pop()))


@define('#pdb')
def _pdb(cat):
    '''
    #pdb : (-- -> --)

    desc:
        turns on the pdb flag in the REPL

    tags:
        custom,system,debugging
    '''
    cat.toggle_pdb()
    #toggle_pdb()


@define('and')
def _and(stack):
    '''
    and : (bool bool -> bool)

    desc:
        returns True if both of the top two values on the stack are True

    tags:
        level0,boolean
    '''
    a, b = stack.pop_2()
    stack.push(a and b)


@define('or')
def _or(stack):
    '''
    or : (bool bool -> bool)

    "desc:
        returns True if either of the top two values on the stack are True

    tags:
        level0,boolean
    '''
    a, b = stack.pop_2()
    stack.push(a or b)


@define('#import')
def _import(stack):
    '''
    #import : (string:module_name -> --)

    desc:
        imports the named module for use by the program
        Note: members of the module are accessed  with this notation: <module name>.<member name>
                parameters must precede the function call as a list with arguments in the order
                required by the function. E.g. ([base expt] list math.pow -> base^expt)
        Example: 'math #import
                    'os #import
                    'localModule #import

    tags:
        custom,module,import
    '''
    what = stack.pop()

    if isinstance(what, basestring):
        sys.modules[what] = __import__(what)

    else:
        raise Exception("#import The module name must be a string")


@define('#trace')
def _trace(cat):
    '''
    #trace: (-- -> --)

    desc:
        toggles the global tracing flag to enable simple tracing of function
        execution.

    tags:
        custom,debugging
    '''
    # This will fail. Needs fixing.
    cat.toggle_trace()


@define('>>')
def _rightShift(stack):
    '''
    >> : (int:base int:n -> int)

    descr:
        performs a right shift of n bits on a base integer

    tags:
        level0,math
    '''
    n, val = stack.pop_2()
    stack.push(int(val) >> n)


@define('<<')
def _leftShift(stack):
    """'
    << : (int:base int:n -> int)

    descr:
        performs a left shift of n bits on a base integer

    tags:
        level0,math
    """
    n, val = stack.pop_2()
    stack.push(int(val) << n)


@define('divmod')
@define('/%')
@define('%/')     # Are you sure you've got enough aliases there?
def _divmod(stack):
    '''
    divmod : (nbr nbr -> nbr nbr)
    /%     : (nbr nbr -> nbr nbr)

    desc:
        applies divmod function to top two members on stack. Number on top
        is the modulus. Returns quotient, remainder on stack (remainder on top).

    tags:
        level0,mathematics
    '''
    a, b = stack.pop_2()
    stack.push(divmod(b, a), multi=True)


@define('inc')
@define('++')
def inc(cat):
    '''
    inc : (nbr -> nbr)

    desc:
        increments the number on top ofthe stack by 1

    tags:
        level0,mathematics
    '''
    cat.stack.push(cat.stack.pop() + 1)


@define('dec')
@define('--')
def dec(cat):
    '''
    dec : (nbr -> nbr)

    desc:
        decrements the number on top ofthe stack by 1

    tags:
        level0,mathematics
    '''
    cat.stack.push(cat.stack.pop() - 1)


@define('mod')
@define('%')
def mod(cat):
    '''
    mod : (nbr nbr -> nbr)

    desc:
        applies modulus function to top two members on stack. Number at [0]
        is the modulus.

    tags:
        level0,mathematics
    '''
    a, b = cat.stack.pop_2()
    cat.stack.push(b % a)


@define('pwr')
@define('**')
def pwr(stack):
    '''
    pwr : (nbr:base nbr:expt -> nbr)

    desc:
        base**expt is pushed onto the stack

    tags:
        level0,math
    '''
    expt, base = stack.pop_2()

    if isinstance(base, basestring):
        base = eval(base)

    if not isinstance(base, (int, long, float)):
        raise ValueError("pwr: The base must be a number")

    if isinstance(expt, basestring):
        expt = eval(expt)

    if not isinstance(expt, (int, long, float)):
        raise ValueError("expt: The exponent must be a number")

    stack.push(base ** expt)


@define('round')
def round(stack):
    '''
    round : (float:nbr int:dp -> float:nbr)

    desc:
        rounds the floating point number at [-1] to the number of
        decimal places specified by the integer at [0]

    tags:
        level1,mathematics
    '''
    dp, nbr = stack.pop_2()

    if not isinstance(nbr, float):
        nbr = float(nbr)

    dp = int(dp)

    stack.push(round(nbr, dp))


@define('abs')
def _abs(stack):
    '''
    abs : (nbr -> nbr)

    desc:
        replaces the number on top of the stack with its absolute value

    tags:
        level1,mathematics
    '''
    nbr = stack.pop()

    if isinstance(nbr, basestring):
        nbr = eval(nbr)

    if isinstance(nbr, (int, long, float)):
        stack.push(abs(nbr))

    else:
        raise ValueError("abs: Argument is not a number")


@define('all')
def _all(stack):
    '''
    all : (list -> bool)

    desc:
        returns true on top of the  stack if all of the elements of the
        list on top of the stack are true

    tags:
        custom,mathematics
    '''
    stack.push(all(stack.pop_list()))


@define('any')
def _any(stack):
    '''
    any : (list -> bool)

    desc:
        Returns true on top of the stack if any element of the list
        on top of the stack is true

    tags:
        custom,lists
    '''
    stack.push(any(stack.pop_list()))


@define('chr')
def _chr(stack):
    '''
    chr : (int -> string)

    desc:
        converts the integer on top of the stack to a single character string

    tags:
        custom,string
    '''
    val = stack.pop()

    if isinstance(val, str) and val.isdigit():
        val = int(val)

    if isinstance(val, float):
        val = int(val)

    if isinstance(val, (int, long)):
        stack.push(chr(val))

    else:
        raise ValueError("chr: Cannot convert argument to an integer")


@define('enum')
def _enum(stack):
    '''
    enum : (list int:start -> list)

    desc:
        returns an enumerated list on top of the stack based on the
        starting int at [0] and the list at [-1] on the stack

    tags:
        custom,lists
    '''
    start, lst = stack.pop_2()

    if isinstance(start, (str, float)):
        start = int(start)

    if not isinstance(start, (int, long)):
        raise ValueError("enum: Starting value must be an integer")

    if isinstance(lst, str):
        lst = eval(lst)

    if not isinstance(lst, (list, tuple)):
        raise ValueError("enum: The list must be an iterable or convertable to one")

    stack.push([[x, y] for x, y in enumerate(lst, start)])


@define('hash')
def _hash(stack):
    '''
    hash : (any -> int)

    desc:
        pushes the hash value of the object on top of the stack onto the stack

    tags:
        custom,math
    '''
    stack.push(hash(stack.pop()))


@define('id')
def id(stack):
    '''
    id : (any -> any int:id)

    desc:
        calculates a unique integer id for the object on top of
        the stack and then pushes this id onto the stack. This id
        is unique as long as the session lasts. A new session will
        produce a different id.

    tags:
        custom,math
    '''
    stack.push(id(stack.peek()))


@define('ord')
def _ord(stack):
    '''
    ord : (string:chr -> int)

    desc:
        takes the single character string (or first character of a longer string)
        and pushes the integer code for that character onto the stack

    tags:
        custom,string,math
    '''
    obj = stack.pop()

    if isinstance(obj, (list, tuple)):
        obj = obj[0]

    if not isinstance(obj, str):
        obj = str(obj)

    stack.push(ord(obj[0]))


@define('sort')
def _sort(stack):
    '''
    sort : (list -> list)

    desc:
        sorts the list on top of the stack in place

    tags:
        custom,sort,list
    '''
    stack.push(sorted(stack.pop()))
