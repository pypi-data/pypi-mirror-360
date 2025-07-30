from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ShapeNode (  Shape) :
    """

    """
    @property

    def ShapeStyle(self)->'ShapeStyle':
        """

        """
        GetDllLibPpt().ShapeNode_get_ShapeStyle.argtypes=[c_void_p]
        GetDllLibPpt().ShapeNode_get_ShapeStyle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeNode_get_ShapeStyle,self.Ptr)
        ret = None if intPtr==None else ShapeStyle(intPtr)
        return ret


    @property

    def ShapeType(self)->'ShapeType':
        """

        """
        GetDllLibPpt().ShapeNode_get_ShapeType.argtypes=[c_void_p]
        GetDllLibPpt().ShapeNode_get_ShapeType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ShapeNode_get_ShapeType,self.Ptr)
        objwraped = ShapeType(ret)
        return objwraped

    @ShapeType.setter
    def ShapeType(self, value:'ShapeType'):
        GetDllLibPpt().ShapeNode_set_ShapeType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ShapeNode_set_ShapeType,self.Ptr, value.value)

    @property

    def Adjustments(self)->'ShapeAdjustCollection':
        """

        """
        GetDllLibPpt().ShapeNode_get_Adjustments.argtypes=[c_void_p]
        GetDllLibPpt().ShapeNode_get_Adjustments.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeNode_get_Adjustments,self.Ptr)
        ret = None if intPtr==None else ShapeAdjustCollection(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().ShapeNode_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ShapeNode_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ShapeNode_Equals,self.Ptr, intPtrobj)
        return ret
    
    @property
    def Points(self)->List['PointF']:
        """

        """
        GetDllLibPpt().ShapeNode_get_Points.argtypes=[c_void_p]
        GetDllLibPpt().ShapeNode_get_Points.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().ShapeNode_get_Points,self.Ptr)
        ret = GetObjVectorFromArray(intPtrArray, PointF)
        return ret

