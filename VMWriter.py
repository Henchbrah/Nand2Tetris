
class VMWriter(object):
    """Emits VM commands into a file, using the VM command syntax"""
    
    def __init__(self,name):
        """Creates a new file and prepares if for writing"""
        self.outname = name + '.vm'
        self.outfile = open(self.outname, 'w')
    
    def writePush(self,segment,index):
        """Writes a VM push command"""      
        self.outfile.write('push %s %d\n' %(segment,index))

    def writePop(self,segment,index):
        """Writes a VM pop command"""
        self.outfile.write('pop %s %d\n' %(segment,index))

    def writeArithmetic(self,command):
        """Writes a VM arithmetic command"""
        self.outfile.write('%s\n' %command)


    def writeLabel(self,label):
        """Writes a VM label command"""
        self.outfile.write('label %s\n' %label)
	

    def writeGoto(self,label):
        """Writes a VM goto command"""
        self.outfile.write('goto %s\n' %label)


    def writeIf(self,label):
        """Writes a VM if-goto command"""
        self.outfile.write('if-goto %s\n' %label)

    def writeCall(self,name,nArgs):
        """Writes a VM call command"""
        self.outfile.write('call %s %d\n' %(name,nArgs)) 

    def writeFunction(self,name,nLocals):
        """Writes a VM function command"""
        self.outfile.write('function %s %s\n'%(name,nLocals))

    def writeReturn(self):
        """Wrties a VM return command"""
        self.outfile.write('return\n')

    def close(self):
        """Closes output file"""
        self.outfile.close()

