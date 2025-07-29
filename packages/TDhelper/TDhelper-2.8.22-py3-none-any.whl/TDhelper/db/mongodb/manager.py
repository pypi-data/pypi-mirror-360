from TDhelper.db.mongodb.obsoletess_dbhelper import dbhelper

class mongodbAND:
    def __new__(cls,conditions:list=[dict]):
        cls.conditions={
            "$and":conditions
        }
        return cls.conditions

class mongodbOR:
    def __new__(cls,conditions:list=[dict]):
        cls.conditions={
            "$or":conditions
        }
        return cls.conditions

class query(dbhelper):
    def __init__(self,conditions:dict={},db=None):
        self.conditions=conditions
        self.setCollection(db)
        
    def filter(self,**kwargs):
        return self.dbClient.collection.find(**kwargs)
    
    def insert(self,**kwargs):
        return self.dbClient.collection.insert_one(**kwargs)
    
    def insert_many(self,**kwargs):
        return self.dbClient.collection.insert_many(**kwargs)
    
    def delete(self,**kwargs):
        return self.dbClient.collection.remove(**kwargs)
    
    def update(self,query:dict={},**kwargs):
        return self.dbClient.collection.update_one(query, {'$set': kwargs})

class querySet(query):
    def __iter__(self):
        self.result=[o for o in range(1,10)]
        return iter(self.result)
        
    db= None
    def __init__(self):#,model,collect):
        self.result=[]
        self.condition={
            "query":{},
            "display":{},
            "skip":None,
            "limit":{},
            "order":{},
            "group":{}
        }

    def all(self):
        self.condition["query"].update({})
        return self
    
    def filter(self,kwargs:dict={}):
        for k,v in kwargs.items():
            self.condition["query"].update({k:v})
        return self
    
    def skip(self,num):
        return self
    
    def limit(self,kwargs:dict={}):
        return self
    
    def orderBy(self,kwargs:dict={}):
        return self
    
    def groupBy(self,kwargs:dict={}):
        return self
    
    def displayFields(self,kwargs:dict={}):
        if "display" not in self.condition:
            self.condition.update({"diplay":kwargs}) 
        else:
            for k,v in kwargs.items():
                self.condition['display'].update({k:v})
            
        return self

if __name__=="__main__":
    q=querySet().filter({"a":1,"b":5}).filter({"c":3,"d":12}).displayFields({"a":1,"b":1,"d":0}).all().filter(mongodbAND([{"and1":1},{"and2":2}]))
    for c in q:
        print(c)
    