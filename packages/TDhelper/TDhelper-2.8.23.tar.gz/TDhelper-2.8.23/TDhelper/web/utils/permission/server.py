import json
import os
import logging
from TDhelper.generic.recursion import recursionCall

class regist_permission:
    def __init__(self, conf_path, union_app: str, platform_key='', domain="", encode='utf8'):
        self.__encoding__ = encode
        self.__conf_path__ = conf_path
        self.__permission_regist_method__ = None
        self.__rpc_secret__ = {}
        self.__union_app__ = union_app
        self.__platform_key__ = platform_key
        self.__domain__ = domain

    def set_handle(self, handle, service_key, method_key):
        if handle:
            o = handle.__get_service__(service_key)
            if o:
                m_method = o.__get_method_handle__(method_key)
                if m_method:
                    self.__permission_regist_method__ = m_method
                else:
                    raise Exception("not found method %s in %s." %
                                    (method_key, service_key))
            else:
                raise Exception("not found service %s in handle" % service_key)
        else:
            raise Exception("handle is none.")

    def register(self) -> None:
        if os.path.exists(self.__conf_path__):
            conf = ''
            with open(self.__conf_path__, "r", -1, encoding=self.__encoding__) as f:
                conf = f.read()
                f.close()
            if conf:
                conf = json.loads(conf)
                if conf:
                    recursionCall(self._register_permission, 200, conf, **{})
                else:
                    logging.info("permission file: '/config/regist_conf/permission.json' not configure.")
        else:
            raise Exception("Not Found '%s'" % self.__conf_path__)

    def _register_permission(self, config, **kwargs):
        if self.__platform_key__:
            config["permission_key"] = '.'.join(
                [self.__platform_key__, config["permission_key"]])
        checkState, msg = self.checkAttr(
            ["permission_name", "permission_key", "permission_uri", "permission_attribute", "permission_sys"], config)
        if not checkState:
            raise Exception("can not found attribute '%s'" % msg)

        post_data = {
            "data": {
                "union_app": self.__union_app__,
                "permission_name": config["permission_name"],
                "permission_key": config["permission_key"].upper(),
                "permission_uri": "".join([self.__domain__.rstrip('/'), '/', config["permission_uri"].strip('/')]),
                "parent": config["permission_parent"]
                if "permission_parent" in config
                else kwargs["permission_parent"]
                if "permission_parent" in kwargs
                else 0,
                "permission_attribute": config["permission_attribute"] if config["permission_attribute"] else 0,
                "sys_type": config['permission_sys']}
        }
        m_result = self.__permission_regist_method__(**post_data)
        m_parent_id = 0
        if m_result.get("state", -1) == 200:
            m_parent_id = m_result["msg"]["id"]
            logging.info(
                "create permission '%s' success." % config["permission_name"]
            )
        else:
            logging.info(
                "create permission '%s' failed.error(%s)"
                % (config["permission_name"], m_result.get("msg", "unknow error."))
            )
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
                msg = ";".join([msg, o]) if msg else "".join(o)
        return state, msg
