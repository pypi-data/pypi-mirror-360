from .meta.modelMeta import modelMeta

class model(metaclass=modelMeta):
    __excelHandle__ = None  # excel object.
    __sheetHandle__ = None  # sheet object.
    __rows__ = []  # all rows.

    def __init__(self, excelPath:str, headrow:bool=True, headrow_rows_count:int=1):
        '''初始化
        params:   
            - excelPath: <string>, Excel文件路径
            - headrow: <bool>, 是否有表头, 默认true
            - headrow_rows_count: <int>, 表头有多少行， 默认1
        
        '''
        assert excelPath, "parameter <excelPath> is None."
        self.Meta.file = excelPath
        self.Meta.headrow = headrow
        self.Meta.headrow_row_offset = headrow_rows_count
        try:
            self.__initExcelHandle__()
        except Exception as e:
            raise e

    def __initExcelHandle__(self):
        return None
    
    def items(self):
        pass

    def items_range(self,star:int=0,end:int=-1):
        pass
            
    def getItem(self, offset):
        pass

    def save_excel(self,save_path:str,auto_name=True):
        pass
        
    def close(self):
        pass

    def getCount(self):
        pass

    class Meta:
        """
        元数据
        - file: <string>, 文件路径.
        - sheet: <string>, sheet名称.
        - extension: <string>, 文件类型(xlsx,csv)
        """
        file = ""
        sheet = "sheet1"
        extension = "xlsx"
        headrow = True
        headrow_row_offset = 1
