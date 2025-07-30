from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class Camera (SpireObject) :
    """
    <summary>
        Represents Camera.
    </summary>
    """
    @property

    def PresetType(self)->'PresetCameraType':
        """
    <summary>
        Camera type
            Read/write <see cref="P:Spire.Presentation.Camera.PresetType" /></summary>
        """
        GetDllLibPpt().Camera_get_PresetType.argtypes=[c_void_p]
        GetDllLibPpt().Camera_get_PresetType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Camera_get_PresetType,self.Ptr)
        objwraped = PresetCameraType(ret)
        return objwraped

    @PresetType.setter
    def PresetType(self, value:'PresetCameraType'):
        GetDllLibPpt().Camera_set_PresetType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().Camera_set_PresetType,self.Ptr, value.value)

    @property
    def FieldOfView(self)->float:
        """
    <summary>
        Camera field of view.
            Read/write <see cref="T:System.Single" /></summary>
        """
        GetDllLibPpt().Camera_get_FieldOfView.argtypes=[c_void_p]
        GetDllLibPpt().Camera_get_FieldOfView.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Camera_get_FieldOfView,self.Ptr)
        return ret

    @FieldOfView.setter
    def FieldOfView(self, value:float):
        GetDllLibPpt().Camera_set_FieldOfView.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Camera_set_FieldOfView,self.Ptr, value)

    @property
    def Zoom(self)->float:
        """
    <summary>
        Camera percentage zoom.
            Read/write <see cref="T:System.Single" /></summary>
        """
        GetDllLibPpt().Camera_get_Zoom.argtypes=[c_void_p]
        GetDllLibPpt().Camera_get_Zoom.restype=c_float
        ret = CallCFunction(GetDllLibPpt().Camera_get_Zoom,self.Ptr)
        return ret

    @Zoom.setter
    def Zoom(self, value:float):
        GetDllLibPpt().Camera_set_Zoom.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().Camera_set_Zoom,self.Ptr, value)


    def SetCameraRotation(self ,latitude:float,longitude:float,revolution:float):
        """
    <summary>
        A rotation is defined .
    </summary>
        """
        
        GetDllLibPpt().Camera_SetCameraRotation.argtypes=[c_void_p ,c_float,c_float,c_float]
        CallCFunction(GetDllLibPpt().Camera_SetCameraRotation,self.Ptr, latitude,longitude,revolution)


    def GetCameraRotations(self)->List[float]:
        """
    <summary>
        A rotation is defined. latitude, longitude, revolution.
            Gets null if no rotation defined.
    </summary>
        """
        GetDllLibPpt().Camera_GetCameraRotations.argtypes=[c_void_p]
        GetDllLibPpt().Camera_GetCameraRotations.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().Camera_GetCameraRotations,self.Ptr)
        ret = GetVectorFromArray(intPtrArray, c_float)
        return ret


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().Camera_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().Camera_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Camera_Equals,self.Ptr, intPtrobj)
        return ret

