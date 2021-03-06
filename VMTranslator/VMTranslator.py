from Parser import *
from CodeWriter import *
from sys import argv
import os

directory = argv[1]
if directory.endswith('/'):
    directory = directory[:-1]
outname = directory.split('/')[-1]
os.chdir(directory)
files = [f for f in os.listdir('.') if f.endswith('.vm')]

codewriter = CodeWriter(outname)

for f in files:
    parser = Parser(f)
    codewriter.setFileName(f[:-3])
    while parser.hasMoreCommands():
        parser.advance()
        Ctype = parser.commandType()
        if Ctype == 'C_ARITHMETIC':
            codewriter.writeArithmetic(parser.currentcommand)
        elif Ctype in ('C_PUSH','C_POP'):
            if 'pop' in parser.currentcommand:
                command = 'pop'
            else:
                command = 'push'
            segment = parser.arg1()
            index = parser.arg2()
            codewriter.writePushPop(command,segment,index)
        elif Ctype == 'C_LABEL':
            label = parser.arg1()
            codewriter.writeLabel(label)
        elif Ctype == 'C_GOTO':
            label = parser.arg1()
            codewriter.writeGoto(label)
        elif Ctype == 'C_IF':
            label = parser.arg1()
            codewriter.writeIf(label)
        elif Ctype == 'C_FUNCTION':
            name = parser.arg1().replace('.','$')
            num = parser.arg2()
            codewriter.writeFunction(name,num)
        elif Ctype == 'C_RETURN':
            codewriter.writeReturn()
        elif Ctype == 'C_CALL':
            name = parser.arg1().replace('.','$')
            num = parser.arg2()
            codewriter.writeCall(name,num)  
        codewriter.outfile.write('@22222\n')     # BreakPoint 

codewriter.close()

        
