
specialSymbols = {'<':'&lt','>':'&gt','"':'&quot','&':'&amp'}

class CompilationEngine(object):
    """Gets input from the JackTokenizer and emits its parsed structure into an output file"""

    def __init__(self,name,tokenizer):
        """Creates a new compilation engine with the given input and output, next routine called
        must be compileClass()"""
        self.outname = name + '.xml'
        self.outfile = open(self.outname, 'w')
        self.tokenizer = tokenizer
        if not self.tokenizer.hasMoreTokens: raise Exception('No Tokens to parse!')
        self.indent = 1
        self.outfile.write('<tokens>\n')

    def compileClass(self):
        """Compiles complete class"""   
        self.write('<class>')           
        self.incrIndent()                     
        self.writeNextToken('class')    
        self.writeNextToken('IDENTIFIER')
        self.writeNextToken('{')          
        while self.lookAhead()[1] in ('static','field'): 
            self.compileClassVarDec()   
        while self.lookAhead()[1] in ('constructor','function','method'):
            self.compileSubroutine()
        self.writeNextToken('}')           
        self.decrIndent()                  
        self.write('</class>')             
        self.closeFile()     

    def compileClassVarDec(self):
        """Compiles a static declaration or a field declaration""" 
        self.write('<classVarDec>')
        self.incrIndent()       
        self.writeNextToken(['field','static'])                   
        self.writeNextToken(['KEYWORD','IDENTIFIER'])
        self.writeNextToken('IDENTIFIER')
        while self.lookAhead()[1] <> ';':
            self.writeNextToken(',')
            self.writeNextToken('IDENTIFIER')        
        self.writeNextToken(';')     
        self.decrIndent()
        self.write('</classVarDec>')

    def compileParameterList(self):
        """Compiles a (possibly empty) parameter list, not including the enclosing "()" """
        self.write('<parameterlist>')
        self.incrIndent()
        atLeastOne = False
        while self.lookAhead()[1] <> ')':
            if atLeastOne: 
                self.writeNextToken(',')
            else: 
                atLeastOne = True
            self.writeNextToken(['KEYWORD','IDENDIFIER'])
            self.writeNextToken('IDENTIFIER')    
        self.decrIndent()
        self.write('</parameterlist>')

    def compileSubroutine(self):
        """Compiles a complete method, function or constructor"""
        self.write('<subroutine>')
        self.incrIndent()
        self.writeNextToken(['constructor','function','method'])
        self.writeNextToken(['KEYWORD','IDENTIFIER'])
        self.writeNextToken('IDENTIFIER')
        self.writeNextToken('(')
        self.compileParameterList()
        self.writeNextToken(')')
        self.write('<subroutineBody>')
        self.incrIndent()
        self.writeNextToken('{')
        while self.lookAhead()[1] == 'var':
            self.compileVarDec()
        self.compileStatements()
        self.writeNextToken('}')
        self.decrIndent()
        self.write('</subroutineBody>')
        self.decrIndent()
        self.write('</subroutine>')        
    
    def compileVarDec(self):
        self.write('<varDec>')
        self.incrIndent()   
        self.writeNextToken('var')                          
        self.writeNextToken(['KEYWORD','IDENTIFIER'])
        self.writeNextToken('IDENTIFIER')
        while self.lookAhead()[1] <> ';':
            self.writeNextToken(',')
            self.writeNextToken('IDENTIFIER')        
        self.writeNextToken(';')        
        self.decrIndent()
        self.write('</varDec>')
       
    def compileStatements(self):
        """Compiles a sequence of statements, not including the enclosing "{}" """
        self.write('<statements>')
        self.incrIndent()
        tok = self.lookAhead()[1]
        while tok <> '}':
            self.validate(['do','let','while','return','if'])
            if tok == 'do':
                self.compileDo()
            elif tok == 'let':  
                self.compileLet()
            elif tok == 'while':
                self.compileWhile()
            elif tok == 'return':
                self.compileReturn()
            elif tok == 'if':
                self.compileIf()
            tok = self.lookAhead()[1]              
        self.decrIndent()
        self.write('</statements>')        

    def compileDo(self):
        """Compiles a do statement"""
        self.write('<do>')
        self.incrIndent()
        self.writeNextToken('do')
        self.writeNextToken('IDENTIFIER')
        if self.lookAhead()[1] == '.':
            self.writeNextToken()
            self.writeNextToken('IDENTIFIER')
        self.writeNextToken('(')
        self.compileExpressionList()
        self.writeNextToken(')')
        self.writeNextToken(';')
        self.decrIndent()
        self.write('</do>')

    def compileLet(self):
        """Compiles a let statement"""
        self.write('<let>')
        self.incrIndent()            
        self.writeNextToken('let')
        self.writeNextToken('IDENTIFIER')
        if self.lookAhead()[1] == '[':
            self.writeNextToken()
            self.compileExpression()
            self.writeNextToken(']')
        self.writeNextToken('=')
        self.compileExpression()
        self.writeNextToken(';')
        self.decrIndent()
        self.write('</let>')
    
    def compileWhile(self):
        """Compiles a while statement"""
        self.write('<while>')
        self.incrIndent()
        self.writeNextToken('while')
        self.writeNextToken('(')
        self.compileExpression()
        self.writeNextToken(')')
        self.writeNextToken('{')
        self.compileStatements()
        self.writeNextToken('}')            
        self.decrIndent()
        self.write('</while>')

    def compileReturn(self):
        """Compiles a return statement"""
        self.write('<return>')
        self.incrIndent()
        self.writeNextToken('return')
        if self.lookAhead()[1] <> ';':
            self.compileExpression()
        self.writeNextToken(';')
        self.decrIndent()
        self.write('</return>')        

    def compileIf(self):
        """Compiles an if statement, possibly with a trailing else clause"""
        self.write('<if>')
        self.incrIndent()
        self.writeNextToken('if')
        self.writeNextToken('(')
        self.compileExpression()
        self.writeNextToken(')')
        self.writeNextToken('{')
        self.compileStatements()
        self.writeNextToken('}')
        if self.lookAhead()[1] == 'else':
            self.writeNextToken()
            self.writeNextToken('{')
            self.compileStatements()
            self.writeNextToken('}')        
        self.decrIndent()
        self.write('</if>')

    def compileExpression(self):
        """Compiles an expression"""
        self.write('<expression>')
        self.incrIndent()
        self.compileTerm()
        while self.lookAhead()[1] in '=+-*/&|~<>':
            self.writeNextToken()
            self.compileTerm()
        self.decrIndent()
        self.write('</expression>')

    def compileExpressionList(self):
        """Compiles a (possibly empty) comma-separated list of expressions"""
        self.write('<expressionlist>')
        self.incrIndent()        
        atLeastOne = False
        while self.lookAhead()[1] <> ')':
            if atLeastOne:
                self.writeNextToken(',')
            else:
                atLeastOne = True
            self.compileExpression()
        self.decrIndent()
        self.write('</expressionlist>')

    def compileTerm(self):
        """Compiles a term. If the current token is an identifier, a single look-ahead token which
        may be one of "[","(" or "." suffices to distinguish between the three possibilities. Any
        other token is not part of this term and should not be advanced over"""                    
        self.write('<term>')
        self.incrIndent()
        tokType,tok = self.lookAhead()       
        if tokType in ['STRING_CONST','INT_CONST','KEYWORD']:
            self.writeNextToken()
        elif tokType == 'SYMBOL':
            if tok == '(':
                self.writeNextToken()
                self.compileExpression()
                self.writeNextToken(')')
            else:
                self.writeNextToken(['-','~'])
                self.compileTerm()
        elif tokType == 'IDENTIFIER':
            self.writeNextToken()
            tok = self.lookAhead()[1]
            if tok == '[':
                self.writeNextToken()
                self.compileExpression()
                self.writeNextToken(']')
            elif tok == '(':
                self.writeNextToken()
                self.compileExpressionList()
                self.writeNextToken(')') 
            elif tok == '.':       
                self.writeNextToken()
                self.writeNextToken('IDENTIFIER')
                self.writeNextToken('(')
                self.compileExpressionList()
                self.writeNextToken(')') 
        else:
            raise Exception('Illegal Token: %s %s' %(tokType,tok))
        self.decrIndent()
        self.write('</term>')

    def lookAhead(self):
        """looks ahead to next (token_type, token)"""
        tok = self.tokenizer.tokens[0]
        tokType = self.tokenizer.tokenType(tok)
        return tokType,tok

    def validate(self,string):
        """Accepts as string or list of strings. Looks ahead to next token and if token type or token itself does not
        match string argument (or each item in list 'string') raises an exception"""
        tokType,tok = self.lookAhead()
        if type(string) <> list:
            string = [string]
        if not any([(tokType == s or tok == s) for s in string]):
            raise Exception('Illegal token: %s %s , Expected: %s' %(tokType,tok,string[0])) 

    def writeNextToken(self,expected=None):
        if expected <> None:
            self.validate(expected)
        tokType,tok = self.getNextToken() 
        self.writeToken(tokType,tok)
        
    def writeToken(self,tokType,tok):
        """Writes simple one-line token"""
        if str(tok) in '<>"&':
            tok = specialSymbols[tok]
        self.write('<%s> %s </%s>' %(tokType,tok,tokType))
    
    def write(self,string):
        """Writes to outfile with current indent level, equivalent of"""
        self.outfile.write('  ' * self.indent + string + '\n')
      
    def incrIndent(self):
        self.indent += 1

    def decrIndent(self):
        self.indent -= 1
    
    def getNextToken(self):
        if self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()
            tokType = self.tokenizer.tokenType()
            if tokType == 'IDENTIFIER':
                return ( 'identifier',self.tokenizer.identifier() )
            elif tokType == 'STRING_CONST':
                return ( 'stringConstant', self.tokenizer.stringVal() )
            elif tokType == 'INT_CONST':
                return ( 'integerConstant',self.tokenizer.intVal() )
            elif tokType == 'SYMBOL':
                return ( 'symbol', self.tokenizer.symbol() )
            elif tokType == 'KEYWORD':
                return ('keyword', self.tokenizer.keyWord() )            
            else:
                raise Exception('Invalid token type: %s' %tokType)
        else:
            return (None,None)   

    def closeFile(self):
        self.outfile.write('</tokens>\n')
        self.outfile.close()


if __name__ == '__main__':
    import JackTokenizer as jack
    j = jack.JackTokenizer('Main.jack')
    c = CompilationEngine('test',j)
    c.compileClass()    

