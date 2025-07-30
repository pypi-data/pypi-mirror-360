from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ShapeAdjustmentList (SpireObject) :
    """
    <summary>
        Reprasents a collection of shape's adjustments.
    </summary>
    """
    @property
    def Count(self)->int:
        """
    <summary>
        Return a number of adjustments.
    </summary>
        """
        GetDllLibPpt().ShapeAdjustmentList_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().ShapeAdjustmentList_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ShapeAdjustmentList_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'ShapeAdjust':
        """
    <summary>
        Gets adjustment by index.
    </summary>
    <param name="index">adjustment's index.</param>
    <returns>
  <see cref="T:Spire.Presentation.ShapeAdjust" />.</returns>
        """
        
        GetDllLibPpt().ShapeAdjustmentList_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ShapeAdjustmentList_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeAdjustmentList_get_Item,self.Ptr, index)
        ret = None if intPtr==None else ShapeAdjust(intPtr)
        return ret


