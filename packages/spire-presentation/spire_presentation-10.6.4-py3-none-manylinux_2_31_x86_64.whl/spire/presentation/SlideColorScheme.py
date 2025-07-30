from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SlideColorScheme (SpireObject) :
    """
    <summary>
        Represents an additional color scheme which can be assigned to a slide.
    </summary>
    """
    @property

    def Name(self)->str:
        """
    <summary>
        Gets a name of this scheme.
    </summary>
        """
        GetDllLibPpt().SlideColorScheme_get_Name.argtypes=[c_void_p]
        GetDllLibPpt().SlideColorScheme_get_Name.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().SlideColorScheme_get_Name,self.Ptr))
        return ret


    @property

    def ColorScheme(self)->'ColorScheme':
        """
    <summary>
        Gets a color scheme.
            Readonly <see cref="T:Spire.Presentation.Drawing.ColorScheme" />.
    </summary>
        """
        GetDllLibPpt().SlideColorScheme_get_ColorScheme.argtypes=[c_void_p]
        GetDllLibPpt().SlideColorScheme_get_ColorScheme.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlideColorScheme_get_ColorScheme,self.Ptr)
        ret = None if intPtr==None else ColorScheme(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().SlideColorScheme_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().SlideColorScheme_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SlideColorScheme_Equals,self.Ptr, intPtrobj)
        return ret

