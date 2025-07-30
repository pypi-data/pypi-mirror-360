from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GradientFillFormat (  IActiveSlide) :
    """
    <summary>
        Represent a gradient format.
    </summary>
    """

    def Equals(self ,obj:'SpireObject')->bool:
        """
    <summary>
        Indicates whether the two GradientFormat instances are equal.
    </summary>
    <param name="obj">The GradientFormat to compare with the current GradientFormat.</param>
    <returns>
  <b>true</b> if the specified GradientFormat is equal to the current GradientFormat; otherwise, <b>false</b>.</returns>
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().GradientFillFormat_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().GradientFillFormat_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GradientFillFormat_Equals,self.Ptr, intPtrobj)
        return ret

    def GetHashCode(self)->int:
        """

        """
        GetDllLibPpt().GradientFillFormat_GetHashCode.argtypes=[c_void_p]
        GetDllLibPpt().GradientFillFormat_GetHashCode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().GradientFillFormat_GetHashCode,self.Ptr)
        return ret

    @property

    def TileFlip(self)->'TileFlipMode':
        """
    <summary>
        Gets or sets the flipping mode for a gradient.
            Read/write <see cref="P:Spire.Presentation.Drawing.GradientFillFormat.TileFlip" />.
    </summary>
        """
        GetDllLibPpt().GradientFillFormat_get_TileFlip.argtypes=[c_void_p]
        GetDllLibPpt().GradientFillFormat_get_TileFlip.restype=c_int
        ret = CallCFunction(GetDllLibPpt().GradientFillFormat_get_TileFlip,self.Ptr)
        objwraped = TileFlipMode(ret)
        return objwraped

    @TileFlip.setter
    def TileFlip(self, value:'TileFlipMode'):
        GetDllLibPpt().GradientFillFormat_set_TileFlip.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().GradientFillFormat_set_TileFlip,self.Ptr, value.value)

    @property

    def TileRectangle(self)->'RelativeRectangle':
        """
<summary></summary>
        """
        GetDllLibPpt().GradientFillFormat_get_TileRectangle.argtypes=[c_void_p]
        GetDllLibPpt().GradientFillFormat_get_TileRectangle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GradientFillFormat_get_TileRectangle,self.Ptr)
        ret = None if intPtr==None else RelativeRectangle(intPtr)
        return ret


    @TileRectangle.setter
    def TileRectangle(self, value:'RelativeRectangle'):
        GetDllLibPpt().GradientFillFormat_set_TileRectangle.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().GradientFillFormat_set_TileRectangle,self.Ptr, value.Ptr)

    @property

    def GradientStyle(self)->'GradientStyle':
        """
    <summary>
        Gets or sets the style of a gradient.
            Read/write <see cref="P:Spire.Presentation.Drawing.GradientFillFormat.GradientStyle" />.
    </summary>
        """
        GetDllLibPpt().GradientFillFormat_get_GradientStyle.argtypes=[c_void_p]
        GetDllLibPpt().GradientFillFormat_get_GradientStyle.restype=c_int
        ret = CallCFunction(GetDllLibPpt().GradientFillFormat_get_GradientStyle,self.Ptr)
        objwraped = GradientStyle(ret)
        return objwraped

    @GradientStyle.setter
    def GradientStyle(self, value:'GradientStyle'):
        GetDllLibPpt().GradientFillFormat_set_GradientStyle.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().GradientFillFormat_set_GradientStyle,self.Ptr, value.value)

    @property

    def GradientShape(self)->'GradientShapeType':
        """
    <summary>
        Gets or sets the shape of a gradient.
            Read/write <see cref="P:Spire.Presentation.Drawing.GradientFillFormat.GradientShape" />.
    </summary>
        """
        GetDllLibPpt().GradientFillFormat_get_GradientShape.argtypes=[c_void_p]
        GetDllLibPpt().GradientFillFormat_get_GradientShape.restype=c_int
        ret = CallCFunction(GetDllLibPpt().GradientFillFormat_get_GradientShape,self.Ptr)
        objwraped = GradientShapeType(ret)
        return objwraped

    @GradientShape.setter
    def GradientShape(self, value:'GradientShapeType'):
        GetDllLibPpt().GradientFillFormat_set_GradientShape.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().GradientFillFormat_set_GradientShape,self.Ptr, value.value)

    @property

    def GradientStops(self)->'GradientStopCollection':
        """
    <summary>
        Gets the collection of gradient stops.
            Read-only <see cref="T:Spire.Presentation.Collections.GradientStopCollection" />.
    </summary>
        """
        GetDllLibPpt().GradientFillFormat_get_GradientStops.argtypes=[c_void_p]
        GetDllLibPpt().GradientFillFormat_get_GradientStops.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GradientFillFormat_get_GradientStops,self.Ptr)
        ret = None if intPtr==None else GradientStopCollection(intPtr)
        return ret


    @property

    def LinearGradientFill(self)->'LinearGradientFill':
        """

        """
        GetDllLibPpt().GradientFillFormat_get_LinearGradientFill.argtypes=[c_void_p]
        GetDllLibPpt().GradientFillFormat_get_LinearGradientFill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GradientFillFormat_get_LinearGradientFill,self.Ptr)
        ret = None if intPtr==None else LinearGradientFill(intPtr)
        return ret


