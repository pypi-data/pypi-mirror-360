from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class IMasterLayouts (SpireObject) :
    """

    """
    @property
    def Count(self)->int:
        """
    <summary>
        Gets the number of layout slides in a collection.
    </summary>
        """
        GetDllLibPpt().IMasterLayouts_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().IMasterLayouts_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IMasterLayouts_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'ILayout':
        """

        """
        
        GetDllLibPpt().IMasterLayouts_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().IMasterLayouts_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IMasterLayouts_get_Item,self.Ptr, index)
        ret = None if intPtr==None else ILayout(intPtr)
        return ret



    def GetByType(self ,type:'SlideLayoutType')->'ILayout':
        """

        """
        enumtype:c_int = type.value

        GetDllLibPpt().IMasterLayouts_GetByType.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().IMasterLayouts_GetByType.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IMasterLayouts_GetByType,self.Ptr, enumtype)
        ret = None if intPtr==None else ILayout(intPtr)
        return ret



    def RemoveMasterLayout(self ,index:int):
        """

        """
        
        GetDllLibPpt().IMasterLayouts_RemoveMasterLayout.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().IMasterLayouts_RemoveMasterLayout,self.Ptr, index)

