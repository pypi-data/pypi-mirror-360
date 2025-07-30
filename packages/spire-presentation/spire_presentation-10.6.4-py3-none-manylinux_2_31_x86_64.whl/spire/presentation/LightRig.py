from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LightRig (SpireObject) :
    """
    <summary>
        Represents LightRig.
    </summary>
    """
    @property

    def Direction(self)->'LightingDirectionType':
        """
    <summary>
        Light direction
            Read/write <see cref="T:Spire.Presentation.LightingDirectionType" /></summary>
        """
        GetDllLibPpt().LightRig_get_Direction.argtypes=[c_void_p]
        GetDllLibPpt().LightRig_get_Direction.restype=c_int
        ret = CallCFunction(GetDllLibPpt().LightRig_get_Direction,self.Ptr)
        objwraped = LightingDirectionType(ret)
        return objwraped

    @Direction.setter
    def Direction(self, value:'LightingDirectionType'):
        GetDllLibPpt().LightRig_set_Direction.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().LightRig_set_Direction,self.Ptr, value.value)

    @property

    def PresetType(self)->'PresetLightRigType':
        """
    <summary>
        Represents a preset light right that can be applied to a shape. 
            The light rig represents a group of lights oriented
            in a specific way relative to a 3D scene.
            Read/write <see cref="T:Spire.Presentation.PresetLightRigType" /></summary>
        """
        GetDllLibPpt().LightRig_get_PresetType.argtypes=[c_void_p]
        GetDllLibPpt().LightRig_get_PresetType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().LightRig_get_PresetType,self.Ptr)
        objwraped = PresetLightRigType(ret)
        return objwraped

    @PresetType.setter
    def PresetType(self, value:'PresetLightRigType'):
        GetDllLibPpt().LightRig_set_PresetType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().LightRig_set_PresetType,self.Ptr, value.value)


    def SetRotation(self ,latitude:float,longitude:float,revolution:float):
        """
    <summary>
        A rotation is defined through the use of a latitude
            coordinate, a longitude coordinate, and a revolution about the axis 
            as the latitude and longitude coordinates.
    </summary>
        """
        
        GetDllLibPpt().LightRig_SetRotation.argtypes=[c_void_p ,c_float,c_float,c_float]
        CallCFunction(GetDllLibPpt().LightRig_SetRotation,self.Ptr, latitude,longitude,revolution)


    def GetRotation(self)->List[float]:
        """
    <summary>
        A rotation is defined through the use of a latitude
            coordinate, a longitude coordinate, and a revolution about the axis 
            as the latitude and longitude coordinates.
            first element in return array - latitude, second - longitude, third - revolution.
    </summary>
        """
        GetDllLibPpt().LightRig_GetRotation.argtypes=[c_void_p]
        GetDllLibPpt().LightRig_GetRotation.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().LightRig_GetRotation,self.Ptr)
        ret = GetVectorFromArray(intPtrArray, c_float)
        return ret


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().LightRig_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().LightRig_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().LightRig_Equals,self.Ptr, intPtrobj)
        return ret

