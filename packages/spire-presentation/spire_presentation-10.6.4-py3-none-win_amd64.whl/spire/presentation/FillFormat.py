from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FillFormat (  IActiveSlide) :
    """
    <summary>
        Represents a fill formatting options.
    </summary>
    """
    @property

    def FillType(self)->'FillFormatType':
        """
    <summary>
        Gets or sets the type of filling.
            Read/write <see cref="P:Spire.Presentation.Drawing.FillFormat.FillType" />.
    </summary>
        """
        GetDllLibPpt().FillFormat_get_FillType.argtypes=[c_void_p]
        GetDllLibPpt().FillFormat_get_FillType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().FillFormat_get_FillType,self.Ptr)
        objwraped = FillFormatType(ret)
        return objwraped

    @FillType.setter
    def FillType(self, value:'FillFormatType'):
        GetDllLibPpt().FillFormat_set_FillType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().FillFormat_set_FillType,self.Ptr, value.value)

    @property
    def IsGroupFill(self)->bool:
        """
    <summary>
        Indicate whether is Group fill.
    </summary>
        """
        GetDllLibPpt().FillFormat_get_IsGroupFill.argtypes=[c_void_p]
        GetDllLibPpt().FillFormat_get_IsGroupFill.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().FillFormat_get_IsGroupFill,self.Ptr)
        return ret

    @IsGroupFill.setter
    def IsGroupFill(self, value:bool):
        GetDllLibPpt().FillFormat_set_IsGroupFill.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().FillFormat_set_IsGroupFill,self.Ptr, value)

    @property
    def IsNoFill(self)->bool:
        """
    <summary>
        Indicates whether is No Fill.
    </summary>
        """
        GetDllLibPpt().FillFormat_get_IsNoFill.argtypes=[c_void_p]
        GetDllLibPpt().FillFormat_get_IsNoFill.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().FillFormat_get_IsNoFill,self.Ptr)
        return ret

    @property

    def SolidColor(self)->'ColorFormat':
        """
    <summary>
        Gets the fill color.
            Read-only <see cref="T:Spire.Presentation.Drawing.ColorFormat" />.
    </summary>
        """
        GetDllLibPpt().FillFormat_get_SolidColor.argtypes=[c_void_p]
        GetDllLibPpt().FillFormat_get_SolidColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FillFormat_get_SolidColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @property

    def Gradient(self)->'GradientFillFormat':
        """
    <summary>
        Gets the gradient fill format.
            Read-only <see cref="P:Spire.Presentation.Drawing.FillFormat.Gradient" />.
    </summary>
        """
        GetDllLibPpt().FillFormat_get_Gradient.argtypes=[c_void_p]
        GetDllLibPpt().FillFormat_get_Gradient.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FillFormat_get_Gradient,self.Ptr)
        ret = None if intPtr==None else GradientFillFormat(intPtr)
        return ret


    @property

    def Pattern(self)->'PatternFillFormat':
        """
    <summary>
        Gets the pattern fill format.
            Read-only <see cref="P:Spire.Presentation.Drawing.FillFormat.Pattern" />.
    </summary>
        """
        GetDllLibPpt().FillFormat_get_Pattern.argtypes=[c_void_p]
        GetDllLibPpt().FillFormat_get_Pattern.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FillFormat_get_Pattern,self.Ptr)
        ret = None if intPtr==None else PatternFillFormat(intPtr)
        return ret


    @property

    def PictureFill(self)->'PictureFillFormat':
        """
    <summary>
        Gets the picture fill format.
            Read-only <see cref="P:Spire.Presentation.Drawing.FillFormat.PictureFill" />.
    </summary>
        """
        GetDllLibPpt().FillFormat_get_PictureFill.argtypes=[c_void_p]
        GetDllLibPpt().FillFormat_get_PictureFill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FillFormat_get_PictureFill,self.Ptr)
        ret = None if intPtr==None else PictureFillFormat(intPtr)
        return ret


    @property

    def RotateWithShape(self)->'TriState':
        """
    <summary>
        Indicates whether the fill would be rotated with shape.
            Read/write <see cref="T:Spire.Presentation.TriState" />.
    </summary>
        """
        GetDllLibPpt().FillFormat_get_RotateWithShape.argtypes=[c_void_p]
        GetDllLibPpt().FillFormat_get_RotateWithShape.restype=c_int
        ret = CallCFunction(GetDllLibPpt().FillFormat_get_RotateWithShape,self.Ptr)
        objwraped = TriState(ret)
        return objwraped

    @RotateWithShape.setter
    def RotateWithShape(self, value:'TriState'):
        GetDllLibPpt().FillFormat_set_RotateWithShape.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().FillFormat_set_RotateWithShape,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """
    <summary>
        Indicates whether two FillFormat instances are equal.
    </summary>
    <param name="obj">The FillFormat to compare with the current FillFormat.</param>
    <returns>
  <b>true</b> if the specified FillFormat is equal to the current FillFormat; otherwise, <b>false</b>.</returns>
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().FillFormat_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().FillFormat_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().FillFormat_Equals,self.Ptr, intPtrobj)
        return ret

    def GetHashCode(self)->int:
        """

        """
        GetDllLibPpt().FillFormat_GetHashCode.argtypes=[c_void_p]
        GetDllLibPpt().FillFormat_GetHashCode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().FillFormat_GetHashCode,self.Ptr)
        return ret

