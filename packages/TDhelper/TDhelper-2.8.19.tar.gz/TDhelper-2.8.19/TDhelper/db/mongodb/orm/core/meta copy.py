import copy
from copy import deepcopy
from typing import TypeVar
from TDhelper.db.mongodb.orm.core.attribute import *
from TDhelper.db.mongodb.orm.core.field import *
from TDhelper.db.mongodb.orm.drives.conn import mongo_connector,connect_conf
conn= mongo_connector(connect_conf)

class objects_cls:
        __delete_state= None
        __conn= None
        __ins__= None
        __results= None
        __result_lists__= []
        __cursor=0
        @property
        def objects_delete(self):
            return self.__delete_state
        
        @objects_delete.setter
        def objects_delete(self, v:bool):
            if not self.__delete_state:
                self.__delete_state= v
            else:
                raise TypeError("objects_delete is readonly. only can be define once.")
            
        def __init__(self,conn,ins:Any) -> None:
            self.__conn= conn
            self.__ins__= ins
            
        def __iter__(self):
            self.__result_lists__= list(self.__results)
            return self
        
        def __next__(self) -> object:
            if self.__cursor< len(self.__result_lists__):
                o= self.__ins__(**self.__result_lists__[self.__cursor])
                self.__cursor+=1
                return o
            else:
                raise StopIteration()
            
        def all(self):
            return self
        
        def find(self,query={}):
            try:
                self.__results= self.__conn.find(query)
                return self
            except Exception as e:
                raise e
        
        
        def find_for_page(self,query={},pagesize:int=20,page:int=1):
            try:
                page= page if page>0 else 1
                m_skip = (page-1) * pagesize
                if m_skip < 0:
                    m_skip = 0
                self.__results= self.__conn.find(query).limit(pagesize).skip(m_skip)
                return self
            except Exception as e:
                raise e
        
        def skip(self,step:0):
            self.__results= self.__results.skip(step)
            return self
        
        def limit(self,l_c=0):
            self.__results= self.__results.limit(l_c)
            return self
        
        def get(self,pk):
            try:
                return self
            except Exception as e:
                raise e
        
        def insert(self,query) -> Any:
            try:
                return self.__conn.insert_many(query)
            except Exception as e:
                raise e
        
        def update(self,query,set) -> Any:
            try:                
                return self.__conn.update(query,{'$set':set})
            except Exception as e:
                raise e
            
        def delete(self):
            pass
T= TypeVar('T')

class new_objects:
    t_cls= None
    args= None
    
    def __init__(self,cls:T, args:tuple=()) -> None:
        self.t_cls= cls
        self.args= args

class mongo_db_meta(type):
    def __new__(cls,name, bases, dct):
        attrs={
            "__fields__":{},
            "__conn__":conn,
            "__collect__":conn.__db__[name],
            "__table__":name,
            "save": cls.save,
            "update": cls.update,
            "delete": cls.delete
        }
        meta_fields=['table']
        for k,v in dct.items():
            attrs.update({k:v})
            if isinstance(v,model):
                if v.model_type != field_type.BsonId:
                    attrs.get("__fields__").update({k.lower():None})
                    attrs[k]=oProperty(k,v)
                else:
                    if v.default:
                        attrs.get("__fields__").update({k.lower():bson.objectid.ObjectId(v.default)})
                    else:
                        attrs.get("__fields__").update({k.lower():None})
                    attrs[k]=oProperty(k,v)
            if k == "Meta":
                for o in v.__dict__:
                    if meta_fields.__contains__(o.lower()):
                        attrs["__collect__"]= conn.__db__[v.__dict__[o]]
                        attrs["__table__"]= v.__dict__[o]
                    else:
                        raise ValueError("Can not set Meta attribute '%s'" % o)
        if not attrs['__fields__'].__contains__("_id"):
            attrs["_id"]=oProperty("_id")
        new_cls= super(mongo_db_meta,cls).__new__(cls,name,bases,attrs) 
        setattr(cls,"_objects_ins",new_objects(objects_cls,(attrs["__collect__"],new_cls)))
        return new_cls
    
    def save(cls):
        try:
            return cls.__collect__.insert_one(cls.__fields__)
        except Exception as e:
            raise e
            
    def update(cls):
        try:
            sets= {}
            # exclude bson field.
            for k,v in cls.__fields__.items():
                if not isinstance(v,bson.objectid.ObjectId):
                    sets[k]=v
            result= cls.__collect__.update_one({"_id":cls._id},{"$set":sets})
            return result
        except Exception as e:
            cls.__fields__
            raise e
    
    def delete(cls):
        try:
            _id= cls._id
            cls.__fields__.clear()
            return cls.__collect__.delete_one({"_id":_id})
        except Exception as e:
            raise e
        
    
    @classmethod
    @property
    def objects(cls) -> objects_cls:
        return cls._objects_ins.t_cls(*cls._objects_ins.args)