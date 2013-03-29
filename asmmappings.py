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
    #
three_bin_digits = map(pad,map(binary,range(8)))
j_mnemonics = ['null','JGT','JEQ','JGE','JLT','JNE','JLE','JMP']
d_mnemonics = ['null','M','D','MD','A','AM','AD','AMD']
JUMP =  dict(zip(j_mnemonics,three_bin_digits))
DEST = dict(zip(d_mnemonics,three_bin_digits))
COMP = {'0':  '0101010',
        '1':  '0111111',
        '-1': '0111010',
        'D':  '0001100',
        'A':  '0110000',
        'M':  '1110000',
        '!D': '0001101',
        '!A': '0110001',
        '!M': '1110001',
        '-D': '0001111',
        '-A': '0110011',
        '-M': '1110011',
        'D+1':'0011111',
        'A+1':'0110111',
        'M+1':'1110111',
        'D-1':'0001110',
        'A-1':'0110010',
        'M-1':'1110010',
        'D+A':'0000010',
        'D+M':'1000010',
        'D-A':'0010011',
        'D-M':'1010011',
        'A-D':'0000111',
        'M-D':'1000111',
        'D&A':'0000000',
        'D&M':'1000000',
        'D|A':'0010101',
        'D|M':'1010101'}

Symbol = {  'SP': 0,    # mapping to both user defined and predefind symbols
            'LCL': 1,'ARG': 2,
            'THIS':3,'THAT':4,
            'R0': 0,'R1': 1,
            'R2': 2,'R3': 3,
            'R4': 4,'R5': 5,
            'R6': 6,'R7': 7,
            'R8': 8,'R9': 9,
            'R10':10,'R11':11,
            'R12':12,'R13':13,
            'R14':14,'R15':15,
            'SCREEN': 16384,
            'KBD': 24576 } 
