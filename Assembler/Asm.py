import re

class Asm(object):
    WORD = r'[a-zA-z\$\.\_\:]+[0-9a-zA-z\$\.\_\:]*'  
    LABEL = re.compile(r'\(' + WORD + r'\)') 
    JUMP = re.compile(r'(?:[AMD]|0);[A-Z]') 
    LOAD = re.compile(r'@(?:[0-9]+|' + WORD + r')')
    COMP = re.compile(r'[ADM]+=[-!]?[ADM10](?:[\-\+\|\&][ADM1])?')
    def __init__(self,fname):
        self.symbol = {  'SP': 0,    # mapping to both user defined and predefind symbols
            'LCL': 1,'ARG': 2,'THIS':3,'THAT':4,'R0': 0,'R1': 1,'R2': 2,'R3': 3,
            'R4': 4,'R5': 5,'R6': 6,'R7': 7,'R8': 8,'R9': 9,'R10':10,'R11':11,
            'R12':12,'R13':13,'R14':14,'R15':15,'SCREEN': 16384,'KBD': 24576 } 
        self.lineno = 0  # for labels
        self.symbol_address = 16 # keep track of where we are to store the next symbol we encounter
        period = fname.rfind('.')
        assert fname[period:] == '.asm'
        self.fnameout = fname[:period]+'.hack'  # name of file to be created
        self.fname = fname 
        self.commands = open(fname, 'r').readlines()
        # remove comments and whitespace
        for i,command in enumerate(self.commands):
            self.commands[i] = re.sub(r'(?://[^\n]*)| |\r|\n','',command)
        self.commands = [line for line in self.commands if line <> '\n' and line <> '']

    def __repr__(self):
        return 'Asm(%r)' %self.fname

    def hasMoreCommands(self):
        return self.commands <> [ ]

    def advance(self):
        self.current_command =self.commands.pop(0)
    
    def commandType(self):
        if self.LOAD.match(self.current_command):
            return 'A_COMMAND'
        elif self.COMP.match(self.current_command):
            return 'C_COMMAND'
        elif self.LABEL.match(self.current_command):
            return 'L_COMMAND'
        elif self.JUMP.match(self.current_command):
            return 'J_COMMAND'
        else: 
            print '%s is invalid' %self.current_command
