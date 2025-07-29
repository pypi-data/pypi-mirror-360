import hashlib
from TDhelper.generic.transformationType import transformation

def MD5(s:"str|list|dict",encoding="utf-8"):
    m= hashlib.md5()
    if isinstance(s,str):
        m.update(s.encode(encoding))
    elif isinstance(s,dict):
        _str=""
        for k,v in s.items():
           _str="".join([_str,transformation(v,str)])
        m.update(_str.encode(encoding))
    elif isinstance(s,list):
        _str=""
        for v in s:
            _str="".join([_str,transformation((lambda v:v if not isinstance(v,tuple) else v[1])(v),str)])
        m.update(_str.encode(encoding))
    else:
        raise Exception("MD5 input param type had error, str,dict,list.")
    return m.hexdigest()

def SALT(s:"list|dict",encoding="utf-8",desc=True):
    '''SALT
        
        generate salt.
    
    Args:
    
        s (list|dict): input value.
        
        encoding(encode): encode, default 'UTF-8'.
        
        desc(Boolen): sort type, default true. value set true sort with descending order, value set false sort with ascending order    
        
    Returns:
            
            salt, 128 bit 
        
    Raises:
            INPUT Type ERROR
        
    '''
    if isinstance(s,list):
        return MD5(s,encoding)
    elif isinstance(s,dict):
        return MD5(sorted(s.items(), reverse=desc), encoding)
    else:
        raise Exception("SALT input param type had errot, list,dict.")