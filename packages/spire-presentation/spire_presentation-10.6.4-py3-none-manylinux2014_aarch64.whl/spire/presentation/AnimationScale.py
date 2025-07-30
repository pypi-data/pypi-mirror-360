from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationScale (  CommonBehavior) :
    """
    <summary>
        Represents animation scale effect.
    </summary>
    """
    @property

    def ZoomContent(self)->'TriState':
        """
    <summary>
        Indicates whether a content should be zoomed.
    </summary>
        """
        GetDllLibPpt().AnimationScale_get_ZoomContent.argtypes=[c_void_p]
        GetDllLibPpt().AnimationScale_get_ZoomContent.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationScale_get_ZoomContent,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @ZoomContent.setter
    def ZoomContent(self, value:'TriState'):
        GetDllLibPpt().AnimationScale_set_ZoomContent.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AnimationScale_set_ZoomContent,self.Ptr, value.value)

    @property

    def From(self)->'PointF':
        """
    <summary>
        Indicates Starting the animation from (in percents).
            Read/write <see cref="T:System.Drawing.PointF" />.
    </summary>
        """
        GetDllLibPpt().AnimationScale_get_From.argtypes=[c_void_p]
        GetDllLibPpt().AnimationScale_get_From.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationScale_get_From,self.Ptr)
        ret = None if intPtr==None else PointF(intPtr)
        return ret


    @From.setter
    def From(self, value:'PointF'):
        GetDllLibPpt().AnimationScale_set_From.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().AnimationScale_set_From,self.Ptr, value.Ptr)

    @property

    def To(self)->'PointF':
        """
    <summary>
        Indicates the ending location for an animation scale effect .
            Read/write <see cref="T:System.Drawing.PointF" />.
    </summary>
        """
        GetDllLibPpt().AnimationScale_get_To.argtypes=[c_void_p]
        GetDllLibPpt().AnimationScale_get_To.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationScale_get_To,self.Ptr)
        ret = None if intPtr==None else PointF(intPtr)
        return ret


    @To.setter
    def To(self, value:'PointF'):
        GetDllLibPpt().AnimationScale_set_To.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().AnimationScale_set_To,self.Ptr, value.Ptr)

    @property

    def By(self)->'PointF':
        """
    <summary>
        describes the relative offset value for the animation.
            Read/write <see cref="T:System.Drawing.PointF" />.
    </summary>
        """
        GetDllLibPpt().AnimationScale_get_By.argtypes=[c_void_p]
        GetDllLibPpt().AnimationScale_get_By.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationScale_get_By,self.Ptr)
        ret = None if intPtr==None else PointF(intPtr)
        return ret


    @By.setter
    def By(self, value:'PointF'):
        GetDllLibPpt().AnimationScale_set_By.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().AnimationScale_set_By,self.Ptr, value.Ptr)

