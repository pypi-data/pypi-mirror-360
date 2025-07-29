class validate_permission:

    def __init__(
        self, rq_class, platformKey
    ):

        self.__error_message__ = ""
        self.__state_code__ = -1
        self.__handle_state__ = False
        self.__debug_state__ = False
        self.__rpc_service_method__ = None

        self.__request_context_class__ = rq_class
        self.__platform_key__:str = platformKey

    @property
    def error_message(self):
        return self.__error_message__

    def __reset_error_cfg__(self):
        self.__error_message__ = ""
        self.__state_code__ = -1

    def __error_update__(self, msg: str | list, code=-1):
        join_str = "" if not self.__error_message__ else ";\r\n"
        msg = (lambda v: v if isinstance(v, list) else [v])(msg)
        if self.__error_message__:
            msg.insert(0, self.__error_message__)
        self.__error_message__ = join_str.join(msg)
        self.__state_code__ = code

    def set_permission_handle(self, handle, permission_service_key, func_name):
        '''set permission client rpc handle.
        
        params:

            handle - <class: TDhelper.network.rpc.client> : rpc handle.
            
            permission_service_key - <class: string> : rpc service key.
            
            func_name - <class: string> : validate permission func key.
            
        returns:

            None.
        '''
        if handle:
            o = handle.__get_service__(permission_service_key)
            if o:
                m_method = o.__get_method_handle__(func_name)
                if m_method:
                    self.__rpc_service_method__ = m_method
                    self.__handle_state__= True
                else:
                    raise Exception("not found method %s in %s." %
                                    (func_name, permission_service_key))
            else:
                raise Exception("not found service %s in handle" % permission_service_key)
        else:
            raise Exception("handle is none.")

    def validate(self, group:int= 0, permission_key:str=None):
        '''validate permission.
        
        params:

            group - <class: int> : group id. 
            
            permission_key - <class: str> : permission key string.
            
        returns:

            object - <class: tuple> : 2 length. index 0 is state, index 1 is message. 
            
            example : (200, "success")
        
        '''
        if self.__handle_state__:
            if not self.__debug_state__:
                m_permission_key= permission_key.upper()
                if not permission_key.upper().startswith("".join([self.__platform_key__.upper(),'.'])):
                    m_permission_key = ("." if self.__platform_key__ else "").join(
                        [self.__platform_key__.upper(), permission_key.upper()])
                validate_ret = self.__rpc_service_method__(
                        **{"g":group,"p": m_permission_key})
                if validate_ret:
                        if validate_ret["state"] == 200:
                            return 200, "success"
                        else:
                            return 500, "access error(%s). " % validate_ret["msg"]
                else:
                        return 500, "access http error. remote call error."
            else:
                return 200, "debug mode, no checked permission."
        else:
            return 500, self.error_message
                
