#! python 3.6

#########################################################
# | @File    :   Service.py
# | @ClsName :   Service
# | @Version :   1.0.0
# | @History :

# you can input 'p-history-table' to insert a history record.
# |----------------------------------------------------------------------------------------------------------|
# | version       | Type                | Author        | Contact                     | Time                 |
# |----------------------------------------------------------------------------------------------------------|
# | 1.0.0         | Create              | Tony.Don      | yeihizhi@163.com            | 2022-09-29 09:27:43  |
# |----------------------------------------------------------------------------------------------------------|
# | @License :   Apache 2.0
# | @Desc    :   RPC server service.
#########################################################

# import lib by pypi

from copy import deepcopy
import json
import logging
from TDhelper.generic.dictHelper import findInDict, createDictbyStr
from TDhelper.network.rpc.Generic.Host import HostManager
from TDhelper.network.http.REST_HTTP import GET, POST, PUT, DELETE, ContentType
# import lib by project
# code start


class override_Attribute:

    def __init__(self, name, map=None):
        self.__name__ = name
        if map:
            self.__name__ = map+"."+self.__name__

    def __set__(self, instance, v):
        createDictbyStr(self.__name__, instance.__dict__, v)

    def __get__(self, instance, owen):
        try:
            return findInDict(self.__name__, instance.__dict__)
        except Exception as e:
            return None

    def __delete__(self, instance):
        name = self.__name__.split('.')
        name = name[len(name)-1]
        instance.__dict__[self.__map__].pop(name)


class Service:
    __cache__ = None
    __conf__ = None
    __logger_hander__ = None
    __ENCODING__ = "UTF-8"
    __HEADERS__ = {}
    __HOST__ = HostManager()
    __USR_ENCODING__ = override_Attribute('encoding', "__conf__")
    __HOST_CONF__ = override_Attribute('hosts', "__conf__")
    __TOKEN_KEY__ = override_Attribute('token_key', "__conf__")
    __SECRET__ = override_Attribute('secret', "__conf__")
    __SERVICE_PATH__ = override_Attribute('uris.service', '__conf__')
    __METHOD_PATH__ = override_Attribute('uris.method', '__conf__')
    __HOST_PATH__ = override_Attribute('uris.host', '__conf__')
    __PARAMS_PATH__ = override_Attribute("uris.param", '__conf__')
    __RETURN_PATH__ = override_Attribute('uris.return', '__conf__')
    __RETURN_DESC_PATH__ = override_Attribute("uris.return_desc", '__conf__')

    def __init__(self, conf, cache_handle={}, logger=None) -> None:
        self.__cache__ = cache_handle
        self.__conf__ = conf
        self.__HEADERS__ = {
            self.__TOKEN_KEY__: self.__SECRET__
        }
        if self.__USR_ENCODING__:
            self.__ENCODING__ = self.__USR_ENCODING__
        self.__logger_hander__ = logger if logger else logging
        offset = 0
        for item in self.__HOST_CONF__:
            self.__HOST__.register(
                serverId=offset, host=item['host'], port=80 if 'port' not in item else item['port'], proto=item['protocol'], status=True)
            offset += 1

    def getService(self, key):
        return self.__get_service__(key)

    def __get_service__(self, key=None):
        if key not in self.__cache__:
            post_data={"key":key} if key else b''
            self.__HOST__.getHost()
            statu, body = self.__remote__(self.__get_uri__(self.__SERVICE_PATH__),post_data,deepcopy(self.__HEADERS__))
            if statu:
                body= json.loads(body)
                if body["state"]==200:
                    for k,v in body["msg"].items():
                        body["msg"][k]["hosts"]=self.__get_host__(v["id"])
                        body["msg"][k]["methods"]=self.__get_method__(v["id"])
                        self.__cache__[k]=v
        if key:
            if key in self.__cache__:
                return self.__cache__[key]
        else:
            return self.__cache__

    def __get_host__(self,s_id):
        get_data={"s_id":s_id}
        state,body=self.__remote__(self.__get_uri__(self.__HOST_PATH__),get_data,deepcopy(self.__HEADERS__))
        if state:
            body= json.loads(body)
            if body["state"]==200:
                return body['msg']
            else:
                return []
        else:
            return []

    def __get_method__(self,s_id,key=None):
        get_data= {"s_id":s_id}
        if key:
            get_data['key']=key
        state,body=self.__remote__(self.__get_uri__(self.__METHOD_PATH__),get_data,deepcopy(self.__HEADERS__))
        if state:
            body= json.loads(body)
            if body["state"]==200:
                for item in body['msg']:
                    for k,v in item.items():
                        item[k]['params']=self.__get_method_params__(v['id'])
                        item[k]['returns']=self.__get_return__(v['id'])
                return body['msg']
            else:
                return []
        else:
            return []

    def __get_method_params__(self,m_id):
        get_data={"m_id":m_id}
        state,body=self.__remote__(self.__get_uri__(self.__PARAMS_PATH__),get_data,deepcopy(self.__HEADERS__))
        if state:
            body=json.loads(body)
            if body["state"]==200:
                return body["msg"]
            else:
                return []
        else:
            return []

    def __get_return__(self,m_id):
        get_data={"m_id":m_id}
        state,body= self.__remote__(self.__get_uri__(self.__RETURN_PATH__),get_data,deepcopy(self.__HEADERS__))
        if state:
            body= json.loads(body)
            if body["state"]==200:
                body['msg']['descriptions']= self.__get_return_desc__(body['msg']['id'])
                return body['msg']
            else:
                return {}
        else:
            return {}
    
    def __get_return_desc__(self,r_id):
        get_data={"r_id":r_id}
        state,body=self.__remote__(self.__get_uri__(self.__RETURN_DESC_PATH__),get_data,deepcopy(self.__HEADERS__))
        if state:
            body= json.loads(body)
            if body["state"]==200:
                return body['msg']
            else:
                return []
        else:
            return []

    def __get_uri__(self, uri):
        uri = uri.strip('/')
        return ''.join([self.__HOST__.__generateHost__(self.__HOST__.getHost()), "/", uri, "/"])

    def __remote__(self, uri, data=b"", headers={}):
        try:
            state, res = GET(uri, post_data=data,
                             http_headers=headers, content_type=ContentType.JSON, time_out=5)
            if state == 200:
                return True, str(res, self.__ENCODING__)
            else:
                self.__logger_hander__.error(
                    "Access('%s'), HTTP CODE: %s" % (uri, state))
                return False, state
        except Exception as e:
            self.__logger_hander__.error(e.args)
            return False, state


if __name__ == "__main__":
    cc = Service({
        "encoding": "utf-8",
        "token_key": "api-token",
        "secret": "d74218cff240f446d341c4a2f3a8c588",
        "hosts": [
            {
                "host": "192.168.50.2",
                "port": "10001",
                "protocol": "http://"
            }
        ],
        "uris": {
            "service": "api/rpcb/",
            "method": "api/rpc_method/",
            "host": "api/rpc_host/",
            "param": "api/rpc_method_params/",
            "return": "api/rpc_return/",
            "return_desc": "api/rpc_return_desc/"
        }
    })
    print(cc.__get_service__())
    print("gg")