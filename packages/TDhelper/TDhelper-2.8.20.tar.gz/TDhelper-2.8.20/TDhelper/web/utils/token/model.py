import __init__
from TDhelper.cache.webCache.webCacheFactory import webCacheFactory
from TDhelper.db.mongodb.objectId import objectId
from TDhelper.db.mongodb.setting import db_cfg
import datetime
from TDhelper.generic.crypto.MD5 import MD5

class Token(objectId):
    
    def __init__(self, **kwargs):
        print(self.__dict__)
        super(Token, self).__init__()
        self.model["createTime"] = datetime.datetime.now()
        self.model["lastUpdateTime"] = datetime.datetime.now()
        self.model["expire"] = datetime.datetime.now().__add__(datetime.timedelta(minutes=5))
        self.model["used"] = False
        self.model["once"] = False
        self.model["renewal"]= False
        for k, v in kwargs.items():
            self.model[k] = v

    @property
    def token(self):
        if 'token' in self.model:
            return self.model['token']
        else:
            raise Exception("NOT FOUND 'token' in model.")

    @token.setter
    def token(self, v):
        if 'token' in self.model:
            self.model['token'] = v
        else:
            raise Exception("NOT FOUND 'token' in model.")

    @property
    def expire(self):
        if 'expire' in self.model:
            return self.model['expire']
        else:
            raise Exception("NOT FOUND 'expire' in model.")

    @expire.setter
    def expire(self, v):
        if 'expire' in self.model:
            self.model['expire'] = v
        else:
            raise Exception("NOT FOUND 'expire' in model.")

    @property
    def remoteIP(self):
        if 'remoteIP' in self.model:
            self.model['remoteIP']
        else:
            raise Exception("NOT FOUND 'remoteIP' in model.")

    @remoteIP.setter
    def remoteIP(self, v):
        if 'remoteIP' in self.model:
            self.model['remoteIP'] = v
        else:
            raise Exception("NOT FOUND 'remoteIP' in model.")

    @property
    def once(self):
        if 'once' in self.model:
            return self.model['once']
        else:
            raise Exception("NOT FOUND 'once' in model.")

    @once.setter
    def once(self, v):
        if 'once' in self.model:
            self.model['once'] = v
        else:
            raise Exception("NOT FOUND 'once' in model.")

    @property
    def used(self):
        if 'used' in self.model:
            return self.model['used']
        else:
            raise Exception("NOT FOUND 'used' in model.")

    @used.setter
    def used(self, v):
        if 'used' in self.model:
            self.model['used'] = v
        else:
            raise Exception("NOT FOUND 'used' in model.")

    @property
    def belong(self):
        if 'belong' in self.model:
            return self.model['belong']
        else:
            raise Exception("NOT FOUND 'belong' in model.")

    @belong.setter
    def belong(self, v):
        if 'belong' in self.model:
            self.model['belong'] = v
        else:
            raise Exception("NOT FOUND 'belong' in model.")

    @property
    def createTime(self):
        if 'createTime' in self.model:
            return self.model['createTime']
        else:
            raise Exception("NOT FOUND 'createTime' in model.")

    @createTime.setter
    def createTime(self, v):
        if 'createTime' in self.model:
            self.model['createTime'] = v
        else:
            raise Exception("NOT FOUND 'createTime' in model.")

    @property
    def lastUpdateTime(self):
        if 'lastUpdateTime' in self.model:
            return self.model['lastUpdateTime']
        else:
            raise Exception("NOT FOUND 'lastUpdateTime' in model.")

    @lastUpdateTime.setter
    def lastUpdateTime(self, v):
        if 'lastUpdateTime' in self.model:
            self.model['lastUpdateTime'] = v
        else:
            raise Exception("NOT FOUND 'lastUpdateTime' in model.")

    @property
    def targetService(self):
        if 'targetService' in self.model:
            return self.model['targetService']
        else:
            raise Exception("NOT FOUND 'targetService' in model.")

    @targetService.setter
    def targetService(self, v):
        if 'targetService' in self.model:
            self.model['targetService'] = v
        else:
            raise Exception("NOT FOUND 'targetService' in model.")

    @property
    def renewal(self):
        if 'renewal' in self.model:
            return self.model['renewal']
        else:
            raise Exception("NOT FOUND 'renewal' in model.")
        
    @renewal.setter
    def renewal(self,v):
        if 'renewal' in self.model:
            self.model['renewal']=v
        else:
            raise Exception("NOT FOUND 'renewwal' in model.")