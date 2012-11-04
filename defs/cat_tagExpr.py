# parse a logical expression that uses tags/Sets as data

from sets import Set

class TagExpr( object ) :
    '''Parses a logical expression using tags
    <expr> ::= <term> <term_tail>
    <term_tail> ::= 'or' <term> <term_tail> | {}
    <term> ::= <factor> <factor_tail>
    <factor_tail> ::= 'and' <factor> <factor_tail> | {}
    <factor> ::= '(' <expr> ')' | 'not' <factor> | <id>
    <id> ::= a key in the tags dictionary
    Note: 'and', 'or', 'not' are reserved words
    The tags dictionary: <tag name> : Set(<words having the tag name>)
    '''
    def __init__(self, mapTags ) :
        self._mapTags = mapTags
    
    def parse( self, text ) :
        self._tokens = text.replace("(", " ( ").replace(")", " ) ").split()
        self._tokens.reverse()
        self._inputToken     = self._tokens.pop()
        self._operands       = [ ]
        self._lastInputToken = ''
        
        if self._expr() :
            return self._operands.pop()
        
        else :
            return None
    
    def _isIdent( self, what ) :
        '''The pseudotoken '<id>' indicates that the inputToken should
        be an identifier. This method is a very simple test for that condition.
        Note: all identifiers must be keys in the _mapTags dictionary.
        '''
        if what == '<id>' :
            if self._inputToken in self._mapTags :
                return True
            
            else :
                return False
        
        else :
            return False
            
    def _match( self, what ) :
        '''Sees if the current inputToken matches the argument. If it does match
        the next input token is acquired and True is returned. If the tokens
        list is empty, the special pseudotoken '<END>' is returned. The pseudotoken '<id>'
        signals that an identifier is required. This requirement is tested by the _isIdent
        method. No match with the argument simply returns False
        '''
        if (self._inputToken == what) or self._isIdent( what ) :
            if len(self._tokens) :
                self._lastInputToken = self._inputToken
                self._inputToken     = self._tokens.pop()
            
            else :
                self._lastInputToken = self._inputToken
                self._inputToken     = '<END>'
            
            return True
        
        else :
            return False
    
    def _expr( self ) :
        '''<expr> ::= <term> <term_tail>'''
        self._term()
        self._term_tail()
        return self._match( '<END>' )
    
    def _term_tail( self ) :
        '''<term_tail> ::= 'or' <term> <term_tail> | {}'''
        if self._match( 'or' ) :
            self._term()
            self._orOp()
            self._term_tail()
    
    def _term( self ) :
        '''<term> ::= <factor> <factor_tail>'''
        self._factor()
        self._factor_tail()
    
    def _factor_tail( self ) :
        '''<factor_tail> ::= 'and' <factor> <factor_tail> | {}'''
        if self._match( 'and' ) :
            self._factor()
            self._andOp()
            self._factor_tail()
    
    def _factor( self ) :
        '''<factor> ::= '(' <expr> ')' | 'not' <factor> | tag_name'''
        if self._match("(") :
            self._expr()
            self._match(")")
        
        elif self._match( 'not' ) :
            self._factor()
            arg = self._operands.pop()
            self._operands.append( self._mapTags['universe'].difference(arg) )
        
        else :
            self._match( '<id>' )
            self._operands.append( self._mapTags[self._lastInputToken] )
    
    def _andOp( self ) :
        '''Perform set intersection'''
        rhs = self._operands.pop()
        lhs = self._operands.pop()
        self._operands.append( lhs.intersection(rhs) )
    
    def _orOp( self ) :
        '''Perform set union'''
        rhs = self._operands.pop()
        lhs = self._operands.pop()
        self._operands.append( lhs.union(rhs) )
