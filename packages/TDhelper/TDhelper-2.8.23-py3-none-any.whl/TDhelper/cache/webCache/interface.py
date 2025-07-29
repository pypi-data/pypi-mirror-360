import abc
import six

@six.add_metaclass(abc.ABCMeta)
class cacheInterface:
    __cache__={}
    __cursor__=None
    @abc.abstractmethod
    def __init__(self):
        pass
    
    @abc.abstractmethod
    def set(self,*args,**kwargs):
        pass
        
    @abc.abstractmethod
    def get(self,flag='single',*args,**kwargs):
        pass
    
    @abc.abstractmethod
    def exist(self,*args,**kwargs):
        pass
    
    @abc.abstractmethod
    def collect(self,*args,**kwargs):
        pass
    
    @abc.abstractmethod
    def addCollect(self,k,v):
        pass
    
    @abc.abstractmethod        
    def delCollect(self,k):
        pass
    
    @abc.abstractmethod   
    def remove(self,*args,**kwargs):
        pass
    
    @abc.abstractmethod   
    def update(self,*args,**kwargs):
        pass