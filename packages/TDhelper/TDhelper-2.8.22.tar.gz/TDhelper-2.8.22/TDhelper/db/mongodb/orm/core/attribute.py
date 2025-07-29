from collections.abc import Callable
from typing import Any
class oProperty(property):
    k= ''
    ins= None
    def __init__(self,k,ins, fget: Callable[[Any], Any] | None = None, fset: Callable[[Any, Any], None] | None = None, fdel: Callable[[Any], None] | None = None, doc: str | None = None) -> None:
        self.k= k
        self.ins= ins
        fget= fget if fget else self.getter
        fset= fset if fset else self.setter
        fdel= fdel if fdel else self.deleter
        doc= doc if doc else k
        super().__init__(fget, fset, fdel, doc)
        
    def setter(self,__instance, __value) -> property:
        if self.k in __instance.__fields__:
            __instance.__fields__[self.k]= __value
        else:
            raise ValueError("do not have attribute %s"%self.k)
            
    def getter(self, __instance) -> property:
        if self.k in __instance.__fields__:
            return __instance.__fields__[self.k]
        else:
            return None
    
    def deleter(self, __fdel: Callable[[Any], None]) -> property:
        return super().deleter(__fdel)