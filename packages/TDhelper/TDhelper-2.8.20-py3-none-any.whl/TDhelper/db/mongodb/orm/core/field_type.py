from enum import Enum
import datetime
import bson

class field_type(Enum):
    Integer= int
    Float= float
    String= str
    DateTime= datetime
    Dict= dict
    List= list
    BsonId= bson