
class VMWriter(self):
    """Emits VM commands into a file, using the VM command syntax"""
    
    def __init__(self,name):
        """Creates a new file and prepares if for writing"""
        self.outname = name + '.vm'
        self.outfile = open(self.outname, 'w')
    
    def writePush(self,segment):
        """Writes a VM push command"""      
        pass

    def writePop(self,segment):
        """Writes a VM pop command"""
        pass

    def writeArithmetic(self,command):
        """Writes a VM arithmetic command"""
        pass


    def writeLabel(self,label):
        """Writes a VM label command"""
        pass
        

    def writeGoto(self,label):
        """Writes a VM goto command"""
        pass


    def writeIf(self,label):
        """Writes a VM if-goto command"""
        pass

    def writeCall(self,name,nArgs):
        """Writes a VM call command"""
        pass

    def writeFunction(self,name,nLocals):
        """Writes a FM function command"""
        pass

    def writeReturn(self):
        """Wrties a VM return command"""
        pass

    def close(self):
        """Closes output file"""
        pass


