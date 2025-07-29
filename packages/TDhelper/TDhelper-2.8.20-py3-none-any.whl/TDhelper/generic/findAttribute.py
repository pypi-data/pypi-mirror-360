def findAttr(query_template,*args,**kwargs):
    '''findAttr
        Args:
        
            query_template: find query;
            
                {
                    "key1":"args.0.b.ccd",
                    "key4":"args.0.a",
                    "key2":"kwargs.r.r1",
                    "key3":"kwargs.r2"
                }
            
            *args: params tuple.
            **kwargs: params dict.
        
        Return:

            query_template format.
    '''
    try:
        for k,v in query_template.items():
            _t= v.split(".")
            if _t[0].lower()=="args":
                o=args[int(_t[1])]
                for r in range(2,len(_t)):
                    o= findV(o,_t[r])
                query_template[k]=o
            elif _t[0].lower()=="kwargs":
                o=kwargs
                for r in range(1,len(_t)):
                    o= findV(o,_t[r])
                query_template[k]=o
            else:
                raise Exception("query_template key '%s' must set args or kwargs."%k)
    except Exception as e:
        raise e
    return query_template

def findV(o,k):
    if isinstance(o,dict):
        if k in o:
            return o[k]
        else:
            raise Exception("not found %s"%k)
    elif isinstance(o,object):
        if hasattr(o,k):
            return o.__getattribute__(k)
        else:
            raise Exception("not found %s"%k)