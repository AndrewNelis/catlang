# user Python extensions go here

from cat.namespace import *
import sys
ns = NameSpace()

# Template:
# 
# define(ns, 'YOUR NEW WORD NAME')
# def <some name>( cat ) :
# 	'''
# 	<name> : (?? -> ??)
# 	
# 	desc:
# 		<description>
# 	tags:
# 		<classification tags comma-separated list>
# 	'''
# 	<YOUR PROGRAM HERE>
# 

# An example:
@define(ns, 'arith')
def arith( cat ) :
    '''
    arith : (string:expression -> nbr:value)
    
    desc:
    	Evaluates the expression returning the value on the stack. User-defined variables,
    	calls to functions in modules, and access to stack variables ($0 -- value on
    	stack at [0], $1 -- value at [-1], etc.). Stack values used in the expression are
    	removed from the stack. For example:
    	
    	Cat> math.pi "3 * math.sin($0) + 83" arith
        
    	expression: the arithmetic expression to be evaluated
    	value: the number returned
    tags:
    	mathematics,arithmetic
    '''
    def isNumber( nbr ) :
        try :
            float( nbr )
            return True
        
        except ValueError :
            return False
    
    expr      = cat.stack.pop()
    ops       = "+-*/()%"
    stackVals = { }
    txt       = expr
    
    # split the text into tokens
    for op in ops:
        repl = " %s " % op
        txt  = txt.replace( op, repl )
    
    tokens    = txt.split()
    localVars = { }
    
    # analyze the tokens one-by-one
    for token in tokens :
        if token in "+-*/()%" or isNumber(token):
            continue
        
        # check for references to functions in modules (e.g. math.PI)
        if token.count(".") >= 1 :
            continue
        
        # check for references to values on the stack ($0 => stack[-1], $1 => stack[-2], etc)
        if token.startswith( "$" ) :
            offset           = -(int( token[1:] ) + 1)
            stackVals[token] = cat.stack[offset]
            continue
        
        # should be a user variable at this point
        ok, val = cat.ns.getVar( token )
        
        if not ok:
            raise ValueError, "Undefined variable '%s'" % token
        
        # replace ":" in a variable name with "_" and save the value
        localVars[token.replace(":", "_")] = val
    
    # replace all ":" with "_"
    expr = expr.replace( ":", "_" )
    
    # check for stack values ($<n>)
    if len(stackVals) :
        cat.stack.reverse() # this for deleting stack variables $0, $1, ...
        
        for key in stackVals :
            val  = stackVals[key]
            expr = expr.replace( key, str(val) )
            cat.stack.remove( val )
        
        cat.stack.reverse() # restore stack to canonical order
            
    # try evaluating the expression
    gbls = globals()
    gbls.update( sys.modules )
    val  = eval( expr, gbls, localVars )
    cat.stack.push( val )


# this goes last
def _returnNS() :
	return ns
