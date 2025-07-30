from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FormatThreeD (  PptObject, IActiveSlide) :
    """
    <summary>
        Represents 3-D properties.
    </summary>
    """
    @property

    def Camera(self)->'Camera':
        """
    <summary>
        Gets or sets the settings of a camera.
            Read/write <see cref="T:Spire.Presentation.Camera" />.
    </summary>
        """
        GetDllLibPpt().FormatThreeD_get_Camera.argtypes=[c_void_p]
        GetDllLibPpt().FormatThreeD_get_Camera.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FormatThreeD_get_Camera,self.Ptr)
        ret = None if intPtr==None else Camera(intPtr)
        return ret


    @Camera.setter
    def Camera(self, value:'Camera'):
        GetDllLibPpt().FormatThreeD_set_Camera.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().FormatThreeD_set_Camera,self.Ptr, value.Ptr)

    @property

    def LightRig(self)->'LightRig':
        """
    <summary>
        Gets or sets the type of a light.
            Read/write <see cref="T:Spire.Presentation.LightRig" />.
    </summary>
        """
        GetDllLibPpt().FormatThreeD_get_LightRig.argtypes=[c_void_p]
        GetDllLibPpt().FormatThreeD_get_LightRig.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FormatThreeD_get_LightRig,self.Ptr)
        ret = None if intPtr==None else LightRig(intPtr)
        return ret


    @LightRig.setter
    def LightRig(self, value:'LightRig'):
        GetDllLibPpt().FormatThreeD_set_LightRig.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().FormatThreeD_set_LightRig,self.Ptr, value.Ptr)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().FormatThreeD_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().FormatThreeD_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().FormatThreeD_Equals,self.Ptr, intPtrobj)
        return ret

    @property

    def ShapeThreeD(self)->'ShapeThreeD':
        """

        """
        GetDllLibPpt().FormatThreeD_get_ShapeThreeD.argtypes=[c_void_p]
        GetDllLibPpt().FormatThreeD_get_ShapeThreeD.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FormatThreeD_get_ShapeThreeD,self.Ptr)
        ret = None if intPtr==None else ShapeThreeD(intPtr)
        return ret


