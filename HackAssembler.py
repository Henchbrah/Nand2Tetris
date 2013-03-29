"""Version of an assembler for the Hack Platform utilizing PLY. Takes an assembly
   language file with extension .asm and converts it to machine code. Machine code is then
   written into a file with .hack extension"""


import asmtokens
import ply.lex as lex
import ply.yacc as yacc
from asmtokens import *
from asmmappings import * # includes DEST,COMP,JUMP,Symbol and binary(), pad() functions
from sys import argv


start = 'asm'

def p_asm(p):
    'asm : element asm'
    p[0] = [p[1]] + p[2]

def p_asm_empty(p):
    'asm : '
    p[0] = [ ]

def p_element(p):
    '''element : load
               | exp
               | jmp
               | label'''
    p[0] = p[1]

def p_load(p):
    'load : AT value'
    p[0] = ('load', p[2])

def p_value(p):
    'value : WORD'
    p[0] = ('word',p[1])

def p_value_num(p):
    'value : NUMBER'
    p[0] = ('number',p[1])

def p_exp(p):
    'exp : WORD EQUAL compute'
    p[0] = ('exp',p[1],p[3])

def p_compute_binop(p):
    '''compute : value PLUS value
               | value MINUS value
               | value AND value
               | value OR value'''
    p[0] = ('binop',p[1],p[2],p[3])

def p_compute_two(p):
    '''compute : NOT value
               | OR value
               | MINUS value'''
    p[0] = ('op',p[1],p[2])

def p_compute_single(p):
    'compute : value'
    p[0] = p[1] 

def p_jmp(p):
    'jmp : value SEMICOLON WORD'
    p[0] = ('jump', p[1][1], p[3])

def p_label(p):
    'label : LPAREN WORD RPAREN'
    p[0] = ('label',p[2])

def p_error(p):
    print p
    print 'Syntax error in input'

def eval_C(dest,compute):
    "Handles compute commands"
    if compute[0] == 'binop':
        operand1 = compute[1][1]
        operand2 = compute[3][1]
        operator = compute[2]
        comp = operand1 + operator + operand2
    elif compute[0] == 'op':
        operator = compute[1]
        operand = compute[2][1]
        comp = operator + operand
    else:
        comp = compute[1]
    return '111' + COMP[comp] + DEST[dest] + '000'

def eval_J(comp,jump):
    "Handles jump commands"
    return '111'+ COMP[comp] + '000' + JUMP[jump]

def eval_A(code):
    "Handles load commands"
    typeof,val = code[0],code[1]
    if typeof == 'word':
        if val in Symbol:     # if we've already assigned a memory address to symbol, use that                      
            val = Symbol[val]      
        else:
            Symbol[val] = eval_A.address #if first we've seen of symbol
            val = Symbol[val]                       
            eval_A.address += 1 # increment symbol_address 
    return '0' + pad(binary(val),15)

eval_A.address = 16 # initialize address for symbols to 0x0010

def interpret_asm(tree):
    """walks abstract syntax tree evaluating it and converting to binary
        representation appropriate for hack platform"""
    res = [ ]
    lineno = 0
    for leaf in tree:
        if leaf[0] == 'label':
            Symbol[ leaf[1] ] = lineno 
        else:
            lineno += 1
    for leaf in tree:
        if leaf[0] == 'exp':
            res.append(eval_C(leaf[1],leaf[2]))
        elif leaf[0] == 'jump':
            res.append(eval_J(leaf[1],leaf[2]))
        elif leaf[0] == 'load':
            res.append(eval_A(leaf[1]))
        else: pass
    return '\n'.join(res)


f_in = argv[1]
f_out = f_in[:-4]+'.hack'
string = open(f_in,"r").read()
asmlexer = lex.lex(module=asmtokens)
asmlexer.input(string)
#while 1:
 #   tok = asmlexer.token()
  #  if not tok: break
   # print tok
asmparser = yacc.yacc()

ast = asmparser.parse(string,lexer=asmlexer)
#print ast
machine_code = interpret_asm(ast)
open(f_out,'w').write(machine_code)




                         
            





            
