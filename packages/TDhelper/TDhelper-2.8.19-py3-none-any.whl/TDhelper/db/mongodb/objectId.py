#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import bson
import copy
import inspect
from TDhelper.db.mongodb.dbhelper import dbhelper

'''
class\r\n
    objectId
description\r\n
    mongodb's bson.objectid\r\n
'''
class objectId:
    model=None
    objects= dbhelper()
    def __init__(self,**kwargs):
        self.objects.setCollection(type(self).__name__)
        self.model={
            name: None for name,prop in inspect.getmembers(type(self)) if isinstance(prop,property)
        }
        for k,v in kwargs:
            self.model[k]=v
            
    @property
    def oId(self):
        if self.model["oId"]:
            return self.model["oId"]
        else:
            self.model["oId"]=bson.objectid.ObjectId()
            return self.model["oId"]
    @oId.setter
    def oId(self,args):
        if args:
            self.model["oId"]=bson.objectid.ObjectId(args)
        else:
            self.model["oId"]=bson.objectid.ObjectId()
        
    def toSave(self):
        '''
        obsolete
        '''
        if self.model:
            if self.oId:  
                return self.objects.save(self.model)
        else:
            return None
        
    def save(self):
        if self.model:
            if self.oId:
                return self.objects.save(self.model)

    def deleteById(self):
        if self.model:
            return self.objects.remove({'oId':self.oId})
        return None

    def getbyId(self):
        if self.model:
            result=copy.deepcopy(self)
            if result:
                oResult=self.objects.findOne({'oId':self.oId})
                if oResult:
                    result.model=oResult
                    return result
                return None
        return None

    def getByfield(self, field_name):
        if field_name:
            return self.objects.findOne({field_name: self.model[field_name]})
        return None

    def UpdateById(self):
        if self.oId:
            self.objects.update({'oId':self.oId}, self.model)
            return self
        else:
            return None
            
    def update(self):
        if self.oId:
            self.objects.update(self.model,**{"oId":self.model['oId']})
            return self
        else:
            return None

    def getOneByQuery(self, query):
        if self.model:
            result=copy.deepcopy(self)
            if result:
                oResult=self.objects.findOne(query)
                if oResult:
                    result.model=oResult
                    return result
        return None