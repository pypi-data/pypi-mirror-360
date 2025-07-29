import json
import logging
import html
from random import Random
from TDhelper.network.rpc.Generic.Host import HostManager
from network.http.REST_HTTP import GET, POST, PUT, DELETE, ContentType


def get_key(key, cnf):
    return cnf[key] if key in cnf else None


class RPC_Returns_description:
    returns: int = None
    key: str = None
    valueDescription: str = None

    def __init__(self, k, v_desc):
        self.key = k
        self.valueDescription = v_desc

    def toCnf(self):
        return json.dumps({
            "returns": self.returns,
            "key": self.key,
            "valueDescription": self.valueDescription
        })

    @classmethod
    def create_by_cnf(self, cnf):
        if isinstance(cnf, str):
            try:
                cnf = json.loads(cnf)
            except Exception as e:
                raise e
        results = []
        if cnf:
            for item in cnf:
                results.append(
                    RPC_Returns_description(
                        item["key"], item["valueDescription"])
                )
        return results


class RPC_Params:
    serviceUri: int = None
    key: str = None
    descripiton: str = None
    default = None

    def __init__(self, k, desc, defaultV):
        self.key = k
        self.descripiton = desc
        self.default = defaultV

    def toCnf(self):
        return json.dumps({
            "serviceUri": self.serviceUri,
            "key": self.key,
            "description": self.descripiton,
            "defaultValue": self.default
        })

    @classmethod
    def create_by_cnf(self, cnf):
        if isinstance(cnf, str):
            try:
                cnf = json.loads(cnf)
            except Exception as e:
                raise e
        results = []
        for item in cnf:
            results.append(
                RPC_Params(get_key('key', item),
                           get_key('description', item),
                           get_key('defaultVale', item)
                           )
            )
        return results


class RPC_Returns:
    serviceUri: int = None
    valueType: str = None
    examples: dict = None
    descriptions: '[RPC_Returns_description]' = []

    def __init__(self, vt, examp, desc):
        self.valueType = vt
        self.examples = examp
        self.descriptions = desc

    def toCnf(self):
        return json.dumps({
            "serviceUri": self.serviceUri,
            "valueType": self.valueType,
            "examples": self.examples
        })

    @classmethod
    def create_by_cnf(self, cnf):
        if isinstance(cnf, str):
            try:
                cnf = json.loads(cnf)
            except Exception as e:
                raise e

        return RPC_Returns(
            get_key("valueType", cnf),
            get_key("examples", cnf),
            RPC_Returns_description.create_by_cnf(get_key('descriptions', cnf))
        )


class RPC_Method:
    service: int = None
    name: str = None
    uri: str = None
    method: str = None
    version: str = None
    description: str = None
    params: '[RPC_Params]' = []
    returns: '[RPC_Returns]' = []

    def __init__(self, name, uri, method, version, description, params, returns, collect=None):
        self.name = name
        self.uri = uri
        self.method = method
        self.version = version
        self.description = description
        self.collect = collect
        self.params = params
        self.returns = returns

    def __get_method_type__(self, v: str):
        v = v.upper()
        if v == "GET":
            return 1
        elif v == "POST":
            return 2
        elif v == "PUT":
            return 3
        elif v == "DELETE":
            return 4
        else:
            raise "method type value must GET,POST,PUT,DELETE."

    def __transfer_method_type__(self, v: int):
        if v == 1:
            return "GET"
        elif v == 2:
            return "POST"
        elif v == 3:
            return "PUT"
        elif v == 4:
            return "DELETE"
        else:
            raise "method transer value must 1,2,3,4."

    def toCnf(self):
        return json.dumps(
            {
                "service": self.service,
                "key": self.name,
                "uri": self.uri,
                "method": self.__get_method_type__(self.method),
                "version": self.version,
                "description": self.description,
                "collect": self.collect
            }
        )

    @classmethod
    def create_by_cnf(self, name, key, cnf):
        if isinstance(cnf, str):
            try:
                cnf = json.loads(cnf)
            except Exception as e:
                raise e
        if 'collect' in cnf:
            m_collect= get_key('collect',cnf)
            if m_collect:
                if not key.upper().startswith(m_collect.upper()+"_"):
                    name = "".join(
                    [name, '.', get_key('collect', cnf).upper(), '_', key])
                else:
                    name = "".join(
                    [name, '.', key])
            else:
                name = "".join([name, '.', key])
        else:
            name = "".join([name, '.', key])
        return RPC_Method(
            name=name,
            uri=get_key('uri', cnf),
            method=get_key('method', cnf),
            version=get_key('version', cnf),
            description=get_key('description', cnf),
            params=RPC_Params.create_by_cnf(get_key('params', cnf)),
            returns=RPC_Returns.create_by_cnf(get_key("returns", cnf)),
            collect=get_key('collect', cnf)
        )


