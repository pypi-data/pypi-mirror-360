'''
from TDhelper.db.mongodb.obsoletess_dbhelper import dbhelper
class Objects(dbhelper): 
    @classmethod
    def filter(cls,**kwargs):
        result= cls.find(**kwargs)
        return result
    
    @classmethod    
    def getById(cls,oId):
        return cls.findOne(**{"oId":oId})
    
    @classmethod
    def delete(cls,**kwargs):
        cls.remove(**kwargs)
        
    @classmethod
    def update(cls,condition:dict,**kwargs):
        return cls.update(condition,**kwargs)
    
    @classmethod
    def insert(cls,flag="one",**kwargs):
        return cls.insert(flag,**kwargs)
'''