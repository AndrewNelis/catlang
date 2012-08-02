
from cat.namespace import define


@define('+')
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
    return cat.push(a + b)


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
