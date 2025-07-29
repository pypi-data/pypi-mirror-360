import logging
import json
import time
from TDhelper.network.http.REST_HTTP import GET
from TDhelper.generic.dynamic.base.Meta import dynamic_creator
from TDhelper.network.rpc.Core.struct import RPC_SERVICE
from TDhelper.Decorators.log import logging, logging_setup
from TDhelper.Decorators.performance import performance
from TDhelper.network.rpc.Core.token import token_manage
performance.on_off(True)

class client():
    __TOKEN_KEY__ = "api-token"
    __LOGGER__ = logging
    __source_service__= ""
    __service_exists__= lambda o,k: True if k in o.__dict__ else False
    __get_service__= lambda o,k: getattr(o,k) if o.__service_exists__(k) else None
    __token_manage:token_manage= None
    __call_time_out=2
    @performance.performance_testing
    def __init__(self,source_service, uri, path: str = "", service_conf: dict = {}, sniffer: str = "api/sniffer", services: list = [], token_key=None, logger: dict = None, try_count:int=5, try_sleep:int=3, call_time_out=2)->None:
        '''rpc client.
        
        params:
            source_service - <class:string>: source service key.
            uri - <class: string>: rpc gateway;
            
            path - <class: str>: rpc init url path;
            
            service_conf - <class: dict>: {"service_key":"","secret":""};
            
            sniffer - <class: str>: rpc service sniffer path, get it with operator;
            
            services - <class: list>: get rpc service by service list, default all, default all; 
            
            token_key - <class: string>: key field  for rpc authorized. it is request headers field; validate in SAAS-CLI framework core.filter.access.py;
            
            logger - <class: dict>: logger configure dict;
            
            try_count - <class:int>: max count for service available sniffer, default 5;
            
            try_sleep -<class: int>: service available sniffer retry sleep time, default 3 second;
            
            call_time_out - <class:int> remote call time out, default 2 second; 
        '''
        if logger:
            self.__LOGGER__.basicConfig(level=logging.INFO)
            self.__LOGGER__.config.dictConfig(logger)
        self.__source_service__= source_service
        self.__TOKEN_KEY__ = token_key if token_key else self.__TOKEN_KEY__
        self.__call_time_out= call_time_out
        header = {
            "access-source":"rpc"
        }
        service_conf['uri']=uri

        self.__token_manage= token_manage(
                token_uri= uri,
                svr_key=service_conf.get("service_key",""),
                secret=service_conf.get("secret",""),
                call_svr_key= self.__source_service__
            )
        if self.__token_manage.Status:
            try:
                header.update({self.__TOKEN_KEY__:self.__token_manage.Token})
            except Exception as e:
                raise Exception("rpc generate token error.%s"%self.__token_manage.ErrMsg)
        else:
            raise Exception(self.__token_manage.ErrMsg)
        uri = uri.rstrip("/")
        rpc_uri ="/".join([uri,path.lstrip("/")])
        if services:
            rpc_uri += "?key="+",".join(services)
        rpc_server_state = False
        for v in range(0, try_count):
            body = self.__get_conf__("/".join([uri,sniffer.lstrip("/")]), header)
            if body:
                if body['state'] == 200:
                    rpc_server_state = True
                    break
            time.sleep(try_sleep)
        if not rpc_server_state:
            raise Exception("rpc server(%s) can not access ." % uri)
        self.__context__ = self.__get_conf__(rpc_uri, header)
        if self.__context__:
            if self.__context__["state"]==200:
                if self.__context__["msg"]:
                    self.__dict__["__srv_struct__"] = {}
                    for k, v in self.__context__["msg"].items():
                        self.__dict__["__srv_struct__"][k] = type(
                            k, (RPC_SERVICE,), {}).create_by_cnf(v, self.__TOKEN_KEY__, service_conf ,self.__call_time_out)
                        methods = [kv for kv in v['methods'].keys()]
                        self.__dict__[k] = type(k, (dynamic_creator,), {
                                                "__dynamic_methods__": methods, "__hook_method__": self.__call__})()
                else:
                    self.__LOGGER__.error("not found rpc method.%s"%self.__context__["msg"])
                    raise Exception("not found rpc method.%s"%self.__context__["msg"])
            else:
                err_str= ",".join(["rpc service has an error: %s"%self.__context__["msg"],"access uri(%s)"%rpc_uri,"head(%s)"%json.dumps(header)])
                raise Exception(err_str)
        else:
            raise Exception("not found rpc instance config.")
        super(client, self).__init__()
    
    @performance.performance_testing
    def __call__(self, service_name, fun_name, *args, **kwargs):
        remote_func_name = ("".join([service_name, '.', fun_name]))
        if 'headers' in kwargs:
            kwargs["headers"].update({"call_service":self.__source_service__})
        else:
            kwargs["headers"]={"call_service":self.__source_service__}
        ''' api trace.
        if "headers" in kwargs:
            kwargs["headers"].update({"trace_id":"","request_id":""})
        else:
            kwargs["headers"]={"trace_id":"","request_id":""}   
        '''
        if service_name in self.__srv_struct__:
            if hasattr(self.__srv_struct__[service_name], 'methods'):
                if fun_name in self.__srv_struct__[service_name].methods:
                    self.__LOGGER__.info("call %s, args:(%s),kwargs:(%s)"%(remote_func_name,",".join(args),str(kwargs)))
                    try:
                        start = time.clock_gettime(0)
                        result = self.__srv_struct__[service_name].__remote_call__(
                            fun_name, *args, **kwargs)
                        end = time.clock_gettime(0)
                        self.__LOGGER__.info("call %s, time consuming %f(s)" % (
                            remote_func_name, (end-start)))
                        return result
                    except Exception as e:
                        self.__LOGGER__.error(e)
                else:
                    self.__LOGGER__.error(
                        "in service(%s) not found method(%s)", (service_name, fun_name))
            else:
                self.__LOGGER__.error("service obj not found key(methods).")
        else:
            self.__LOGGER__.error('not found service(%s).' % service_name)
        return {"state": -1, "msg": {}}

    def __get_conf__(self, uri, header={}):
        state, body = GET(uri, http_headers=header,
                          time_out=5, charset="utf-8")
        if state == 200:
            body = json.loads(body)
            return body
        return {
            "state": state,
            "msg":body
        }
    
    def reload(self):
        pass
    
    def monitor(self,speed=None):
        '''
            start monitor service health.
            
            Args:
            
                speed: <cls,int>, monitor speed. seconds.
        '''
        if self.__srv_struct__:
            for o in self.__srv_struct__:
                self.__srv_struct__[o].monitor(speed)
                
    def stop_monitor(self):
        '''
            stop monitor service health.
        '''
        if self.__srv_struct__:
            for o in self.__srv_struct__:
                self.__srv_struct__[o].stop_monitor()
