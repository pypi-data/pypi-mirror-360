from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationMotion (  CommonBehavior) :
    """

    """
    @property

    def From(self)->'PointF':
        """

        """
        GetDllLibPpt().AnimationMotion_get_From.argtypes=[c_void_p]
        GetDllLibPpt().AnimationMotion_get_From.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationMotion_get_From,self.Ptr)
        ret = None if intPtr==None else PointF(intPtr)
        return ret


    @From.setter
    def From(self, value:'PointF'):
        GetDllLibPpt().AnimationMotion_set_From.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().AnimationMotion_set_From,self.Ptr, value.Ptr)

    @property

    def To(self)->'PointF':
        """

        """
        GetDllLibPpt().AnimationMotion_get_To.argtypes=[c_void_p]
        GetDllLibPpt().AnimationMotion_get_To.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationMotion_get_To,self.Ptr)
        ret = None if intPtr==None else PointF(intPtr)
        return ret


    @To.setter
    def To(self, value:'PointF'):
        GetDllLibPpt().AnimationMotion_set_To.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().AnimationMotion_set_To,self.Ptr, value.Ptr)

    @property

    def By(self)->'PointF':
        """

        """
        GetDllLibPpt().AnimationMotion_get_By.argtypes=[c_void_p]
        GetDllLibPpt().AnimationMotion_get_By.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationMotion_get_By,self.Ptr)
        ret = None if intPtr==None else PointF(intPtr)
        return ret


    @By.setter
    def By(self, value:'PointF'):
        GetDllLibPpt().AnimationMotion_set_By.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().AnimationMotion_set_By,self.Ptr, value.Ptr)

    @property

    def RotationCenter(self)->'PointF':
        """

        """
        GetDllLibPpt().AnimationMotion_get_RotationCenter.argtypes=[c_void_p]
        GetDllLibPpt().AnimationMotion_get_RotationCenter.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationMotion_get_RotationCenter,self.Ptr)
        ret = None if intPtr==None else PointF(intPtr)
        return ret


    @RotationCenter.setter
    def RotationCenter(self, value:'PointF'):
        GetDllLibPpt().AnimationMotion_set_RotationCenter.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().AnimationMotion_set_RotationCenter,self.Ptr, value.Ptr)

    @property

    def Origin(self)->'AnimationMotionOrigin':
        """

        """
        GetDllLibPpt().AnimationMotion_get_Origin.argtypes=[c_void_p]
        GetDllLibPpt().AnimationMotion_get_Origin.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationMotion_get_Origin,self.Ptr)
        objwraped = AnimationMotionOrigin(ret)
        return objwraped

    @Origin.setter
    def Origin(self, value:'AnimationMotionOrigin'):
        GetDllLibPpt().AnimationMotion_set_Origin.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AnimationMotion_set_Origin,self.Ptr, value.value)

    @property

    def Path(self)->'MotionPath':
        """

        """
        from spire.presentation import MotionPath
        GetDllLibPpt().AnimationMotion_get_Path.argtypes=[c_void_p]
        GetDllLibPpt().AnimationMotion_get_Path.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationMotion_get_Path,self.Ptr)
        ret = None if intPtr==None else MotionPath(intPtr)
        return ret


    @Path.setter
    def Path(self, value:'MotionPath'):
        GetDllLibPpt().AnimationMotion_set_Path.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().AnimationMotion_set_Path,self.Ptr, value.Ptr)

    @property

    def PathEditMode(self)->'AnimationMotionPathEditMode':
        """

        """
        GetDllLibPpt().AnimationMotion_get_PathEditMode.argtypes=[c_void_p]
        GetDllLibPpt().AnimationMotion_get_PathEditMode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationMotion_get_PathEditMode,self.Ptr)
        objwraped = AnimationMotionPathEditMode(ret)
        return objwraped

    @PathEditMode.setter
    def PathEditMode(self, value:'AnimationMotionPathEditMode'):
        GetDllLibPpt().AnimationMotion_set_PathEditMode.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AnimationMotion_set_PathEditMode,self.Ptr, value.value)

    @property
    def RelativeAngle(self)->float:
        """

        """
        GetDllLibPpt().AnimationMotion_get_RelativeAngle.argtypes=[c_void_p]
        GetDllLibPpt().AnimationMotion_get_RelativeAngle.restype=c_float
        ret = CallCFunction(GetDllLibPpt().AnimationMotion_get_RelativeAngle,self.Ptr)
        return ret

    @RelativeAngle.setter
    def RelativeAngle(self, value:float):
        GetDllLibPpt().AnimationMotion_set_RelativeAngle.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().AnimationMotion_set_RelativeAngle,self.Ptr, value)

    @property

    def PointsType(self)->str:
        """

        """
        GetDllLibPpt().AnimationMotion_get_PointsType.argtypes=[c_void_p]
        GetDllLibPpt().AnimationMotion_get_PointsType.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().AnimationMotion_get_PointsType,self.Ptr))
        return ret


