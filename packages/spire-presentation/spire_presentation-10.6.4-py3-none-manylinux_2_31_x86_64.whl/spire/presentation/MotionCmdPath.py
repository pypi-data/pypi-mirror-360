from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class MotionCmdPath (SpireObject) :
    """
    <summary>
        Represent one command of a path.
    </summary>
    """
    @property

    def Points(self)->List['PointF']:
        """

        """
        GetDllLibPpt().MotionCmdPath_get_Points.argtypes=[c_void_p]
        GetDllLibPpt().MotionCmdPath_get_Points.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().MotionCmdPath_get_Points,self.Ptr)
        ret = GetObjVectorFromArray(intPtrArray, PointF)
        return ret


#    @Points.setter
#    def Points(self, value:List['PointF']):
#        vCount = len(value)
#        ArrayType = c_void_p * vCount
#        vArray = ArrayType()
#        for i in range(0, vCount):
#            vArray[i] = value[i].Ptr
#        GetDllLibPpt().MotionCmdPath_set_Points.argtypes=[c_void_p, ArrayType, c_int]
#        CallCFunction(GetDllLibPpt().MotionCmdPath_set_Points,self.Ptr, vArray, vCount)


    @property

    def CommandType(self)->'MotionCommandPathType':
        """

        """
        GetDllLibPpt().MotionCmdPath_get_CommandType.argtypes=[c_void_p]
        GetDllLibPpt().MotionCmdPath_get_CommandType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().MotionCmdPath_get_CommandType,self.Ptr)
        objwraped = MotionCommandPathType(ret)
        return objwraped

    @CommandType.setter
    def CommandType(self, value:'MotionCommandPathType'):
        GetDllLibPpt().MotionCmdPath_set_CommandType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().MotionCmdPath_set_CommandType,self.Ptr, value.value)

    @property
    def IsRelative(self)->bool:
        """

        """
        GetDllLibPpt().MotionCmdPath_get_IsRelative.argtypes=[c_void_p]
        GetDllLibPpt().MotionCmdPath_get_IsRelative.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().MotionCmdPath_get_IsRelative,self.Ptr)
        return ret

    @IsRelative.setter
    def IsRelative(self, value:bool):
        GetDllLibPpt().MotionCmdPath_set_IsRelative.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().MotionCmdPath_set_IsRelative,self.Ptr, value)

    @property

    def PointsType(self)->'MotionPathPointsType':
        """

        """
        GetDllLibPpt().MotionCmdPath_get_PointsType.argtypes=[c_void_p]
        GetDllLibPpt().MotionCmdPath_get_PointsType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().MotionCmdPath_get_PointsType,self.Ptr)
        objwraped = MotionPathPointsType(ret)
        return objwraped

    @PointsType.setter
    def PointsType(self, value:'MotionPathPointsType'):
        GetDllLibPpt().MotionCmdPath_set_PointsType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().MotionCmdPath_set_PointsType,self.Ptr, value.value)

