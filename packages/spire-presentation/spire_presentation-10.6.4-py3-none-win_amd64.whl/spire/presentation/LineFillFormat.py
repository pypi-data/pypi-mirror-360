from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LineFillFormat (  PptObject, IActiveSlide, IActivePresentation) :
    """
    <summary>
        Represents properties for lines filling.
    </summary>
    """
    @property

    def FillType(self)->'FillFormatType':
        """
    <summary>
        Gets or sets the fill type.
            Read/write <see cref="P:Spire.Presentation.Drawing.LineFillFormat.FillType" />.
    </summary>
        """
        GetDllLibPpt().LineFillFormat_get_FillType.argtypes=[c_void_p]
        GetDllLibPpt().LineFillFormat_get_FillType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().LineFillFormat_get_FillType,self.Ptr)
        objwraped = FillFormatType(ret)
        return objwraped

    @FillType.setter
    def FillType(self, value:'FillFormatType'):
        GetDllLibPpt().LineFillFormat_set_FillType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().LineFillFormat_set_FillType,self.Ptr, value.value)

    @property

    def SolidFillColor(self)->'ColorFormat':
        """
    <summary>
        Gets the color of a solid fill.
            Read-only <see cref="T:Spire.Presentation.Drawing.ColorFormat" />.
    </summary>
        """
        GetDllLibPpt().LineFillFormat_get_SolidFillColor.argtypes=[c_void_p]
        GetDllLibPpt().LineFillFormat_get_SolidFillColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().LineFillFormat_get_SolidFillColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def Gradient(self)->'GradientFillFormat':
        """
    <summary>
        Gets the gradient fill format.
            Read-only <see cref="P:Spire.Presentation.Drawing.LineFillFormat.Gradient" />.
    </summary>
        """
        GetDllLibPpt().LineFillFormat_get_Gradient.argtypes=[c_void_p]
        GetDllLibPpt().LineFillFormat_get_Gradient.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().LineFillFormat_get_Gradient,self.Ptr)
        ret = None if intPtr==None else GradientFillFormat(intPtr)
        return ret


    @property

    def Pattern(self)->'PatternFillFormat':
        """
    <summary>
        Gets the pattern fill format.
            Read-only <see cref="P:Spire.Presentation.Drawing.LineFillFormat.Pattern" />.
    </summary>
        """
        GetDllLibPpt().LineFillFormat_get_Pattern.argtypes=[c_void_p]
        GetDllLibPpt().LineFillFormat_get_Pattern.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().LineFillFormat_get_Pattern,self.Ptr)
        ret = None if intPtr==None else PatternFillFormat(intPtr)
        return ret


    @property

    def RotateWithShape(self)->'TriState':
        """
    <summary>
        Indicates whether the fill should be rotated with a shape.
            Read/write <see cref="T:Spire.Presentation.TriState" />.
    </summary>
        """
        GetDllLibPpt().LineFillFormat_get_RotateWithShape.argtypes=[c_void_p]
        GetDllLibPpt().LineFillFormat_get_RotateWithShape.restype=c_int
        ret = CallCFunction(GetDllLibPpt().LineFillFormat_get_RotateWithShape,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @RotateWithShape.setter
    def RotateWithShape(self, value:'TriState'):
        GetDllLibPpt().LineFillFormat_set_RotateWithShape.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().LineFillFormat_set_RotateWithShape,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().LineFillFormat_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().LineFillFormat_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().LineFillFormat_Equals,self.Ptr, intPtrobj)
        return ret

    def GetHashCode(self)->int:
        """

        """
        GetDllLibPpt().LineFillFormat_GetHashCode.argtypes=[c_void_p]
        GetDllLibPpt().LineFillFormat_GetHashCode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().LineFillFormat_GetHashCode,self.Ptr)
        return ret

