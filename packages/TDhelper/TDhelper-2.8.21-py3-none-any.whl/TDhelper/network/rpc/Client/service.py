from types import FunctionType
from copy import copy
import os
import logging
from TDhelper.generic.requier import R as require
from TDhelper.generic.classDocCfg import doc
from TDhelper.network.rpc.Core.Meta import Meta
from TDhelper.network.rpc.Core.struct import *
from TDhelper.network.rpc.Core.token import token_manage
from TDhelper.network.http.REST_HTTP import GET, POST, PUT, DELETE, ContentType

# 反射获取类
def reflectClass(cls):
    return require(cls).getType()

class SRC(metaclass=Meta):
    """SRC
        service register center interface.
    Parameters:
        uris - <class:list>, rpc server apis.
        server_cnf - <class:dict>, service conf.
        rpc_conf_header - <class:dict>, rpc configure general header struct. example :{
                    "name": "权限服务",
                    "description": "权限服务",
                    "key": "RPC_TEST",
                    "secret": "203920398409238408204324",
                    "protocol": "http://",
                    "hosts": [
                        {
                            "serverId": 1,
                            "host": "192.168.0.1",
                            "port": 8080,
                            "sniffer": "api/sniffer",
                            "proto": "http://"
                        }
                    ]
                } 
        logger - <class:logging>, log handle.
        **kwargs:
            token_key - <class:str>, access token key. it will auto assembly http header. default 'api-token'.
    Returns:
        None
    Raises:
        None
    """
    def __init__(self, uris: list, server_cnf: dict = None, rpc_conf_header:dict={}, logger: "logging" = None,**kwargs):
        self.__RPC_CNF__ = RPC_SERVICE_CONF(uris)
        self.__token_manage__= token_manage(
            self.__RPC_CNF__.getUri(),
            rpc_conf_header.get("key"),
            rpc_conf_header.get('secret'),
            path="api/regist_monent_token",
            post_data={
                "svr_key": rpc_conf_header.get("key")
            }
        )
        self.__logger_hander__ = logger if logger else self.__logger_hander__
        self.__rpc_server_cnf__ = server_cnf if server_cnf else self.__rpc_server_cnf__
        apiToken="api-token" if "token_key" not in kwargs else kwargs["token_key"]
        #self.__headers__[apiToken] = self.__token_manage__.Token#self.__RPC_CNF__.token
        self.__rpc_conf_header__= rpc_conf_header
        self.__headers__.update({apiToken:self.__token_manage__.Token})
        self.__headers__.update({"access-source":"service_regist"})
        self.__headers__.update({"svr-key":rpc_conf_header.get("key")})

    def __set_coding__(self, encoding='utf-8'):
        self.__ENCODING__ = encoding

    def __setting__(self, cnf):
        self.__rpc_server_cnf__ = cnf

    def AutoRegister(self,cxt:list,conf_header:dict= None):
        """AutoRegister
            Auto register service by method annotate.
        Parameters:
            cxt - <class:list>, want to auto register cls.
            conf_header - <class:dict>, override rpc configure general header struct.
        Returns:
            None
        Raises:
            None
        Example annotate:
            Conf In Annotate:
                [rpc]
                {
                    "uri": <class, str>,
                    "method": <class, enum(GET|POST|PUT|DELETE)>,
                    "version": <class, str(1.0.0)>,
                    "description": <class: str>,
                    "params": [
                        {
                            "key":<class, str>,
                            "description":<class, str>,
                            "defaultValue":<class, str>
                        }
                    ],
                    "returns":{
                        "valueType":"json",
                        "examples":<class, str>,
                        "descriptions":[
                            {
                                "key":<class, str>,
                                "valueDescription":<class, str>
                            }
                        ]
                    }
                }
                [rpcend]
            Conf In Json:
                [rpc]
                methods.fun1::test.json
                [rpcend]

                [rpc]
                fun1::test.json
                [rpcend]
        """
        conf= conf_header if conf_header else copy(self.__rpc_conf_header__)
        if not conf:
            raise Exception("configure header is none. see more in config/regist_conf/readme.md")
        if "methods" not in conf:
            conf['methods']={}
        for cxt_item in cxt:
            m_cxt= cxt_item
            if isinstance(cxt_item,str):
                m_cxt= reflectClass(cxt_item)
            for k, v in m_cxt.__dict__.items():
                if isinstance(v, FunctionType):
                    func_name = "".join([m_cxt.__name__,'_',v.__name__]).upper()
                    if v.__doc__:
                        methods = doc(v.__doc__, "rpc")
                        if methods:
                            methods = methods.replace("\n", "").strip()
                            try:
                                if func_name not in conf['methods']:
                                    conf['methods'][func_name]=json.loads(methods)#, encoding="utf-8")
                                    conf['methods'][func_name]["collect"]=m_cxt.__name__
                            except Exception as e:
                                raise e
        self.__register_by_cnf__(conf)
        return self
    
    def Register(self, cxt:"dict|str", filepath:bool=False, conf_header:dict=None):
        """Register
            register service by conf.
        Parameters:
            cxt - <class:dict|str>, conf json or conf file path.
            filepath - <class:bool>, control conf mode. default False use dict to register.
            conf_header - <class:dict>, override rpc configure general header struct.
        Returns:
            None
        Raises:
            None
        """
        conf= conf_header if conf_header else copy(self.__rpc_conf_header__)
        if not conf:
            raise Exception("configure header is none. see more in config/regist_conf/readme.md")
        
        if filepath:
            if os.path.exists(cxt):
                m_conf= self.__register_by_file__(cxt)
                if conf:
                    m_conf['name']=conf['name']
                    m_conf['description']=conf['description']
                    m_conf['key']=conf['key']
                    m_conf['secret']=conf['secret']
                    m_conf['protocol']=conf['protocol']
                    m_conf['hosts']=conf['hosts']
                if "methods" in m_conf:
                    conf.update(m_conf)
                else:
                    conf.update({"methods":m_conf})
                self.__register_by_cnf__(conf)
            else:
                raise Exception("can not found path '%s'" % cxt)
        else:
            if "methods" in cxt:
                if "methods" in cxt:
                    conf.update(cxt)
                else:
                    conf.update({"methods":cxt})
            self.__register_by_cnf__(conf)
        return self

    def __register_by_file__(self, filepath):
        m_json_source = None
        filepath = filepath.replace("\\", "/")
        with open(filepath, mode='r', encoding=self.__ENCODING__) as f:
            m_json_source = f.read()
            f.close()
        return json.loads(m_json_source)

    def __register_by_cnf__(self, cnf: "dict|str"):
        if isinstance(cnf, str):
            cnf = json.loads(cnf)
        self.__analysis_cnf__(cnf)

    def __register_service__(self):
        uri = "".join([self.__RPC_CNF__.getUri(),
                      self.__service_register_uri__])
        state, res = self.__remote__(
            uri, self.__RPC_SERVICES__.toCnf(), copy(self.__headers__))
        if state:
            res = json.loads(res)
            if res["state"] == 200:
                self.__logger_hander__.info("service(%s) register success."%res['msg']['name'])
                s_id = res["msg"]["id"]
                self.__register_host__(s_id)
                self.__register_method__(s_id)
            else:
                self.__logger_hander__.error(
                    "Access(%s), '%s'" % (uri, res["msg"]))

    def __register_host__(self, parentId):
        uri = "".join([self.__RPC_CNF__.getUri(), self.__host_register_uri__])
        for v in self.__RPC_SERVICES__.host.__host__:
            host_cnf = self.__RPC_SERVICES__.host.get_host_by_key(v)
            data = {
                "host": host_cnf['host'],
                "port": host_cnf['port'],
                "state": True,
                "service": parentId,
                "sniffer":host_cnf['sniffer']
            }
            state, res = self.__remote__(uri, data, copy(self.__headers__))
            if state:
                res = json.loads(res)
                if res["state"] == 200:
                    self.__logger_hander__.info(
                        "register host '%s' success." % host_cnf['host'])
                else:
                    self.__logger_hander__.error(
                        "register host error(%s)" % res["msg"])

    def __register_method__(self, parentId):
        uri = "".join([self.__RPC_CNF__.getUri(),
                      self.__method_register_uri__])
        for k,v in self.__RPC_SERVICES__.methods.items():
            data = v
            data.service = parentId
            state, res = self.__remote__(
                uri, data.toCnf(), copy(self.__headers__))
            if state:
                res = json.loads(res)
                if res["state"] == 200:
                    self.__logger_hander__.info(
                        "register method '%s' success." % v.name)
                    m_id = res["msg"]["id"]
                    self.__register_parameters__(v, m_id)
                    self.__register_returns__(v, m_id)
                else:
                    self.__logger_hander__.error(
                        "register method '%s' error (%s)" % (v.name, res["msg"]))

    def __register_parameters__(self, method, parentId):
        uri = "".join([self.__RPC_CNF__.getUri(),
                      self.__params_register_uri__])
        for item in method.params:
            data = item
            data.serviceUri = parentId
            state, res = self.__remote__(
                uri, data.toCnf(), copy(self.__headers__))
            if state:
                res = json.loads(res)
                if res["state"] == 200:
                    self.__logger_hander__.info(
                        "register method paramete '%s' success." % item.key)
                else:
                    self.__logger_hander__.error(
                        "register method %s error(%s)." % (item.key, res["msg"]))

    def __register_returns__(self, method, parentId):
        uri = "".join([self.__RPC_CNF__.getUri(),
                      self.__return_register_uri__])
        data = method.returns
        data.serviceUri = parentId
        state, res = self.__remote__(uri, data.toCnf(), copy(self.__headers__))
        if state:
            res = json.loads(res)
            if res["state"] == 200:
                self.__logger_hander__.info("register method return success.")
                r_id = res["msg"]["id"]
                self.__register_return_desc__(data.descriptions, r_id)
            else:
                self.__logger_hander__.error(
                    "register method return error(%s)" % res["msg"])

    def __register_return_desc__(self, items, return_id):
        uri = "".join(
            [self.__RPC_CNF__.getUri(), self.__return_desc_register_uri__])
        for item in items:
            data = item
            data.returns = return_id
            state, res = self.__remote__(
                uri, data.toCnf(), copy(self.__headers__))
            if state:
                res = json.loads(res)
                if res["state"] == 200:
                    self.__logger_hander__.info(
                        "register method return description '%s' success." % item.key)
                else:
                    self.__logger_hander__.error(
                        "register method return description '%s' error(%s)", (item.key, res["msg"]))

    def __analysis_cnf__(self, cnf):
        assert isinstance(cnf, dict), "cnf must dict types."
        try:
            self.__RPC_SERVICES__ = RPC_SERVICE.create_by_cnf(cnf)
            if self.__RPC_SERVICES__:
                self.__register_service__()
            else:
                raise Exception("RPC services create error.")
        except Exception as e:
            raise e

    def __sniffer__(self):
        return True, self.__rpc_server_cnf__["key"]

    def __remote__(self, uri, data=b"", headers={}):
        try:
            state, res = POST(uri, post_data=data,
                              http_headers=headers, content_type=ContentType.JSON, time_out=5)
            if state == 200:
                return True, str(res, self.__ENCODING__)
            else:
                self.__logger_hander__.error(
                    "Access('%s'), HTTP CODE: %s" % (uri, state))
                return False, None
        except Exception as e:
            self.__logger_hander__.error(e.args)
            return False, None