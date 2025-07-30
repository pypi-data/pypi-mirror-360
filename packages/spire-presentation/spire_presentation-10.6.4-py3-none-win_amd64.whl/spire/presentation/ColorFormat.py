from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ColorFormat (  PptObject) :
    """
    <summary>
        Represents the color of a one-color object
    </summary>
    """
    @property

    def Color(self)->'Color':
        """
    <summary>
        Gets or Sets RGB colors.
            Read/write <see cref="P:Spire.Presentation.Drawing.ColorFormat.Color" />.
    </summary>
        """
        GetDllLibPpt().ColorFormat_get_Color.argtypes=[c_void_p]
        GetDllLibPpt().ColorFormat_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ColorFormat_get_Color,self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


    @Color.setter
    def Color(self, value:'Color'):
        GetDllLibPpt().ColorFormat_set_Color.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ColorFormat_set_Color,self.Ptr, value.Ptr)

    @property

    def ColorType(self)->'ColorType':
        """
    <summary>
        Gets or sets color type.
    </summary>
        """
        GetDllLibPpt().ColorFormat_get_ColorType.argtypes=[c_void_p]
        GetDllLibPpt().ColorFormat_get_ColorType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ColorFormat_get_ColorType,self.Ptr)
        objwraped = ColorType(ret)
        return objwraped

    @ColorType.setter
    def ColorType(self, value:'ColorType'):
        GetDllLibPpt().ColorFormat_set_ColorType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ColorFormat_set_ColorType,self.Ptr, value.value)

    @property

    def KnownColor(self)->'KnownColors':
        """
    <summary>
        Gets or sets the color preset.
            Read/write <see cref="P:Spire.Presentation.Drawing.ColorFormat.KnownColor" />.
    </summary>
        """
        GetDllLibPpt().ColorFormat_get_KnownColor.argtypes=[c_void_p]
        GetDllLibPpt().ColorFormat_get_KnownColor.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ColorFormat_get_KnownColor,self.Ptr)
        objwraped = KnownColors(ret)
        return objwraped

    @KnownColor.setter
    def KnownColor(self, value:'KnownColors'):
        GetDllLibPpt().ColorFormat_set_KnownColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ColorFormat_set_KnownColor,self.Ptr, value.value)

    @property

    def SystemColor(self)->'SystemColorType':
        """
    <summary>
        Gets or sets the color identified by the system color table.
            Read/write <see cref="P:Spire.Presentation.Drawing.ColorFormat.SystemColor" />.
    </summary>
        """
        GetDllLibPpt().ColorFormat_get_SystemColor.argtypes=[c_void_p]
        GetDllLibPpt().ColorFormat_get_SystemColor.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ColorFormat_get_SystemColor,self.Ptr)
        objwraped = SystemColorType(ret)
        return objwraped

    @SystemColor.setter
    def SystemColor(self, value:'SystemColorType'):
        GetDllLibPpt().ColorFormat_set_SystemColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ColorFormat_set_SystemColor,self.Ptr, value.value)

    @property

    def SchemeColor(self)->'SchemeColor':
        """
    <summary>
        Gets or sets the color identified by a color scheme.
            Read/write <see cref="P:Spire.Presentation.Drawing.ColorFormat.SchemeColor" />.
    </summary>
        """
        GetDllLibPpt().ColorFormat_get_SchemeColor.argtypes=[c_void_p]
        GetDllLibPpt().ColorFormat_get_SchemeColor.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ColorFormat_get_SchemeColor,self.Ptr)
        objwraped = SchemeColor(ret)
        return objwraped

    @SchemeColor.setter
    def SchemeColor(self, value:'SchemeColor'):
        GetDllLibPpt().ColorFormat_set_SchemeColor.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ColorFormat_set_SchemeColor,self.Ptr, value.value)

    @property
    def R(self)->int:
        """
    <summary>
        Gets or sets the red component of a color. All color transformations are ignored.
            Read/write <see cref="T:System.Byte" />.
    </summary>
        """
        GetDllLibPpt().ColorFormat_get_R.argtypes=[c_void_p]
        GetDllLibPpt().ColorFormat_get_R.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ColorFormat_get_R,self.Ptr)
        return ret

    @R.setter
    def R(self, value:int):
        GetDllLibPpt().ColorFormat_set_R.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ColorFormat_set_R,self.Ptr, value)

    @property
    def G(self)->int:
        """
    <summary>
        Gets or sets the green component of a color. 
            Read/write <see cref="T:System.Byte" />.
    </summary>
        """
        GetDllLibPpt().ColorFormat_get_G.argtypes=[c_void_p]
        GetDllLibPpt().ColorFormat_get_G.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ColorFormat_get_G,self.Ptr)
        return ret

    @G.setter
    def G(self, value:int):
        GetDllLibPpt().ColorFormat_set_G.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ColorFormat_set_G,self.Ptr, value)

    @property
    def B(self)->int:
        """
    <summary>
        Gets or sets the blue component of a color.
            Read/write <see cref="T:System.Byte" />.
    </summary>
        """
        GetDllLibPpt().ColorFormat_get_B.argtypes=[c_void_p]
        GetDllLibPpt().ColorFormat_get_B.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ColorFormat_get_B,self.Ptr)
        return ret

    @B.setter
    def B(self, value:int):
        GetDllLibPpt().ColorFormat_set_B.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ColorFormat_set_B,self.Ptr, value)

    @property
    def Hue(self)->float:
        """
    <summary>
        Gets or sets the hue component of a color in HSL representation.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().ColorFormat_get_Hue.argtypes=[c_void_p]
        GetDllLibPpt().ColorFormat_get_Hue.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ColorFormat_get_Hue,self.Ptr)
        return ret

    @Hue.setter
    def Hue(self, value:float):
        GetDllLibPpt().ColorFormat_set_Hue.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ColorFormat_set_Hue,self.Ptr, value)

    @property
    def Saturation(self)->float:
        """
    <summary>
        Gets or sets the saturation component of a color in HSL representation.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().ColorFormat_get_Saturation.argtypes=[c_void_p]
        GetDllLibPpt().ColorFormat_get_Saturation.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ColorFormat_get_Saturation,self.Ptr)
        return ret

    @Saturation.setter
    def Saturation(self, value:float):
        GetDllLibPpt().ColorFormat_set_Saturation.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ColorFormat_set_Saturation,self.Ptr, value)

    @property
    def Luminance(self)->float:
        """
    <summary>
        Gets or sets the luminance component of a color in HSL representation.
            Read/write <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().ColorFormat_get_Luminance.argtypes=[c_void_p]
        GetDllLibPpt().ColorFormat_get_Luminance.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ColorFormat_get_Luminance,self.Ptr)
        return ret

    @Luminance.setter
    def Luminance(self, value:float):
        GetDllLibPpt().ColorFormat_set_Luminance.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ColorFormat_set_Luminance,self.Ptr, value)


    def Equals(self ,obj:'SpireObject')->bool:
        """
    <summary>
        Indicates whether the two ColorFormat instances are equal.
    </summary>
    <param name="obj">The ColorFormat to compare with the current ColorFormat.</param>
    <returns>
  <b>true</b> if the specified ColorFormat is equal to the current ColorFormat; otherwise, <b>false</b>.</returns>
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().ColorFormat_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ColorFormat_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ColorFormat_Equals,self.Ptr, intPtrobj)
        return ret

    def GetHashCode(self)->int:
        """

        """
        GetDllLibPpt().ColorFormat_GetHashCode.argtypes=[c_void_p]
        GetDllLibPpt().ColorFormat_GetHashCode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ColorFormat_GetHashCode,self.Ptr)
        return ret
    

    @property

    def Transparency(self)->'float':
        """
    <summary>
     
    </summary>
        """
        GetDllLibPpt().ColorFormat_get_Transparency.argtypes=[c_void_p]
        GetDllLibPpt().ColorFormat_get_Transparency.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ColorFormat_get_Transparency,self.Ptr)
        return ret


    @Transparency.setter
    def Transparency(self, value:'float'):
        GetDllLibPpt().ColorFormat_set_Transparency.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ColorFormat_set_Transparency,self.Ptr, value)


    @property

    def Brightness(self)->'float':
        """
    <summary>
     
    </summary>
        """
        GetDllLibPpt().ColorFormat_get_Brightness.argtypes=[c_void_p]
        GetDllLibPpt().ColorFormat_get_Brightness.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ColorFormat_get_Brightness,self.Ptr)
        return ret


    @Brightness.setter
    def Brightness(self, value:'float'):
        GetDllLibPpt().ColorFormat_set_Brightness.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ColorFormat_set_Brightness,self.Ptr, value)

