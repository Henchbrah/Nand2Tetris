import os
import JackTokenizer as jackT
import CompilationEngine as compE 
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
    tokenizer = jackT.JackTokenizer(f)
    engine = compE.CompilationEngine(outname,tokenizer)
    print 'COMPILING %s'%f
    engine.compileClass()
        


