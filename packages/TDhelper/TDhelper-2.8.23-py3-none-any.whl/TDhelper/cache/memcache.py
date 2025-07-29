from TDhelper.generic.dictHelper import findInDict, hitDict,setDictValue,destoryKey,appendDict
class cache:
    __cache__={}

    @classmethod
    def insert(self,k,v):
        appendDict(k,v,self.__cache__)
    
    @classmethod
    def append(self,k,v):
        if k in self.__cache__:
            raise Exception("%s already."%k)
        appendDict(k,v,self.__cache__)

    @classmethod
    def update(self,k,v):
        setDictValue(k,v,self.__cache__)

    @classmethod
    def destory(self,k):
        destoryKey(k,self.__cache__)

    @classmethod
    def findValue(self,k):
        return findInDict(k,self.__cache__)

    @classmethod
    def findInstance(self,k):
        return hitDict(k,self.__cache__)

    @classmethod
    def __get__(self):
        return self.__cache__
    
    @classmethod
    def __items__(self):
        return self.__cache__.items()
    
    @classmethod
    def __clear__(self):
        self.__cache__.clear()