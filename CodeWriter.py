
bin_ops = ('add','sub','and','or')
unary_ops = ('neg','not')    
compare = ('eq','gt','lt')
Op = dict(zip(bin_ops,('+','-','&','|')))
Op.update(zip(unary_ops,('-','!')))
Comp = dict(zip(compare,('JEQ','JGT','JLT')))
Seg = dict(zip(('local','argument','this','that','temp','pointer','static'),('LCL','ARG','THIS','THAT',5,3,16)))

class CodeWriter(object):
    """Translates VM commands into Hack Assembly code"""
    def __init__(self,name):
        self.endoflabel = 1
        self.endoffunc = 1
        self.outname = name + '.asm'
        self.outfile = open(self.outname, "w")
        self.writeInit()
        
    
    def __repr__(self):
        return 'CodeWriter(%s)' % self.outname

    def setFileName(self,fname):
        """Sets name of current file we are working on"""
        self.fileName = fname

    def writeInit(self):
        self.outfile.write('@256\n')
        self.outfile.write('D=A\n')
        self.outfile.write('@SP\n')
        self.outfile.write('M=D\n')
        self.writeCall('Sys$init', 0)   ########## not sure about this ###########

    def writeLabel(self,label):
        """Labels current locatin in function's code, within scope of function in which it is defined"""
        #self.outfile.write('WRITE LABEL\n')
        self.outfile.write('(%s)\n' %label)
   
    def writeGoto(self,label):
        """Effects unconditional jump, destination is within scope of function in which it is defined"""
        #self.outfile.write('WRITE GOTO\n')
        self.outfile.write('@%s\n' %label)
        self.outfile.write('0;JMP\n')    

    def writeIf(self,label):
        """Effects conditional goto, if top of stack is <> 0, goto label"""
        #self.outfile.write('GOTO-IF\n')
        self.popToD()
        self.outfile.write('@%s\n' %label)
        self.outfile.write('D;JNE\n')

    def writeCall(self,functionName,numArgs):   # arguments would have already been pushed unto stack      
        """Prep for and call function"""
        #self.outfile.write('CALL %s %s\n' %(functionName,numArgs))
        argOffset = int(numArgs) + 5
        returnLabel = 'return%s%d' %(functionName,self.endoffunc) 
        self.endoffunc += 1
        self.outfile.write('@%s\n' %returnLabel)
        self.outfile.write('D=A\n')
        self.pushD()
        for segment in ('LCL','ARG','THIS','THAT'):   # push base address of segments
            self.outfile.write('@%s\n' %segment)
            self.outfile.write('D=M\n')
            self.pushD()
        self.outfile.write('@SP\n')           # reposition ARG
        self.outfile.write('D=M\n')
        self.outfile.write('@%d\n' %argOffset)
        self.outfile.write('D=D-A\n')#SP-n-5
        self.outfile.write('@ARG\n')
        self.outfile.write('M=D\n')
        
        self.outfile.write('@SP\n')              # reposition LCL
        self.outfile.write('D=M\n')
        self.outfile.write('@LCL\n')
        self.outfile.write('M=D\n')
        self.writeGoto(functionName)
        self.writeLabel(returnLabel)
        
    def writeReturn(self):
        FRAME = 'R5'
        RET = 'R6' 
        #self.outfile.write('assign LCL to temporary variable\n')
        self.outfile.write('@LCL\n')        #assign LCL to temporary variable 'FRAME'
        self.outfile.write('D=M\n')
        self.outfile.write('@%s\n' %FRAME)
        self.outfile.write('M=D\n')    #now FRAME is pointer to same address LCL held
        #self.outfile.write('assign RET to temp variable\n')
        self.outfile.write('D=M\n')         #assign RET to temp variable 
        self.outfile.write('@5\n')
        self.outfile.write('D=D-A\n')
        self.outfile.write('@%s\n' %RET)
        self.outfile.write('M=D\n')      #now RET points to return argument from called function
        #self.outfile.write('reposition ARG the return value for caller\n')
        self.popToD()
        self.outfile.write('@ARG\n')       #reposition ARG the return value for caller
        self.outfile.write('A=M\n')
        self.outfile.write('M=D\n')     # now ARG is pointer to return value       
        #self.outfile.write('restore SP of caller')
        self.outfile.write('@ARG\n')    #restore SP of ca\nller
        self.outfile.write('D=M+1\n')
        self.outfile.write('@SP\n')
        self.outfile.write('M=D\n')
        #self.outfile.write('restore THAT,THIS,ARG and LCL')
        self.outfile.write('@%s\n' %FRAME) #restore THAT,THIS,ARG and LCL
        self.outfile.write('A=M-1\n')
        self.outfile.write('D=M\n')
        self.outfile.write('@THAT\n')
        self.outfile.write('M=D\n')
        
        self.outfile.write('@%s\n' %FRAME)
        self.outfile.write('D=M\n')
        self.outfile.write('@2\n')
        self.outfile.write('A=D-A\n')
        self.outfile.write('D=M\n')
        self.outfile.write('@THIS\n')
        self.outfile.write('M=D\n')

        self.outfile.write('@%s\n' %FRAME)
        self.outfile.write('D=M\n')
        self.outfile.write('@3\n')
        self.outfile.write('A=D-A\n')
        self.outfile.write('D=M\n')
        self.outfile.write('@ARG\n')
        self.outfile.write('M=D\n')

        self.outfile.write('@%s\n' %FRAME)
        self.outfile.write('D=M\n')
        self.outfile.write('@4\n')
        self.outfile.write('A=D-A\n')
        self.outfile.write('D=M\n')
        self.outfile.write('@LCL\n')
        self.outfile.write('M=D\n')
        #self.outfile.write('goto return address')
        self.outfile.write('@%s\n' %RET) #goto return address
        self.outfile.write('A=M\n')
        self.outfile.write('A=M\n')
        self.outfile.write('0;JMP\n')
        

    def writeFunction(self,functionName,numLocals):
        """Declares a function. Initializes local variables to zero"""
        #self.outfile.write('FUNCTION %s %s\n' %(functionName,numLocals))
        self.writeLabel(functionName)
        for _ in range(int(numLocals)):
            self.outfile.write('@0\n')
            self.outfile.write('D=A\n')
            self.pushD()

    def writeArithmetic(self,command):
        """Writes arithmetic commands"""
        #self.outfile.write('ARITHMETIC %s\n' %command)
        if command in bin_ops:             
            self.twoFromStack()
            self.outfile.write('D=A%sD\n'%Op[command])
            self.pushD()

        elif command in unary_ops:
            self.popToD()
            self.outfile.write('D=%sD\n'%Op[command])
            self.pushD()

        elif command in compare:
            true = 'TRUE%s' %(self.endoflabel)
            skip = 'SKIP%s' %(self.endoflabel)
            self.endoflabel += 1
            self.twoFromStack()
            self.outfile.write('D=A-D\n')
            self.outfile.write('@%s\n' %true)
            self.outfile.write('D;%s\n' %Comp[command])
            self.outfile.write('@SP\n')
            self.outfile.write('A=M\n')
            self.outfile.write('M=0\n')
            self.incrementSP()  
            self.outfile.write('@%s\n' %skip)
            self.outfile.write('0;JMP\n')    #skip over 'true' clause
            self.outfile.write('(%s)\n' %true) # (TRUE)
            self.outfile.write('@SP\n')
            self.outfile.write('A=M\n')
            self.outfile.write('M=-1\n')
            self.incrementSP()
            self.outfile.write('(%s)\n' %skip) # (SKIP)
          

    def pushD(self):
        """Pushes value of D reg onto stack"""
        #self.outfile.write('PUSH D\n')
        self.outfile.write('@SP\n')
        self.outfile.write('A=M\n')
        self.outfile.write('M=D\n')
        self.incrementSP()        

    def twoFromStack(self):
        """Pops top two elements from stack and stores them in Reg A and Reg D respectively"""
        #self.outfile.write('TWO FROM STACK\n')
        self.popToD()
        self.popToA()

    def decrementSP(self):
        """Decrements SP"""
        self.outfile.write('@SP\n')
        self.outfile.write('M=M-1\n')

    def incrementSP(self):
        """Increments SP"""
        self.outfile.write('@SP\n')
        self.outfile.write('M=M+1\n')        

    def popToA(self):
        """Pops the top of stack to A reg"""
        self.decrementSP()
        self.outfile.write('@SP\n')
        self.outfile.write('A=M\n')
        self.outfile.write('A=M\n')

    def popToD(self):
        self.decrementSP()
        self.outfile.write('@SP\n')
        self.outfile.write('A=M\n')
        self.outfile.write('D=M\n')
        
         
    def writePushPop(self,command,segment,index): 
        """Push or pops from designated segment and index"""
        #self.outfile.write('%s %s %s\n' %(command,segment,index))     
        if command == 'push':
            if segment == 'constant':
                self.outfile.write('@%s\n' %index)
                self.outfile.write('D=A\n')
            elif segment in ('temp','pointer'):
                self.outfile.write('@%d\n' %(Seg[segment] + int(index)))
                self.outfile.write('D=M\n')
            elif segment == 'static':
                varName = self.fileName + index
                self.outfile.write('@%s\n' %varName)
                self.outfile.write('D=M\n')            
            else:
                symbol = Seg[segment]
                self.outfile.write('@%s\n' %symbol)
                self.outfile.write('D=M\n')
                self.outfile.write('@%s\n' %index)
                self.outfile.write('A=D+A\n')
                self.outfile.write('D=M\n')
            self.pushD()
        elif command == 'pop':
            if segment in ('temp','pointer'):
                self.outfile.write('@%d\n' %(Seg[segment] + int(index)))
                self.outfile.write('D=A\n')
                self.outfile.write('@R13\n')
                self.outfile.write('M=D\n')
            elif segment == 'static':
                varName = self.FileName + index
                self.outfile.write('@%s\n' %varName)
                self.outfile.write('D=A\n')
                self.outfile.write('@R13\n')
                self.outfile.write('M=D\n')
            else:
                symbol = Seg[segment]
                self.outfile.write('@%s\n' %symbol)
                self.outfile.write('D=M\n')
                self.outfile.write('@%s\n' %index)
                self.outfile.write('D=D+A\n')
                self.outfile.write('@R13\n')
                self.outfile.write('M=D\n')
            self.popToD()
            self.outfile.write('@R13\n')
            self.outfile.write('A=M\n')
            self.outfile.write('M=D\n')

    def close(self):
        self.outfile.close()


if __name__ == "__main__":
    from Parser import *
    import os
    testfile = '/home/agnesi/nand2tetris/projects/07/StackArithmetic/StackTest/StackTest.vm'
    parser = Parser(testfile)
    test = CodeWriter(parser)
    os.system('clear')
    print 'File to be written to is  %s' %test.outname
    raw_input('PRESS ENTER TO CONTINUE')
    os.system('clear')
    print 'The VM commands to be translated and their corresponding are: '
    while parser.hasMoreCommands():
        parser.advance()
        print parser.currentcommand
        

    
