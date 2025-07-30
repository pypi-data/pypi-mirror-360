from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LocaleFonts (SpireObject) :
    """
    <summary>
        Fonts collection.
    </summary>
    """
    @property

    def LatinFont(self)->'TextFont':
        """
    <summary>
        Gets or sets the Latin font.
            Read/write <see cref="T:Spire.Presentation.TextFont" />.
    </summary>
        """
        GetDllLibPpt().LocaleFonts_get_LatinFont.argtypes=[c_void_p]
        GetDllLibPpt().LocaleFonts_get_LatinFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().LocaleFonts_get_LatinFont,self.Ptr)
        ret = None if intPtr==None else TextFont(intPtr)
        return ret


    @LatinFont.setter
    def LatinFont(self, value:'TextFont'):
        GetDllLibPpt().LocaleFonts_set_LatinFont.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().LocaleFonts_set_LatinFont,self.Ptr, value.Ptr)

    @property

    def EastAsianFont(self)->'TextFont':
        """
    <summary>
        Gets or sets the East Asian font.
            Read/write <see cref="T:Spire.Presentation.TextFont" />.
    </summary>
        """
        GetDllLibPpt().LocaleFonts_get_EastAsianFont.argtypes=[c_void_p]
        GetDllLibPpt().LocaleFonts_get_EastAsianFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().LocaleFonts_get_EastAsianFont,self.Ptr)
        ret = None if intPtr==None else TextFont(intPtr)
        return ret


    @EastAsianFont.setter
    def EastAsianFont(self, value:'TextFont'):
        GetDllLibPpt().LocaleFonts_set_EastAsianFont.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().LocaleFonts_set_EastAsianFont,self.Ptr, value.Ptr)

    @property

    def ComplexScriptFont(self)->'TextFont':
        """
    <summary>
        Gets or sets the complex script font.
            Read/write <see cref="T:Spire.Presentation.TextFont" />.
    </summary>
        """
        GetDllLibPpt().LocaleFonts_get_ComplexScriptFont.argtypes=[c_void_p]
        GetDllLibPpt().LocaleFonts_get_ComplexScriptFont.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().LocaleFonts_get_ComplexScriptFont,self.Ptr)
        ret = None if intPtr==None else TextFont(intPtr)
        return ret


    @ComplexScriptFont.setter
    def ComplexScriptFont(self, value:'TextFont'):
        GetDllLibPpt().LocaleFonts_set_ComplexScriptFont.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().LocaleFonts_set_ComplexScriptFont,self.Ptr, value.Ptr)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().LocaleFonts_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().LocaleFonts_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().LocaleFonts_Equals,self.Ptr, intPtrobj)
        return ret

