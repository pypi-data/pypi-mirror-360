from TDhelper.cache.webCache.mongo import mongo
class webCacheFactory:
    __cache__={}
    __cursor__=None
    __handle__=None
    def __init__(self,conf={}):
        assert 'ENGINE' in conf, "'ENGINE' not in conf"
        cls= conf['ENGINE'].lower()
        if cls=="memory":
            pass
        elif cls=="mongo":
            self.__handle__= mongo(**conf)
        elif cls=="redis":
            pass
        else:
            raise Exception("cls must value: memory | mongo | redis.")
    
    def set(self,*args,**kwargs):
        return self.__handle__.set(*args,**kwargs)
        
    def get(self,flag='single',*args,**kwargs):
        return self.__handle__.get(flag,*args,**kwargs)

    def exist(self,*args,**kwargs):
        return self.__handle__.exist(*args,**kwargs)
    
    def collect(self,k):
        self.__handle__.collect(k)
        return self
    
    def addCollect(self,k,v):
        return self.__handle__.addCollect(k,v)
         
    def delCollect(self,k):
        return self.__handle__.delCollect(k)
    
    def remove(self,*args,**kwargs):
        return self.__handle__.remove(*args,**kwargs)
    
    def update(self,*args,**kwargs):
        return self.__handle__.update(*args,**kwargs)