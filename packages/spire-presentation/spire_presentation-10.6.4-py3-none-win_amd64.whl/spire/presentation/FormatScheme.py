from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FormatScheme (  PptObject, IActiveSlide, IActivePresentation) :
    """
    <summary>
        Stores theme-defined formats for the shapes.
    </summary>
    """
    @property

    def FillStyles(self)->'FillStyleCollection':
        """
    <summary>
        Gets a collection of theme defined fill styles.
            Readonly <see cref="T:Spire.Presentation.Drawing.FillStyleCollection" />.
    </summary>
        """
        GetDllLibPpt().FormatScheme_get_FillStyles.argtypes=[c_void_p]
        GetDllLibPpt().FormatScheme_get_FillStyles.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FormatScheme_get_FillStyles,self.Ptr)
        ret = None if intPtr==None else FillStyleCollection(intPtr)
        return ret


    @property

    def LineStyles(self)->'LineStyleCollection':
        """
    <summary>
        Gets a collection of theme defined line styles.
            Readonly <see cref="T:Spire.Presentation.Collections.LineStyleCollection" />.
    </summary>
        """
        GetDllLibPpt().FormatScheme_get_LineStyles.argtypes=[c_void_p]
        GetDllLibPpt().FormatScheme_get_LineStyles.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FormatScheme_get_LineStyles,self.Ptr)
        ret = None if intPtr==None else LineStyleCollection(intPtr)
        return ret


    @property

    def EffectStyles(self)->'EffectStyleCollection':
        """
    <summary>
        Gets a collection of theme defined effect styles.
            Readonly <see cref="T:Spire.Presentation.Collections.EffectStyleCollection" />.
    </summary>
        """
        GetDllLibPpt().FormatScheme_get_EffectStyles.argtypes=[c_void_p]
        GetDllLibPpt().FormatScheme_get_EffectStyles.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FormatScheme_get_EffectStyles,self.Ptr)
        ret = None if intPtr==None else EffectStyleCollection(intPtr)
        return ret


    @property

    def BackgroundFillStyles(self)->'FillStyleCollection':
        """
    <summary>
        Gets a collection of theme defined background fill styles.
            Readonly <see cref="T:Spire.Presentation.Drawing.FillStyleCollection" />.
    </summary>
        """
        GetDllLibPpt().FormatScheme_get_BackgroundFillStyles.argtypes=[c_void_p]
        GetDllLibPpt().FormatScheme_get_BackgroundFillStyles.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FormatScheme_get_BackgroundFillStyles,self.Ptr)
        ret = None if intPtr==None else FillStyleCollection(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().FormatScheme_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().FormatScheme_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().FormatScheme_Equals,self.Ptr, intPtrobj)
        return ret

    @property

    def Slide(self)->'ActiveSlide':
        """
    <summary>
        Gets the parent slide.
            Read-only <see cref="T:Spire.Presentation.ActiveSlide" />.
    </summary>
        """
        GetDllLibPpt().FormatScheme_get_Slide.argtypes=[c_void_p]
        GetDllLibPpt().FormatScheme_get_Slide.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FormatScheme_get_Slide,self.Ptr)
        ret = None if intPtr==None else ActiveSlide(intPtr)
        return ret


    @property

    def Presentation(self)->'Presentation':
        """

        """
        GetDllLibPpt().FormatScheme_get_Presentation.argtypes=[c_void_p]
        GetDllLibPpt().FormatScheme_get_Presentation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FormatScheme_get_Presentation,self.Ptr)
        ret = None if intPtr==None else Presentation(intPtr)
        return ret


    @property

    def Name(self)->str:
        """
    <summary>
        Gets the font scheme name.
            Readonly string.
    </summary>
        """
        GetDllLibPpt().FormatScheme_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().FormatScheme_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().FormatScheme_get_Name,self.Ptr))
        return ret


    @Name.setter
    def Name(self, value:str):
        valuePtr = StrToPtr(value)
        GetDllLibPpt().FormatScheme_set_Name.argtypes=[c_void_p, c_char_p]
        CallCFunction(GetDllLibPpt().FormatScheme_set_Name,self.Ptr,valuePtr)

