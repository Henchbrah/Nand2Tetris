#! /usr/bin/env python
"""First version of an assembler for the Hack Platform."""
import sys,re


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

class Asm(object):
    def __init__(self,f):
        delimiters = r"\@|\;|\="
        res = []
        code = open(f,"r")
        i = 0
        self.Symbol = Symbol.copy()
        for line in code:
            line = re.sub(r"//[^\n]*\n","",line).strip()
            label = re.findall(r"\(.+\)",line)
            if label:
                assert len(label) == 1
                self.Symbol[label[0][1:-1]] = i
                line = ''
            if line:
                res.append(line)
                i += 1
        self.code = res
        code.close()


    def __str__(self):
        return '\n'.join(self.code)

    def make_tree(self):  # not to be called directly
        self.tree = []
        # delimiters = ; @ =
        for line in self.code:
            semicolon = line.find(';')
            at = line.find('@')
            equal = line.find('=')
            if semicolon != -1:
                self.tree.append( ('jump',line[:semicolon],line[semicolon+1:]) )
            elif equal != -1:
                self.tree.append( ('assign',line[:equal],line[equal+1:]) )
            elif at != -1:
                assert at == 0
                self.tree.append( ('load',line[1:]) )
            else:
                print 'Error creating tree from this line ', line
        return self.tree

    def interpret(self):         # not to be called directly
        res = []               
        symbol_address = 16 
        for leaf in self.tree:
            if leaf[0] == 'load':
                val = leaf[1]
                try:
                    val = str(int(val)) # if you can convert it to integer it must be string of numbers
                except ValueError:                    
                    if val in self.Symbol:     # if we've already assigned a memory address to symbol, use that                      
                        val = self.Symbol[val]      
                    else:
                        val = self.Symbol[leaf[1]] = symbol_address   #if first we've seen of symbol                       
                        symbol_address += 1                           # a memory address and increment symbol_address
                res.append('0' + pad(binary(val),15))
            elif leaf[0] == 'assign':
                comp_code = leaf[2]
                destination = leaf[1]
                res.append('111' + COMP[comp_code] + DEST[destination] + '000')
            elif leaf[0] == 'jump':
                jump_code = leaf[2]
                comp_code = leaf[1]
                res.append('111'+ COMP[comp_code] + '000' + JUMP[jump_code])
            else:
                print 'Error interpreting this leaf ', leaf 

        return '\n'.join(res)
  

    def assemble(self): 
        """creates parse tree and interprets it"""
        self.make_tree()
        return self.interpret()
                         
            

if __name__ == "__main__":  
    name_in = sys.argv[1]
    period = name_in.find('.')
    name_out = name_in[:period] + '.hack'
    file_out = open(name_out,"w")
    asm = Asm(sys.argv[1])
    file_out.write(asm.assemble())
    file_out.close()



            
