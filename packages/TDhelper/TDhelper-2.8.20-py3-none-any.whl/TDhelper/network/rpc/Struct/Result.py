import json
#! python 3.6
import json
from typing import Any

class Result:

    __result_code__ = 0
    __result_status__ = False
    __result_message = ""
    __result_data = Any

    def __init__(self, code: int, status: bool, message: str, data: dict | str) -> object:
        """__init__
            Instance Result object.
        Parameters:
            code - <class:int>, result code.
            status - <class:bool>, result status.
            message - <class:str>, if status is false, then read message get the error message.
            data - <class:str|dict>, if status is true, the read data get the data.
        Returns:
            <class: object>, the result instance.
        """
        self.__result_code__ = code
        self.__result_status__ = status
        self.__result_message__ = message
        self.__result_data__ = data

    @classmethod
    def dumps(self,isJson= False) -> json:
        """jump
            jump instance to json object.
        Parameters:
            self - Result instance.
            isJson - control result type. default False, return Dict, can set True then will return Json str.
        Returns:
            <class: dict|json>, result dict or json.
        """
        m_result= {
            "code": self.__result_code__,
            "status": self.__result_code__,
            "message": self.__result_message,
            "data": self.__result_data
        }
        if isJson:
            m_result=json.dumps(m_result)
        return m_result

    @classmethod
    def loads(self,_json:str|dict) -> object:
        if isinstance(_json,str):
            _json= json.loads(_json)
        if _json:
            if 'code' not in _json:
                raise(Exception("Missing field 'code'."))
            if 'status' not in _json:
                raise(Exception("Missing field 'status'."))
            if _json['status']:
                if 'data' not in _json:
                    raise(Exception("Missing field 'data'"))
            else:
                if 'message' not in _json:
                    raise(Exception("Missing field 'message'."))
            return Result(_json['code'],_json['status'],_json['message'],_json['data'])
