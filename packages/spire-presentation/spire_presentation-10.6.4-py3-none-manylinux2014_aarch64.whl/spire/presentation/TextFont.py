from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextFont (SpireObject) :

    @dispatch
    def __init__(self):
        GetDllLibPpt().Creat_TextFont.argtypes=[c_wchar_p]
        GetDllLibPpt().Creat_TextFont.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Creat_TextFont,'Arail')
        super(TextFont, self).__init__(intPtr)

    @dispatch
    def __init__(self,fontName:str):
        fontNamePtr = StrToPtr(fontName)
        GetDllLibPpt().Creat_TextFont.argtypes=[c_char_p]
        GetDllLibPpt().Creat_TextFont.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Creat_TextFont,fontNamePtr)
        super(TextFont, self).__init__(intPtr)
    """
    <summary>
        Represents a font definition. Immutable.
    </summary>
    """
    @property

    def FontName(self)->str:
        """
    <summary>
        Gets the font name. Read-only <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().TextFont_get_FontName.argtypes=[c_void_p]
        GetDllLibPpt().TextFont_get_FontName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().TextFont_get_FontName,self.Ptr))
        return ret


    @FontName.setter
    def FontName(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().TextFont_set_FontName.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().TextFont_set_FontName,self.Ptr,valuePtr)


    def GetFontName(self ,theme:'Theme')->str:
        """
    <summary>
        Gets the font name, replacing theme referrence with an actual font used.
    </summary>
    <param name="theme">Theme from which themed font name should be taken. Its up to caller to provide a correct value. See <see cref="P:Spire.Presentation.ActiveSlide.Theme" /></param>
    <returns>Font name.</returns>
        """
        intPtrtheme:c_void_p = theme.Ptr

        GetDllLibPpt().TextFont_GetFontName.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TextFont_GetFontName.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().TextFont_GetFontName,self.Ptr, intPtrtheme))
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """
    <summary>
        Indicates whether two FontData instances are equal.
    </summary>
    <param name="obj">The FontData to compare with the current FontData.</param>
    <returns>
  <b>true</b> if the specified FontData is equal to the current FontData; otherwise, <b>false</b>.</returns>
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TextFont_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TextFont_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextFont_Equals,self.Ptr, intPtrobj)
        return ret

    def GetHashCode(self)->int:
        """

        """
        GetDllLibPpt().TextFont_GetHashCode.argtypes=[c_void_p]
        GetDllLibPpt().TextFont_GetHashCode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextFont_GetHashCode,self.Ptr)
        return ret

