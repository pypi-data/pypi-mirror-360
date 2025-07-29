import logging
import html
from types import FunctionType
from TDhelper.cache.memcache import cache

class RPC_Server:
    __logger__ = logging
    __logic__= None
    def __init__(self, logic:FunctionType=None ,logger_handle=None):
        self.__logger__ = logger_handle if logger_handle else self.__logger__
        self.__logic__= logic
        if self.__logic__:
            self.__logic__(self)
        
    def __reload__(self):
        cache.__clear__()
        if self.__logic__:
            self.__logic__(self)
        else:
            self.__logger__.error("logic is none.")
                
    def __insert__(self, k, v):
        try:
            cache.insert(k, v)
        except Exception as e:
            self.__logger__.error(e)

    def __append__(self, k, v):
        try:
            cache.append(k, v)
        except Exception as e:
            self.__logger__.error(e)

    def __set__(self, k, v):
        try:
            cache.update(k, v)
        except Exception as e:
            self.__logger__.error(e)

    def __get__(self, k=None):
        try:
            if k:
                return cache.findValue(k)
            else:
                return cache.__get__()
        except Exception as e:
            self.__logger__.error(e)

    def __delete__(self, k):
        try:
            cache.destory(k)
        except Exception as e:
            self.__logger__.error(k)

    def __clear__(self):
        cache.__clear__()
    
    def __transfer_method_type__(self,v:int):
        if v==1:
            return "GET"
        elif v==2:
            return "POST"
        elif v==3:
            return "PUT"
        elif v==4:
            return "DELETE"
        else:
            raise "method transfer value must 1,2,3,4."
    
    def add_service(self, k, n, d, s, p):
        """add service
            add new service
        Parameters:
            k - <class:string>, service key.
            n - <class:string>, service name.
            d - <class:string>, service description.
            s - <class:stirng>, service secret.
            p - <class:string>, service protocol
        Returns:
             None
        Raises:
             None
        """
        cnf = {
            "key": k,
            "name": n,
            "description": d,
            "secret": s,
            "protocol": p,
            "hosts": [],
            "methods": {}
        }
        self.__insert__(k, cnf)

    def add_host(self, service, serverId, host, port, state, proto):
        cnf = {
            "serverId": serverId,
            "host": host,
            "port": port,
            "state": state,
            "proto": proto
        }
        cache.findInstance("".join([service,'.hosts'])).append(cnf)

    def add_method(self, service,key,uri,method,version,description="",collect=''):
        key= key.split('.')
        if len(key)>1:
            key=key[1]
        else:
            key=key[0]
        cnf = {
            "collect": collect.upper() if collect else collect,
            "key": key.upper() if key else key,
            "uri": uri,
            "method": self.__transfer_method_type__(method),
            "version": version,
            "description": description,
            "params": [],
            "returns": {}
        }
        cache.insert("".join([service, ".methods.",key]),cnf)
        
    def add_param(self,service,method,key,desc,defaultValue=None):
        cnf={
                    "key": key,
                    "description": desc,
                    "defaultValue":defaultValue
            }
        cache.findInstance("".join([service,".methods.",method,".params"])).append(cnf)

    def add_return(self,service,method,v_type,examples):
        cnf={
                "valueType": v_type,
                "examples": html.unescape(examples),
                "descriptions": []
            }
        cache.update("".join([service,".methods.",method,".returns"]),cnf)
        
    def add_return_desc(self,service,method,key,desc):
        cnf={
                "key": key,
                "valueDescription": desc
            }
        cache.findInstance("".join([service,".methods.",method,".returns",".descriptions"])).append(cnf)