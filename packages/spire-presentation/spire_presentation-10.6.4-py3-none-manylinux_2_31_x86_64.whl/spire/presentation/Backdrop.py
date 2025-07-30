from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class Backdrop (  PptObject) :
    """
    <summary>
        Represents Backdrop
            are being applied to
    </summary>
    """

    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().Backdrop_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().Backdrop_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Backdrop_Equals,self.Ptr, intPtrobj)
        return ret

    @property

    def NormalVector(self)->List[float]:
        """
    <summary>
        Gets or sets a normal vector.
    </summary>
        """
        GetDllLibPpt().Backdrop_get_NormalVector.argtypes=[c_void_p]
        GetDllLibPpt().Backdrop_get_NormalVector.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().Backdrop_get_NormalVector,self.Ptr)
        ret = GetVectorFromArray(intPtrArray, c_float)
        return ret

    @NormalVector.setter
    def NormalVector(self, value:List[float]):
        vCount = len(value)
        ArrayType = c_float * vCount
        vArray = ArrayType()
        for i in range(0, vCount):
            vArray[i] = value[i]
        GetDllLibPpt().Backdrop_set_NormalVector.argtypes=[c_void_p, ArrayType, c_int]
        CallCFunction(GetDllLibPpt().Backdrop_set_NormalVector,self.Ptr, vArray, vCount)

    @property

    def AnchorPoint(self)->List[float]:
        """
    <summary>
        Gets or sets a point in 3D space. 
    </summary>
        """
        GetDllLibPpt().Backdrop_get_AnchorPoint.argtypes=[c_void_p]
        GetDllLibPpt().Backdrop_get_AnchorPoint.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().Backdrop_get_AnchorPoint,self.Ptr)
        ret = GetVectorFromArray(intPtrArray, c_float)
        return ret

    @AnchorPoint.setter
    def AnchorPoint(self, value:List[float]):
        vCount = len(value)
        ArrayType = c_float * vCount
        vArray = ArrayType()
        for i in range(0, vCount):
            vArray[i] = value[i]
        GetDllLibPpt().Backdrop_set_AnchorPoint.argtypes=[c_void_p, ArrayType, c_int]
        CallCFunction(GetDllLibPpt().Backdrop_set_AnchorPoint,self.Ptr, vArray, vCount)

    @property

    def UpVector(self)->List[float]:
        """
    <summary>
        Gets or sets a vector representing up.
    </summary>
        """
        GetDllLibPpt().Backdrop_get_UpVector.argtypes=[c_void_p]
        GetDllLibPpt().Backdrop_get_UpVector.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().Backdrop_get_UpVector,self.Ptr)
        ret = GetVectorFromArray(intPtrArray, c_float)
        return ret

    @UpVector.setter
    def UpVector(self, value:List[float]):
        vCount = len(value)
        ArrayType = c_float * vCount
        vArray = ArrayType()
        for i in range(0, vCount):
            vArray[i] = value[i]
        GetDllLibPpt().Backdrop_set_UpVector.argtypes=[c_void_p, ArrayType, c_int]
        CallCFunction(GetDllLibPpt().Backdrop_set_UpVector,self.Ptr, vArray, vCount)

