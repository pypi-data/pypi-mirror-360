from TDhelper.generic.transformationType import transformation
from TDhelper.document.excel.FieldType import *
from openpyxl import load_workbook
import datetime
import os
import csv
from types import FunctionType,MethodType





class Meta:
    file = None
    sheet = "sheet1"
    extension = "xlsx"
    headrow = True 
    headrow_row_offset = 1

class modelMeta(type):
    def __new__(cls, name, bases, dct):
        attrs = {
            "mapping": {},
            "__reverse_mapping__": {},
            "__enter__": __enter__,
            "__exit__": __exit__,
            "__rows__": [],
            "close": close,
            "__initExcelHandle__": __initExcelHandle__,
            "_translateMode": _translateMode,
            "__rowsCount__": 0,
            "__col_offset__": 0, 
        }
        for name, value in dct.items():
            if isinstance(dct[name], FieldType):
                attrs["mapping"][name] = value.bindCol
                attrs["__reverse_mapping__"][str(value.bindCol)] = name
                attrs[name] = cls._AttributeOverride(name, value.fieldType)
            elif isinstance(dct[name],FunctionType):
                _n_=name.lower()
                if _n_ == "getcount":
                    attrs[name]= getCount
                elif _n_ == "items":
                    attrs[name]= items
                elif _n_=="close":
                    attrs[name]= close
                elif _n_=="range_items":
                    attrs[name]= items_range
                elif _n_=="getitem":
                    attrs[name]= getItem
                elif _n_=="save_excel":
                    attrs[name]= save_excel
                else:
                    attrs[name]= value
            else:
                attrs[name] = value
        return super(modelMeta, cls).__new__(cls, name, bases, attrs)

    class _AttributeOverride:
        def __init__(self, name, m_type):
            self._name = name
            self._type = m_type

        def __get__(self, instance, owen):
            return instance.__dict__[self._name]

        def __set__(self, instance, value):
            try:
                instance.__dict__[self._name] = transformation(value, self._type)
                instance.__rows__[instance.__col_offset__-1][instance.mapping[self._name]-1].value= value
            except Exception as e:
                raise e
            
        def __delete__(self, instance):
            instance.__dict__.pop(self._name)

def __initExcelHandle__(self):
    try:
        if self.Meta.file:
            m_extension = self.Meta.file.rsplit(".")[1]
            if m_extension == "csv":
                self.Meta.extension = "csv"
                self.__excelHandle__ = open(self.Meta.file)
                self.__sheetHandle__ = csv.reader(self.__excelHandle__)
            elif m_extension == "xlsx" or m_extension == "xls":
                self.Meta.extension = "xlsx"
                self.__excelHandle__ = load_workbook(self.Meta.file)
                self.__sheetHandle__ = self.__excelHandle__[self.Meta.sheet]
            else:
                raise Exception("file extension is error.")
            if self.__sheetHandle__:
                for col in self.__sheetHandle__:
                    self.__rows__.append(col)
                if self.Meta.headrow:
                    for _t_ in range(0,self.Meta.headrow_row_offset):
                        self.__rows__.pop(0)
                self.__rowsCount__ = len(self.__rows__)
        else:
            raise Exception("meta file is None.")
    except Exception as e:
        raise e


def _translateMode(self, data=[]):
    if data:
        try:
            tmp_index = 1
            for v in data:
                if v == None or v == "None" or v=="#N/A":
                    v = None
                if str(tmp_index) in self.__reverse_mapping__:
                    setattr(
                        self,
                        self.__reverse_mapping__[str(tmp_index)],
                        v if not hasattr(v, "value") else v.value,
                    )
                tmp_index += 1
            return self
        except Exception as e:
            raise e
    else:
        raise Exception("translate data is none.")


def items(self):
    assert self.Meta.file, "Meta file is none."
    self.__col_offset__=0
    for col in self.__rows__:
        self.__col_offset__+=1
        yield self._translateMode(col)

def items_range(self,star:int=0,end:int=-1):
    if star<0:
        raise Exception("params 'star' value error.")
    if end==-1:
        end= len(self.__rows__)
    elif end >= len(self.__rows__):
        raise Exception("params 'end' out of range.")
    self.__col_offset__= star
    for o in range(star,end):
        result = self._translateMode(self.__rows__[o])
        self.__col_offset__+=1
        yield result
        
def getItem(self, offset):
    assert 0 <= offset < self.__rowsCount__, "offset %d, " % offset
    self.__col_offset__= offset
    return self._translateMode(self.__rows__[offset])

def __enter__(self):
    return self

def __exit__(self, exc_type, exc_value, exc_t):
    self.close()

def save_excel(self,save_path:str,auto_name=True):
    if os.path.exists(save_path):
        if not auto_name:
            raise Exception("%s file has exists." % save_path) 
        else:
            save_path = save_path.replace(".csv",datetime.datetime.now().strftime("%Y_%m_%d %H_%m_%S")+".csv")
    try:
        with open(save_path,"a+",766) as f:
            for col in self.__rows__:
                row_str= ",".join([o.value for o in col])
                row_str=",".join([row_str,"\r"])
                f.write(row_str)
                f.flush()
            f.close()
        return True
    except Exception as e:
        raise e
    
def close(self):
    self.__excelHandle__.close()
    if self.Meta.extension.lower() != "csv":
        pass#self.__sheetHandle__.close()
    self.__excelHandle__ = None
    self.__sheetHandle__ = None
    self.Meta = None


def getCount(self):
    return self.__rowsCount__
