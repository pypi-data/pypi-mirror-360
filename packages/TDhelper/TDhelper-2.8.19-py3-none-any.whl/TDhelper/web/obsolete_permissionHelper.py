import json
import os
import logging
from rest_framework.request import Request
from TDhelper.network.http.REST_HTTP import GET, POST, PUT, DELETE, serializePostData, ContentType
from TDhelper.generic.recursion import recursion, recursionCall
from TDhelper.generic.randGetValue import getValue

class permission:
    def __init__(self, host, platformKey, secret, httpHeaders={}, token_key='api-token') -> None:
        self._host = getValue(host).rstrip("/") + "/api/"
        self._platformKey = platformKey
        self._secret = secret
        self._httpHeaders = httpHeaders
        self._httpHeaders[token_key] = self._secret

    def register(self, path, encode='utf8') -> None:
        if os.path.exists(path):
            conf = ''
            with open(path, "r", -1, encoding=encode) as f:
                conf = f.read()
                f.close()
            if conf:
                conf = json.loads(conf)
                recursionCall(self._register_permission, 200, conf, **{})
        else:
            raise Exception("Not Found '%s'" % path)

    def _register_permission(self, config, **kwargs):
        if self._platformKey:
            config["permission_key"] = (
                self._platformKey + "." + config["permission_key"]
            )
        if not self._host.endswith("/"):
            self._host += "/"
        checkState, msg = self.checkAttr(
            ["permission_name", "permission_key", "permission_domain", "permission_uri","permission_enable","permission_attribute"], config)
        if not checkState:
            raise Exception("can not found attribute '%s'" % msg)
        post_data = {
            "permission_name": config["permission_name"],
            "permission_key": config["permission_key"],
            "permission_domain": config["permission_domain"],
            "permission_uri": config["permission_uri"],
            "permission_enable": config["permission_enable"],
            "permission_parent": config["permission_parent"]
            if "permission_parent" in config
            else kwargs["permission_parent"]
            if "permission_parent" in kwargs
            else 0,
            "permission_attribute": config["permission_attribute"] if config["permission_attribute"] else 0
        }
        state, body = POST(
            uri=self._host + "permissions/",
            post_data=post_data,
            http_headers=self._httpHeaders,
            content_type=ContentType.JSON,
            time_out=15,
        )
        m_parent_id = 0
        if state == 200:
            m_ret = str(body, encoding="utf-8")
            m_ret_json = json.loads(m_ret)  # , encoding="utf-8")
            if m_ret_json["state"] == 200:
                m_parent_id = m_ret_json["msg"]["permission_id"]
                logging.info(
                    "create permission '%s' success." % config["permission_name"]
                )
            else:
                logging.info(
                    "create permission '%s' failed.error(%s)"
                    % (config["permission_name"], m_ret_json["msg"])
                )
        else:
            logging.info("create permission '%s' failed.error(%s)" %
                         (config["permission_name"], body))
        if "children" not in config:
            kwargs["break"] = False
        else:
            for item in config["children"]:
                kwargs["permission_parent"] = m_parent_id
                recursionCall(
                    self._register_permission, kwargs["limit"], item, **kwargs
                )
            kwargs["break"] = False
        return config, kwargs

    def checkAttr(self, attrs: list, rel: dict):
        state = True
        msg = ""
        for o in attrs:
            if o not in rel:
                state = False
                msg = "".join([o, ","])
        return state, msg


class PermissionACL:
    '''权限检查
    args:
        rpc_key: permission key.
        permission_rpc_service: permission service key.
        method: permission service validate method.
        params_container_class: context class.
        platformKey: service platform key.
        tokenKey: token key filed.
    '''

    def __init__(
        self, permission_rpc_service, method, params_container_class, platformKey=None, tokenKey="permission-token"
    ):
        self._params_container = params_container_class
        self._platformKey = platformKey
        self._tokenKey = tokenKey
        self._rpc = None
        self._rpc_service_key= permission_rpc_service
        self._rpc_service_method = method

    def addRPCHandle(self, handle):
        self._rpc = handle

    def _core(self, premissionKey=None, debug=False, *args, **kwargs):
        validate_state = False
        if not debug:
            if self._platformKey:
                self._platformKey += "."
                self._platformKey = self._platformKey.upper()
            eventKey = self._platformKey + premissionKey.upper()
            params_instance = None
            for k in args:
                if isinstance(k, self._params_container):
                    params_instance = k
                    break
            if not params_instance:
                for k, v in kwargs:
                    if isinstance(v, self._params_container):
                        params_instance = v
                        break
            if not params_instance:
                return 500,"can found context."
            if isinstance(params_instance, Request):
                if self._tokenKey in params_instance._request.headers:
                    token = params_instance._request.headers[self._tokenKey]
                else:
                    return 500,"http headers can not found '%s' key." % self._tokenKey
            elif isinstance(params_instance, dict):
                token = params_instance[self._tokenKey]
            elif isinstance(params_instance, (int, str, float)):
                token = params_instance
            else:
                token = getattr(params_instance, self._tokenKey)
            if token:
                if self._rpc:
                    validate_ret = self._rpc.__call__(self._rpc_service_key,self._rpc_service_method, **{"token": token, "event": eventKey})
                    if validate_ret:
                        if validate_ret["state"] == 200:
                            validate_state = True
                        else:
                            return 500,"access error.(%s)" % validate_ret["msg"]
                    else:
                        return 500,"access http error. remote call error."
                else:
                    return 500,"rpc handle is none."
            else:
                return 500,"'%s' is None."%self._tokenKey
        else:
            validate_state = True
        if validate_state:
            return 200,"success"
        else:
            return 401,"Unauthorized"
