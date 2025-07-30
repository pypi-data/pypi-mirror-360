from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PresetShadow (SpireObject) :

    @dispatch
    def __init__(self):
        GetDllLibPpt().PresetShadow_CreatPresetShadow.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().PresetShadow_CreatPresetShadow)
        super(PresetShadow, self).__init__(intPtr)
    """
    <summary>
        Represents a preset shadow effect.
    </summary>
    """
    @property
    def Direction(self)->float:
        """
    <summary>
        Direction of shadow.
    </summary>
        """
        GetDllLibPpt().PresetShadow_get_Direction.argtypes=[c_void_p]
        GetDllLibPpt().PresetShadow_get_Direction.restype=c_float
        ret = CallCFunction(GetDllLibPpt().PresetShadow_get_Direction,self.Ptr)
        return ret

    @Direction.setter
    def Direction(self, value:float):
        GetDllLibPpt().PresetShadow_set_Direction.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().PresetShadow_set_Direction,self.Ptr, value)

    @property
    def Distance(self)->float:
        """
    <summary>
        Distance of shadow.
    </summary>
        """
        GetDllLibPpt().PresetShadow_get_Distance.argtypes=[c_void_p]
        GetDllLibPpt().PresetShadow_get_Distance.restype=c_double
        ret = CallCFunction(GetDllLibPpt().PresetShadow_get_Distance,self.Ptr)
        return ret

    @Distance.setter
    def Distance(self, value:float):
        GetDllLibPpt().PresetShadow_set_Distance.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().PresetShadow_set_Distance,self.Ptr, value)

    @property

    def ColorFormat(self)->'ColorFormat':
        """
    <summary>
        Color of shadow.
    </summary>
        """
        GetDllLibPpt().PresetShadow_get_ColorFormat.argtypes=[c_void_p]
        GetDllLibPpt().PresetShadow_get_ColorFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().PresetShadow_get_ColorFormat,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def Preset(self)->'PresetShadowValue':
        """
    <summary>
        Preset.
    </summary>
        """
        GetDllLibPpt().PresetShadow_get_Preset.argtypes=[c_void_p]
        GetDllLibPpt().PresetShadow_get_Preset.restype=c_int
        ret = CallCFunction(GetDllLibPpt().PresetShadow_get_Preset,self.Ptr)
        objwraped = PresetShadowValue(ret)
        return objwraped

    @Preset.setter
    def Preset(self, value:'PresetShadowValue'):
        GetDllLibPpt().PresetShadow_set_Preset.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().PresetShadow_set_Preset,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().PresetShadow_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().PresetShadow_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().PresetShadow_Equals,self.Ptr, intPtrobj)
        return ret

