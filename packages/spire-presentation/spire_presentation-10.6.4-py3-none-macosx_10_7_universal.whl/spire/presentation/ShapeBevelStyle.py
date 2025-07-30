from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ShapeBevelStyle (SpireObject) :
    """
    <summary>
        Contains the properties of shape.
    </summary>
    """
    @property
    def Width(self)->float:
        """
    <summary>
        Bevel width.
            Read/write <see cref="T:System.Double" /></summary>
        """
        GetDllLibPpt().ShapeBevelStyle_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().ShapeBevelStyle_get_Width.restype=c_double
        ret = CallCFunction(GetDllLibPpt().ShapeBevelStyle_get_Width,self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        GetDllLibPpt().ShapeBevelStyle_set_Width.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().ShapeBevelStyle_set_Width,self.Ptr, value)

    @property
    def Height(self)->float:
        """
    <summary>
        Bevel height.
            Read/write <see cref="T:System.Double" /></summary>
        """
        GetDllLibPpt().ShapeBevelStyle_get_Height.argtypes=[c_void_p]
        GetDllLibPpt().ShapeBevelStyle_get_Height.restype=c_double
        ret = CallCFunction(GetDllLibPpt().ShapeBevelStyle_get_Height,self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:float):
        GetDllLibPpt().ShapeBevelStyle_set_Height.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().ShapeBevelStyle_set_Height,self.Ptr, value)

    @property

    def PresetType(self)->'BevelPresetType':
        """
    <summary>
        Bevel type.
            Read/write <see cref="T:Spire.Presentation.Drawing.BevelPresetType" /></summary>
        """
        GetDllLibPpt().ShapeBevelStyle_get_PresetType.argtypes=[c_void_p]
        GetDllLibPpt().ShapeBevelStyle_get_PresetType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ShapeBevelStyle_get_PresetType,self.Ptr)
        objwraped = BevelPresetType(ret)
        return objwraped

    @PresetType.setter
    def PresetType(self, value:'BevelPresetType'):
        GetDllLibPpt().ShapeBevelStyle_set_PresetType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ShapeBevelStyle_set_PresetType,self.Ptr, value.value)

