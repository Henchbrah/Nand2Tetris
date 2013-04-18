import re

class Parser(object):
    """Handles parsing of single .vm file, and encapsulates access to the input code.
       Reads VM commands, parses them, and provides access to their components. In addition,
       removes white space and comments."""

    def __init__(self,fname):
        self.fname = fname
        self.commands = open(fname, 'r').readlines()
        self.cleanUp()

    def __repr__(self):
        return 'Parser(%s)' %self.fname

    def cleanUp(self):
        """Remove comments and normalize whitespace"""
        for (i,command) in enumerate(self.commands):
            self.commands[i] = re.sub(r'(?://[^\n]*)|\r|\n','',command)
        self.commands = [' '.join(line.split()) for line in self.commands if line <> '']

    def hasMoreCommands(self):
        """Return True if more commands to parse else return False"""
        return self.commands <> [ ]

    def advance(self):
        """Make next command in command the current command"""
        self.currentcommand = self.commands.pop(0)

    def commandType(self):
        """return command type of current command"""
        types = ('C_ARITHMETIC','C_PUSH','C_POP','C_LABEL',
                    'C_GOTO','C_IF','C_FUNCTION','C_RETURN','C_CALL')
        keyword = self.currentcommand.split(" ",1)[0]
        if keyword in ('add','sub','neg','eq','gt','lt','and','or','not'):
            return types[0]
        elif keyword == 'push':
            return types[1]
        elif keyword == 'pop':
            return types[2]
        elif keyword == 'label':
            return types[3]
        elif keyword == 'goto':
            return types[4]
        elif 'if' in keyword:
            return types[5]
        elif keyword == 'function':
            return types[6]
        elif keyword == 'return':
            return types[7]
        elif keyword == 'call':
            return types[8]
        else:
            raise Exception('Parser cannot determing command type for %s' %self.currentcommand)

    def arg1(self):
        """Return first argument of current command, if is arithmetic command will return command itself(sub,add etc)"""
        atoms = self.currentcommand.split()
        if self.commandType() == 'C_ARITHMETIC':
            return atoms[0]
        else:
            return atoms[1]
    
    def arg2(self):
        """return second argument of command which should be an int"""
        atoms = self.currentcommand.split()
        return atoms[2]
    

if __name__ == '__main__':
    from sys import argv    
    testfile = './FunctionCalls/SimpleFunction/SimpleFunction.vm'
    if len(argv) > 1: testfile = argv[1]
    test = Parser(testfile)
    while test.hasMoreCommands():
        test.advance()
        print test.commandType().ljust(20), 'Command: ',test.currentcommand,
        if test.commandType() <> 'C_RETURN':
            print 'Arg1: ',test.arg1(), 
        if test.commandType() in ('C_PUSH','C_POP','C_FUNCTION','C_CALL'):
            print 'Arg2: ',test.arg2()
        print 

 
