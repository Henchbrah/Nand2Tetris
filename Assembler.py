import sys
from Asm import Asm

def binary(n):
    """Takes a decimal number as a string and returns
       binary representation also as a string"""
    num = int(n)
    if num == 0:
        return '0'
    res = ''
    while num != 0:
        if num%2==0:
            res = '0' + res
            num=num/2
        elif num%2<>0:
            num = (num -1)/2
            res = '1' + res
    return res

def pad(n,length=3):
    while len(n) < length: n='0'+n
    return n
    
three_bin_digits = map(pad,map(binary,range(8)))
j_mnemonics = ['null','JGT','JEQ','JGE','JLT','JNE','JLE','JMP']
d_mnemonics = ['null','M','D','MD','A','AM','AD','AMD']
jump =  dict(zip(j_mnemonics,three_bin_digits))
dest = dict(zip(d_mnemonics,three_bin_digits))
comp = {'0':  '0101010','1':  '0111111','-1': '0111010','D':  '0001100',
        'A':  '0110000','M':  '1110000','!D': '0001101','!A': '0110001',
        '!M': '1110001','-D': '0001111','-A': '0110011','-M': '1110011',
        'D+1':'0011111','A+1':'0110111','M+1':'1110111','D-1':'0001110',
        'A-1':'0110010','M-1':'1110010','D+A':'0000010','D+M':'1000010',
        'D-A':'0010011','D-M':'1010011','A-D':'0000111','M-D':'1000111',
        'D&A':'0000000','D&M':'1000000','D|A':'0010101','D|M':'1010101'}


    
def eval_C(destination,compute):
    "Handles compute commands"
    return '111' + comp[compute] + dest[destination] + '000'

def eval_J(compute,jmp):
    "Handles jump commands"
    return '111'+ comp[compute] + '000' + jump[jmp]

def is_number(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

def eval_A(val):
    "Handles load commands"
    if is_number(val) == False:
        if val in asm.symbol:     # if we've already assigned a memory address to symbol, use that                      
            val = asm.symbol[val]      
        else:
            asm.symbol[val] = asm.symbol_address #if first we've seen of symbol
            val = asm.symbol[val]                       
            asm.symbol_address += 1 # increment symbol_address 
    return '0' + pad(binary(val),15)

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

asm = Asm(sys.argv[1])

AST = []
while asm.hasMoreCommands():  # first pass through to get labels and build build AST
    asm.advance()
    command_type = asm.commandType()
    current_command = asm.current_command
    if command_type == 'L_COMMAND':
        asm.symbol[current_command[1:-1]] = asm.lineno        
    else:
        AST.append((command_type,current_command))
        asm.lineno += 1
res=[]
for leaf in AST:
    if leaf[0] == 'C_COMMAND':
        exp = leaf[1]
        equal = exp.find('=')
        destination = exp[:equal]
        compute = exp[equal+1:]
        res.append(eval_C(destination,compute))
    elif leaf[0] == 'A_COMMAND':  
        command = leaf[1]
        res.append(eval_A(command[1:]))
    elif leaf[0] == 'J_COMMAND':
        command = leaf[1]
        semicolon = command.find(';')
        res.append(eval_J(command[:semicolon],command[semicolon+1:]))
    else:
        print 'problem in AST with this leaf, ', leaf

open(asm.fnameout,'w').write('\n'.join(res))