class RPC_SERVICE:
    __TOKEN_KEY__ = ""
    host = None
    name: str = None
    description: str = None
    key: str = None
    secret: str = None
    protocol: str = "http://"
    methods = {}
    __method_exists__= lambda o,k: True if k in o.__dict__ else False
    
    def __init__(self, name=None, description=None, key=None, secret=None, protocol=None, host_cnf=None, methods_cnf=None, token_key="api-token"):
        self.__TOKEN_KEY__ = token_key
        self.name = name
        self.description = description
        self.key = key
        self.secret = secret
        self.protocol = protocol
        self.host = HostManager()
        self.methods={}
        if host_cnf:
            for item in host_cnf:
                self.host.register(
                    get_key('serverId', item),
                    get_key("host", item),
                    int(get_key("port", item)),
                    get_key("sniffer", item),
                    protocol,
                    True
                )
        if methods_cnf:
            for k, v in methods_cnf.items():
                self.methods[k] = RPC_Method.create_by_cnf(
                    self.key.upper(), k.upper(), v)
            # self.methods = [RPC_Method.create_by_cnf(
            #    self.key.upper(), k.upper(), v) for k, v in methods_cnf.items()]
    def __get_token__():
        pass
    
    def toCnf(self):
        return json.dumps({
            "name": self.name,
            "description": self.description,
            "key": self.key.upper(),
            "accessSecret": self.secret,
            "protocol": self.protocol
        })

    def monitor(self,speed=None):
        self.host.__start_state_monitor__(speed)
        
    def stop_monitor(self):
        self.host.__stop_state_monitor__()
    
    def __hit_method__(self, key):
        if key in self.methods:
            return self.methods[key]
        else:
            raise Exception("can not found method(%s)." % key)

    def __remote_call__(self, func_name, *args, **kwargs):
        logging.info("remote call %s.%s" % (self.key, func_name))
        method = self.__hit_method__(func_name)
        m_uri,serverId = self.__genrate_method_uri__(func_name)
        if not m_uri:
            return {"state": -1, "msg": "%s not found remote uri." % self.__name__+func_name}
        try:
            header, data, kwargs = self.__genrate_params__(
                method, *args, **kwargs)
        except Exception as e:
            return {"state": -1, "msg": e.args}
        if m_uri.__contains__("{pk}"):
            if 'pk' in kwargs:
                m_uri = m_uri.replace("{pk}", kwargs['pk'])
            else:
                if 'pk' in data:
                    m_uri = m_uri.replace("{pk}", data['pk'])
                else:
                    if 'pk' in header:
                        m_uri = m_uri.replace("{pk}", header['PK'])
                    else:
                        return {"state": -1, "msg": "miss param 'pk'."}
        return self.__call__(m_uri, method.method, header, **kwargs)

    def __call__(self, uri, method_type: str, http_headers={}, **kwargs):
        state = -1
        ret = ""
        if method_type.upper() == "GET":
            logging.info("access api:(%s), method(%s)." % (uri, method_type))
            state, ret = GET(uri=uri,
                             post_data=kwargs,
                             http_headers=http_headers,
                             time_out=15)
        elif method_type.upper() == "POST":
            logging.info("access api:(%s), method(%s), postdata:%s." %
                         (uri, method_type, kwargs))
            state, ret = POST(
                uri,
                kwargs["data"] if "data" in kwargs else None,
                content_type=ContentType.JSON,
                http_headers=http_headers,
                time_out=15,
            )
        elif method_type.upper() == "PUT":
            logging.info("access api:(%s), method(%s),postdata:%s." %
                         (uri, method_type, kwargs))
            # 还没有写PUT方法
            raise Exception("urllib PUT方法还没写.")
        elif method_type.upper() == "DELETE":
            # 还没有写DELETE方法
            logging.info("access api:(%s), method(%s)" %
                         (uri, method_type))
            if "data" in kwargs:
                state, ret = DELETE(
                    uri,
                    post_data=kwargs["data"],
                    http_headers=method_type,
                    content_type=ContentType.JSON,
                    time_out=15,
                )
            else:
                state, ret = DELETE(uri=uri,
                                    http_headers=method_type,
                                    time_out=15)
        else:
            return {"state": -1, "msg": "uri(%s),method type %s error." % (uri, method_type)}
        if state == 200:
            try:
                ret = json.loads(str(ret, encoding="utf-8"))
                return {"state": ret["state"], "msg": ret["msg"]}
            except Exception as e:
                logging.error(e.args)
                return {
                    "state":
                    state,
                    "msg":
                    'remote call "%s" error.(%s)' %
                    (uri, e.args),
                }
        else:
            try:
                if ret:
                    if isinstance(ret,str):
                        ret = ret
                        return {
                            "state": state,
                            "msg": ret
                        } 
                    elif isinstance(ret,dict):
                        ret = json.loads(str(ret, encoding="utf-8"))
                        return {
                            "state": ret["state"],
                            "msg": ret["msg"]
                        }
                else:
                    return {"state": state, "msg": "%s" % uri}
            except Exception as e:
                return {
                    "state":
                    state,
                    "msg":
                    'remote call "%s" error.(%s)' %
                    (uri, e.args),
                }

    def __genrate_params__(self, method, *args, **kwargs):
        try:
            data = {}
            m_headers = {}
            if "headers" in kwargs:
                if isinstance(kwargs["headers"], dict):
                    for o in kwargs["headers"]:
                        m_key=o.lower().replace('-',"_").replace("http_", "").replace("header_","").replace(
                            "_", "-")
                        m_headers[m_key] = kwargs["headers"][o]
                else:
                    return {
                        "state": -1,
                        "msg": "http request headers must is dict type.",
                    }
            if "access-source" not in m_headers:
                m_headers.update({"access-source":"rpc"})
            if self.__TOKEN_KEY__ not in m_headers:
                m_headers[self.__TOKEN_KEY__] = self.secret
            for item in method.params:
                if item.key.lower().startswith("http_header_"):
                    if item.key.lower().replace("http_header_", "").replace("_", "-") not in m_headers:
                        logging.info(item.key)
                        logging.info(kwargs)
                        if item.key in kwargs:
                            m_headers[item.key.lower().replace(
                                "http_header_", "").replace("_", "-")] = kwargs[item.key]
                            del kwargs[item.key]
                        else:
                            if item.default:
                                m_headers[item.upper.replace("HTTP_HEADER_", "").replace(
                                    "http_header_", "").replace("_", "-")] = item.default
                            else:
                                raise Exception(
                                    "not found http header key(%s)" % item.key)
                elif item.key.lower().startswith("http_data_"):
                    if "data" not in kwargs:
                        kwargs["data"] = {}
                    if (item.key.replace("http_data_", "") not in kwargs["data"]):
                        if item.key in kwargs:
                            kwargs["data"][item.key.replace(
                                "http_data_",
                                "")] = kwargs[item.key]
                            del kwargs[item.key]
                        else:
                            if item.default:
                                kwargs["data"][item.key.replace(
                                    "http_data_",
                                    "")] = item.default
                            else:
                                kwargs["data"][item.key.replace(
                                    "http_data_", "")] = None
                else:
                    if item.key in kwargs:
                        data[item.key] = html.escape(kwargs[item.key]) if isinstance(
                            kwargs[item.key], str) else kwargs[item.key]
                    else:
                        if item.default:
                            data[item.key] = html.escape(item.default) if isinstance(
                                item.default, str) else item.default
                        else:
                            raise Exception("not found params(%s)" % item.key)
            return m_headers, data, kwargs
        except Exception as e:
            logging.error(e)
            raise Exception(e)

    def __genrate_method_uri__(self, key):
        try:
            host_conf=self.host.getHost()
            host = self.host.__generateHost__(host_conf).strip('/')
            uri = self.__hit_method__(key).uri.strip('/')
            return "".join([host, '/', uri, '/']),host_conf["serverId"]
        except Exception as e:
            logging.error(e)
            return None

    @classmethod
    def create_by_cnf(self, cnf,token_key="api-token"):
        if isinstance(cnf, str):
            try:
                cnf = json.loads(cnf)
            except Exception as e:
                raise e
        return RPC_SERVICE(
            name=get_key('name', cnf),
            description=get_key('description', cnf),
            key=get_key('key', cnf).upper(),
            secret=get_key('secret', cnf),
            protocol=get_key('protocol', cnf),
            host_cnf=get_key('hosts', cnf),
            methods_cnf=get_key('methods', cnf),
            token_key=token_key
        )


class RPC_SERVICE_CONF:
    uris: list = []
    token: str = None

    def __init__(self, uris, token):
        self.uris = uris
        self.token = token
        for offset in range(0, len(self.uris)):
            self.uris[offset] = self.uris[offset].strip("/")

    def getUri(self):
        offset = len(self.uris)-1
        if offset > 0:
            return self.uris[Random.randint(0, offset-1)]+"/"
        elif offset == 0:
            return self.uris[0]+"/"
        else:
            raise Exception("RPC server config has error, uri is none.")
