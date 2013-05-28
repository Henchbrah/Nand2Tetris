import re

string = r'(?:"[^"]*["])|(?:\'[^\']*[\'])'
comment = r'(?:(?:\/\*\*(?:.|\n)*?/*\/)|(?:\/\/[^\n]*\n))'
symbols = r'()[]{},;=.+-*/&|~<>'
delimiters = r'[\(\)\[\]\{\}\,\;\=\.\+\-\*\/\&\|\~\<\>]|'+string+'| *'
keywords = ('class','constructor','method','function','int','boolean','char','void',
            'var','static','field','let','do','if','else','while','return','true','false','null','this')

def isnum(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

class JackTokenizer(object):
    """Accepts input file of type xxx.jack and provides methods for tokenizing it"""
    def __init__(self,f):
        self.input = open(f,"r").read()
        self.cleanUp()
        self.tokens = [token for token in re.split(r'('+ delimiters + r')',self.input) if token not in ('', ' ')]
        self.currentToken = None 

    def cleanUp(self):
        """Removed comments and normalizes whitespace"""
        self.input = " ".join(re.sub(comment,"",self.input).split())

    def advance(self):
        self.currentToken = self.tokens.pop(0)    

    def hasMoreTokens(self):
        """Returns True if there are more tokens, else returns False"""
        return True if len(self.tokens) > 0 else False

    def tokenType(self,tok=None):
        """Returns the type of the current token"""
        if tok == None:
            tok = self.currentToken
        if tok in keywords:
            return 'KEYWORD'
        elif tok in symbols:
            return 'SYMBOL'
        elif isnum(tok):
            return 'INT_CONST'
        elif re.match(string,tok):
            return 'STRING_CONST'
        else:
            return 'IDENTIFIER'

    def keyWord(self):
        """Returns the keyword which is the current token. Should be called only when tokenType() is KEYWORD"""
        return self.currentToken
            
    def symbol(self):
        """Returns the Symbol which is the current token. Should be called only
        when tokenType() is SYMBOL"""        
        return self.currentToken
        
    def identifier(self):
        """Returns the identifier which is the current token. Should be called only
           when tokenType() is IDENTIFIER""" 
        return self.currentToken

    def intVal(self):
        """Returns the interger value of the current token. Should be called only
           when tokenType() is INT_CONST""" 
        return int(self.currentToken)

    def stringVal(self):
        """Returns the string value of the current token. Should be called only
           when tokenType() is STRING_CONST""" 
        return self.currentToken[1:-1]

