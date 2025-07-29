from types import FunctionType
from TDhelper.db.mongodb.orm.core.field_type import *
class field:
    model_type:field_type= None
    default= None
    max_length= None
    validate_funs:list|FunctionType= None
    is_none= False
    value= None
    
    def __init__(self,type:field_type, default_value=None,max_length=None,none:bool=False,valid_list:list|FunctionType= None) -> None:
        self.model_type=type
        self.default= default_value
        self.max_length= max_length
        self.is_none= none
        self.validate_funs= valid_list
        if type == field_type.String:
            if not max_length:
                raise ValueError("string field must set max length.")