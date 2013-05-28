
class SymbolTable(object):
    """Provides a symbl table abtraction"""
    def __init__(self):
        """Creates a new empty Symbol Table"""
        self.classTable = {}
        self.subroutineTable = {}
        self.scope = self.classTable
        self.outerscope = None

    def startSubroutine(self):
        """Starts a new subroutine scope(i.e. resets the subroutine's symbol table)"""
        self.subroutineTable = {}
        self.scope = self.subroutineTable
        self.outerscope = self.classTable

    def endSubroutine(self):
        self.outerscope = None
        self.scope = self.classTable

    def define(self,name,type,kind):
        """Defines a new Identifier of a given name, type and kind and assigns it to
        a running index. STATIC and FIELD identifiers have a class scope, while ARG and VAR
        have a subroutine scope"""
        self.scope[name] = (type,kind,self.varCount(kind))

    def varCount(self, kind):
        """Returns the number of variables of the given kind already defined in the current scope"""
        return len([k for (t,k,n) in self.scope.values() if k == kind])

    def kindOf(self,name):
        """Returns the kind of the named identifier in the current scope. If the identifier is unknown
        in the current scope, returns None"""   
        try:
            return self.scope[name][1]
        except KeyError:
            return None
      
    def typeOf(self,name):
        """Returns the type of the named identifier in the current scope"""
        try:
            return self.scope[name][0]
        except KeyError:
            return None

    def indexOf(self,name):
        """Returns the index assigned to the named identifier"""
        try:
            return self.scope[name][2]
        except KeyError:
            return None

    def kindOfOuterScope(self,name):
        """Returns the kind of the named identifier in the current scope. If the identifier is unknown
        in the current scope, returns None"""   
        try:
            return self.outerscope[name][1]
        except KeyError:
            return None
      
    def typeOfOuterScope(self,name):
        """Returns the type of the named identifier in the current scope"""
        try:
            return self.outerscope[name][0]
        except KeyError:
            return None

    def indexOfOuterScope(self,name):
        """Returns the index assigned to the named identifier"""
        try:
            return self.outerscope[name][2]
        except KeyError:
            return None

    def getKind(self,name):
        innerScope = self.kindOf(name)
        if innerScope or self.outerscope == None:
            return innerScope
        else:  
            try:        
                return self.kindOfOuterScope(name)
            except KeyError:
                return None        
    
    def getType(self,name):
        innerScope = self.typeOf(name)
        if innerScope or self.outerscope == None:
            return innerScope
        else:          
            try:        
                return self.typeOfOuterScope(name)
            except KeyError:
                return None   

    def getIndex(self,name):
        innerScope = self.indexOf(name)
        if innerScope or self.outerscope == None:
            return innerScope
        else:          
            try:        
                return self.indexOfOuterScope(name)
            except KeyError:
                return None   
        
