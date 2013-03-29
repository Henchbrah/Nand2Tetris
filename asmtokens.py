
tokens = (
    'EQUAL', # =
    'LPAREN', # (
    'MINUS', # -
    'NOT', # !
    'NUMBER',
    'OR', # |
    'PLUS', # +
    'RPAREN', # )
    'SEMICOLON', # ;
    'WORD', # something 
    'AT', #@
    'AND', #&
)



t_ignore = ' \t\r'    

def t_eolcomment(t):
    r'//[^\n]*'
    pass



t_WORD = r'[a-zA-z\$\.\_\:]+[0-9a-zA-z\$\.\_\:]*'  #any sequence of letters,digits, _, . , $ and :, that doesn't begin with a digit
t_EQUAL = r'\='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_MINUS = r'\-'
t_OR = r'\|'
t_NOT = r'\!'
t_NUMBER = r'[0-9]+'
t_PLUS = r'\+'
t_AT = r'\@'
t_AND = r'\&'
t_SEMICOLON = r'\;' #


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print 'Illegal character "%s"' % t.value[0]
    t.lexer.skip(1)

