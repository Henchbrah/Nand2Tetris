
ops = {'=':'eq','+':'add','-':'sub','&':'and','|':'or','~':'not','<':'lt','>':'gt'}

class CompilationEngine(object):
    """Gets input from the JackTokenizer and emits its parsed structure into an output file"""
    def __init__(self,tokenizer,table,writer):
        """Creates a new compilation engine with the given input and output, 
	    next routine called must be compileClass()"""
    	self.tokenizer = tokenizer
    	if not self.tokenizer.hasMoreTokens: 
		    raise Exception('No Tokens to parse!')
        self.table = table
        self.writer = writer
        self.ifNum = 0
        self.whileNum = 0

    def compileClass(self):
        """Compiles complete class"""            
        self.validate('class')
        name = self.validate('IDENTIFIER')
        self.table.define(name,name,'class')	
        self.validate('{')          
        while self.lookAhead()[1] in ('static','field'): 
            self.compileClassVarDec()   
        while self.lookAhead()[1] in ('constructor','function','method'):
            self.compileSubroutine(name)
        self.validate('}')                                       
        self.writer.close()

    def compileClassVarDec(self):
        """Compiles a static declaration or a field declaration""" 
        kind = self.validate(['field','static'])          
        type = self.validate(['KEYWORD','IDENTIFIER'])
        name = self.validate('IDENTIFIER')
        self.table.define(name,type,kind)
        while self.lookAhead()[1] <> ';':
            self.validate(',')
            name = self.validate('IDENTIFIER')
            self.table.define(name,type,kind)  				      
        self.validate(';')     

    def compileParameterList(self,routine):
        """Compiles a (possibly empty) parameter list, not including the enclosing "()" """
        atLeastOne = False
        kind = 'argument'
        if routine == 'method':
            self.table.define('this',None,kind)
        while self.lookAhead()[1] <> ')':
            if atLeastOne: 
                self.validate(',')
            else: 
                atLeastOne = True
            type = self.validate(['KEYWORD','IDENTIFIER'])
            name = self.validate('IDENTIFIER') 
            self.table.define(name,type,kind)

    def compileSubroutine(self,className):
        """Compiles a complete method, function or constructor"""
        self.resetLabels()
        kind = self.validate(['constructor','function','method'])
        self.validate(['KEYWORD','IDENTIFIER'])
        name = self.validate('IDENTIFIER')
        self.table.define(name,None,kind)
        self.table.startSubroutine()
        self.validate('(')
        self.compileParameterList(kind)
        self.validate(')')        
        self.validate('{')
        while self.lookAhead()[1] == 'var':
            self.compileVarDec()
        self.writer.writeFunction(className+'.'+name,self.table.varCount('local')) # function nameoffunction #oflocals
        if kind == 'constructor':              # if 
            count = self.table.varCount('this','outer')
            self.writer.writePush('constant',count)
            self.writer.writeCall('Memory.alloc',1) ##allocate memory for object
            self.writer.writePop('pointer',0) ### assign pointer to object to pointer 0
        if kind == 'method':
            self.writer.writePush('argument',0) # if it's a method the first argument is
            self.writer.writePop('pointer',0)   # a pointer to 'this'
        self.compileStatements()
        self.validate('}')
        self.table.endSubroutine()       

    def compileVarDec(self):
        self.validate('var')                          
        type = self.validate(['KEYWORD','IDENTIFIER'])
        name = self.validate('IDENTIFIER')
        self.table.define(name,type,'local')
        while self.lookAhead()[1] <> ';':
            self.validate(',')
            name = self.validate('IDENTIFIER')
            self.table.define(name,type,'local')        
        self.validate(';')        
        
    def compileStatements(self):
        """Compiles a sequence of statements, not including the enclosing "{}" """
        tok = self.lookAhead()[1]
        while tok <> '}':
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
            else:
                raise Exception('%s should not begin a statement' %tok)
            tok = self.lookAhead()[1]              

    def compileDo(self):
        """Compiles a do statement"""
        self.validate('do')
        self.compileTerm() 
        self.writer.writePop('temp',0)
        self.validate(';')

    def compileLet(self):
        """Compiles a let statement"""      # let x = y     
        self.validate('let')
        tokType,tok = self.getNextToken()
        kind,index = self.table.getKind(tok),self.table.getIndex(tok)
        if self.lookAhead()[1] == '[':      
            self.validate('[')
            self.compileExpression()
            self.validate(']')
            self.writer.writePush(kind,index)
            self.writer.writeArithmetic('add')
            self.validate('=')
            self.compileExpression() # now top of stack is y and just under it is x ....and if it's not a a[0]
            self.writer.writePop('temp',0)
            self.writer.writePop('pointer',1)
            self.writer.writePush('temp',0)
            self.writer.writePop('that',0)
        else:
            self.validate('=')
            self.compileExpression()
            self.writer.writePop(kind,index)
        self.validate(';')
    
    def compileWhile(self):
        """Compiles a while statement"""        
        self.validate('while')
        label1 = 'WHILE_EXP%d' %self.whileNum
        label2 = 'WHILE_END%d' %self.whileNum
        self.whileNum += 1
        self.writer.writeLabel(label1)              #label1
        self.validate('(')
        self.compileExpression()
        self.validate(')')
        self.writer.writeArithmetic('not')          #compute ~(condition)
        self.writer.writeIf(label2)                 #if-goto label2
        self.validate('{')
        self.compileStatements()
        self.validate('}')            
        self.writer.writeGoto(label1)               #goto label1
        self.writer.writeLabel(label2)              #label2

    def compileReturn(self):
        """Compiles a return statement"""   
        self.validate('return')
        if self.lookAhead()[1] <> ';':
            self.compileExpression()                #this should leave value on top of stack
        else:
            self.writer.writePush('constant',0)     # if is void return 0
        self.validate(';')
        self.writer.writeReturn()     

    def compileIf(self):
        """Compiles an if statement, possibly with a trailing else clause"""
        self.validate('if')
        label1 = 'IF_TRUE%d' %self.ifNum
        label2 = 'IF_FALSE%d' %self.ifNum
        label3 = 'IF_END%d' %self.ifNum
        self.ifNum += 1
        self.validate('(')
        self.compileExpression()
        self.validate(')')
        #self.writer.writeArithmetic('not')   #calculate ~(condition)
        self.writer.writeIf(label1)          #if-goto IF_TRUE
        self.writer.writeGoto(label2)       # GOTO IF_FALSE
        self.writer.writeLabel(label1)      #IF_TRUE
        self.validate('{')
        self.compileStatements()
        self.validate('}')
        if self.lookAhead()[1] == 'else':
            self.writer.writeGoto(label3)       #GOTO IF_END
        self.writer.writeLabel(label2)      #IF_FALSE
        if self.lookAhead()[1] == 'else':
            self.validate('else')
            self.validate('{')
            self.compileStatements()
            self.validate('}')       
            self.writer.writeLabel(label3)      #IF_END

    def compileExpression(self):
        """Compiles an expression"""
        self.compileTerm() 
        while self.lookAhead()[1] in '+-*/&|<>=':
            tok = self.getNextToken()[1]
            self.compileTerm()
            if tok == '/':
                self.writer.writeCall('Math.divide',2)
            elif tok == '*':
                self.writer.writeCall('Math.multiply',2)
            else:
                self.writer.writeArithmetic(ops[tok])

    def compileExpressionList(self):
        """Compiles a (possibly empty) comma-separated list of expressions"""       
        atLeastOne = False
        count = 0
        while self.lookAhead()[1] <> ')':
            if atLeastOne:
                self.validate(',')
            else:
                atLeastOne = True
            self.compileExpression()
            count += 1
        return count

    def compileTerm(self):
        """Compiles a term. If the current token is an identifier, a single look-ahead token which
        may be one of "[","(" or "." suffices to distinguish between the three possibilities. Any
        other token is not part of this term and should not be advanced over"""                    
        tokType,tok = self.getNextToken()
        if tokType == 'INT_CONST':
            self.writer.writePush('constant',tok)       
        elif tokType == 'STRING_CONST':
            self.writer.writePush('constant',len(tok))
            self.writer.writeCall('String.new',1)               # create empty string of length len(tok)
            for letter in tok:
                self.writer.writePush('constant',ord(letter))
                self.writer.writeCall('String.appendChar', 2)   # append each letter to string            
        elif tokType == 'KEYWORD':
            if tok in ['false','null']:
                self.writer.writePush('constant',0)
            elif tok == 'true':
                self.writer.writePush('constant',0)
                self.writer.writeArithmetic('not')
            elif tok == 'this':
                self.writer.writePush('pointer',0)
            else:
                raise Exception('%s is not an acceptable term' %tok)
        elif tokType == 'SYMBOL':
            if tok == '(':
                self.compileExpression()
                self.validate(')')
            elif tok in ['-','~']:
                count = self.compileTerm() # push next term first, then do operation
                if tok == '-':
                    op = 'neg'
                else:
                    op = 'not'
                self.writer.writeArithmetic(op)
            else:
                raise Exception('%s %s is unexpected symbol' %(tokType,tok))
        elif tokType == 'IDENTIFIER':
            count = 0
            name = tok
            kind,index = self.table.getKind(name),self.table.getIndex(name)
            tokType,tok = self.lookAhead()
            if tok == '(':
                self.writer.writePush('pointer',0) # if is of form do something() it is method call within this class
                self.validate('(')
                count = self.compileExpressionList() + 1
                self.validate(')')
                currentClass = self.table.getClass()
                self.writer.writeCall(currentClass+'.'+name,count)
            elif tok == '.':    
                self.validate('.')
                function = self.validate('IDENTIFIER')
                print name, kind
                if kind in ('this','local','static'):
                    self.writer.writePush(kind,index)
                    count = 1
                self.validate('(')
                count += self.compileExpressionList()
                self.validate(')')                
                type = self.table.getType(name)
                if type == None: type = name 
                self.writer.writeCall('%s.%s' %(type,function),count)    
            elif tok == '[':
                self.validate('[')
                self.compileExpression()
                self.validate(']')
                self.writer.writePush(kind,index)
                self.writer.writeArithmetic('add')  
                self.writer.writePop('pointer',1)
                self.writer.writePush('that',0)
            else:
                self.writer.writePush(kind,index)
        else:
            raise Exception('Illegal Token: %s %s' %(tokType,tok))


    def lookAhead(self):
        """looks ahead to next (token_type, token)"""
        tok = self.tokenizer.tokens[0]
        tokType = self.tokenizer.tokenType(tok)
        return tokType,tok

    def validate(self,string):
        """Accepts as string or list of strings. Advances to next token. If token type or token itself does not
        match string argument (or each item in list 'string') raises an exception. Returns token type and token itself"""
        
        tokType,tok = self.getNextToken()
        if type(string) <> list:
            string = [string]
        if not any([(tokType == s or tok == s) for s in string]):
            raise Exception('Illegal token: %s %s , Expected: %s' %(tokType,tok,string[0]))
	return tok 

    def getNextToken(self):
        if self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()
            tokType = self.tokenizer.tokenType()
            if tokType == 'IDENTIFIER':
                return ( tokType, self.tokenizer.identifier() )
            elif tokType == 'STRING_CONST':
                return ( tokType, self.tokenizer.stringVal() )
            elif tokType == 'INT_CONST':
                return ( tokType,self.tokenizer.intVal() )
            elif tokType == 'SYMBOL':
                return ( tokType, self.tokenizer.symbol() )
            elif tokType == 'KEYWORD':
                return (tokType, self.tokenizer.keyWord() )            
            else:
                raise Exception('Invalid token type: %s' %tokType)
        else:
            return (None,None)   
 
    def resetLabels(self):
        self.ifNum,self.whileNum = 0,0

