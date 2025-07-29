from TDhelper.db.mongodb.orm.core.meta import *

class model(metaclass= mongo_db_meta):
        '''mongo db orm model class.
        
        define fileds with filed class.
        
        class Meta:
            table - <class, str>: if not set value, it is class name  
        '''
        _id= field(type= field_type.BsonId)
        
        #class Meta:
        #    table= "testdb_db"
        
        def __init__(self,**kwargs) -> None:
            self.__mongo__= self.__db_drives__(connect_conf)
            if self.__table__ != "model":
                self.__collect__= self.__mongo__.__db__[self.__table__]
            for k,v in kwargs.items():
                if hasattr(self,k):
                    self.__setattr__(k,v)