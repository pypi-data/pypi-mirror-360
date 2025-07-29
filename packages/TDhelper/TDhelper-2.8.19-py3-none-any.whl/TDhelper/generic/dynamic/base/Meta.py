from types import FunctionType, MethodType

class Meta(type):
    class FunctionOverride:
        def __init__(self,cls_name,fn_name,fn):
            self.__cls_name__=cls_name
            self.__name__=fn_name
            self.__fn__= fn
        
        def __call__(self,*args, **kwargs):
            return self.__fn__(self.__cls_name__,self.__name__,*args,**kwargs)
    
    def __new__(cls, name, bases, dct):
        attrs = {
            "__name__":name,
            "__context__":{} if '__context__' not in dct else dct['__context__'],
            "__dynamic_methods__":[],
            "__set_hook__":cls.__set_hook_method__,
            "__hook_method__":dct["__hook_method__"] if '__hook_method__' in dct else None,
            "FunctionOverride":cls.FunctionOverride
        }      
        for key, value in dct.items():
            if key != "__construct__" and key != "__dynamic_methods__" and key!="__hook_method__":
                    attrs[key]=value
            '''
            if key not in attrs:
                if key != "__construct__":
                    attrs[key]=value
            '''
            if key=="__construct__":
                if '__hook_method__' in dct:
                    attrs["__hook_method__"]=dct["__hook_method__"]
                    if value:
                        for o in bases:
                            if(isinstance(o,Meta)):
                                o.Meta.__construct__= value
                                for item in o.Meta.__construct__:
                                    for k,v in item.items():
                                        attrs[k]=type(k,(dynamic_creator,),{"__dynamic_methods__":v,        "__hook_method__":attrs['__hook_method__']})()
                else:
                    raise(Exception("missing field '__hook_method__'."))
            if key=="__dynamic_methods__":
                for item in value:
                    attrs["__dynamic_methods__"].append(item)
                    attrs[item]= cls.FunctionOverride(name,item,attrs["__hook_method__"])
        return super(Meta,cls).__new__(cls, name, bases, attrs)

    def __set_hook_method__(self,fn):
        if fn:
            self.__hook_method__= fn
            for k in self.__dynamic_methods__:
                self.__dict__[k]=self.FunctionOverride(self.__name__,k,fn)

class dynamic_creator(metaclass=Meta):
    __self_handle__= lambda o: o,
    __get_method_handle__= lambda o,k: getattr(o,k) if hasattr(o,k) else None
    __has_method__=lambda o,k: True if o.__dynamic_methods__.__contains__(k) else False
    def __init__(self,fn=None):
        self.__set_hook__(fn)
        super(dynamic_creator,self).__init__()
        
    class Meta:
        __name__=None
        __construct__=None
        __hook_method__=None