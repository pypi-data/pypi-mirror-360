from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FillOverlayEffect (  ImageTransformBase) :
    """
    <summary>
        Represents a Fill Overlay effect. A fill overlay may be used to specify
            an additional fill for an object and blend the two fills together.
    </summary>
    """
    @property

    def FillFormat(self)->'FillFormat':
        """
    <summary>
        Fill format.
    </summary>
        """
        GetDllLibPpt().FillOverlayEffect_get_FillFormat.argtypes=[c_void_p]
        GetDllLibPpt().FillOverlayEffect_get_FillFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FillOverlayEffect_get_FillFormat,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @FillFormat.setter
    def FillFormat(self, value:'FillFormat'):
        GetDllLibPpt().FillOverlayEffect_set_FillFormat.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().FillOverlayEffect_set_FillFormat,self.Ptr, value.Ptr)

    @property

    def Blend(self)->'BlendMode':
        """
    <summary>
        BlendMode.
    </summary>
        """
        GetDllLibPpt().FillOverlayEffect_get_Blend.argtypes=[c_void_p]
        GetDllLibPpt().FillOverlayEffect_get_Blend.restype=c_int
        ret = CallCFunction(GetDllLibPpt().FillOverlayEffect_get_Blend,self.Ptr)
        objwraped = BlendMode(ret)
        return objwraped

    @Blend.setter
    def Blend(self, value:'BlendMode'):
        GetDllLibPpt().FillOverlayEffect_set_Blend.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().FillOverlayEffect_set_Blend,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().FillOverlayEffect_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().FillOverlayEffect_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().FillOverlayEffect_Equals,self.Ptr, intPtrobj)
        return ret

