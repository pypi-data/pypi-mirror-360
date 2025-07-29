from TDhelper.network.rpc.Generic.Host import HostManager
from TDhelper.Decorators.log import logging, logging_setup

class attribute_override:
        def __init__(self, name):
            self.__name__ = name

        def __set__(self, instance, v):
            if isinstance(instance.__rpc_server_cnf__,dict):
                if isinstance(v, str):
                    instance.__rpc_server_cnf__[self.__name__] = v.strip('/')
                else:
                    raise Exception("%s uri must str type." % self.__name__)
            else:
                raise Exception("rpc server config must dict. checked init method parameter server_cnf.")

        def __get__(self, instance, owen):
            if isinstance(instance.__rpc_server_cnf__,dict):
                if self.__name__ in instance.__rpc_server_cnf__:
                    return instance.__rpc_server_cnf__[self.__name__].strip('/')+"/"
                else:
                    raise Exception("rpc server config not found %s."%self.__name__)
            else:
                raise Exception("rpc server config must dict. checked init method parameter server_cnf.")

        def __delete__(self, instance):
            instance.__rpc_server_cnf__.pop(self._name)

class Meta(type):
    def __new__(cls, name, bases, dct):
        attrs={
            "__host__": HostManager(),
            "__RPC_SERVICES__":None,
            "__RPC_CNF__":None,
            "__ENCODING__":"utf-8",
            "__headers__":{},
            "__logger_hander__":logging,
            "__rpc_server_cnf__":{},
            "__service_register_uri__":attribute_override("service"),
            "__host_register_uri__":attribute_override("host"),
            "__method_register_uri__":attribute_override("method"),
            "__params_register_uri__":attribute_override("params"),
            "__return_register_uri__":attribute_override("return"),
            "__return_desc_register_uri__":attribute_override("return_desc")
        }
        for k,v in dct.items():
            if k not in attrs:
                attrs[k]=v
        return super(Meta,cls).__new__(cls,name,bases,attrs)


