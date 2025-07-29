#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo
from urllib.parse import quote_plus
'''
class\r\n
    lib.db.mongodb.mongodbclient\r\n
description\r\n
    Mongodb database helper class\r\n
'''
connect_conf={
    "host":"",
    "port":0,
    "db":"",
    "usr":"",
    "pw":""
}

def setConf(host:str,port:int,db:str,usr:str="",pw:str=""):
    connect_conf["host"]= host
    connect_conf["port"]= port
    connect_conf["db"]= db
    connect_conf["usr"]= usr if usr else ""
    connect_conf["pw"]= pw if pw else ""

class mongo_connector:
    __client__= None
    __db__= None
    __db_name__=""
    __url__= ""
    def __init__(self, conf:dict):
        if conf["usr"] and conf["pw"]:
            self.__url__= "mongodb://%s:%s@%s:%d" % (conf["usr"],conf["pw"],conf["host"],conf["port"])
        else:
            self.__url__= "mongodb://%s:%d" % (conf["host"],conf["port"])
        if self.__url__:
            self.__db_name__= conf["db"]
            self.__client__=pymongo.MongoClient(self.__url__,connect=False)
            self.__db__= self.__client__[conf["db"]]
        else:
            raise Exception("mongodb url is none.")
        
    def __get_new_client__(self):
        if self.__url__:
            return pymongo.MongoClient(self.__url__)[self.__db_name__]
        else:
            raise Exception("mongodb url is none.")
