import os
import JackTokenizer as jT
import CompilationEngine as cE 
import SymbolTable as sT
import VMWriter as vmW
from sys import argv

arg = argv[1]
if not os.path.isfile(arg):
    directory = arg
    if directory.endswith('/'):
        directory = directory[:-1]
    os.chdir(directory)
    files = [f for f in os.listdir('.') if f.endswith('.jack')]
else:
    files = [arg]

for f in files:
    outname = f.split('/')[-1].split('.')[0] 
    tokenizer = jT.JackTokenizer(f)
    table = sT.SymbolTable()
    writer = vmW.VMWriter(outname)           
    engine = cE.CompilationEngine(tokenizer,table,writer)
    engine.compileClass()
    print 'COMPILING %s'%f

        


