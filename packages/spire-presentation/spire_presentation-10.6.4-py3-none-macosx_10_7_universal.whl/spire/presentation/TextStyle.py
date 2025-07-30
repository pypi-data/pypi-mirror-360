from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextStyle (  IActiveSlide, IActivePresentation) :
    """
    <summary>
        Summary description for TextStyle.
    </summary>
    """

    def GetListLevelTextStyle(self ,index:int)->'TextParagraphProperties':
        """
    <summary>
        If level of style exist returns it, otherwise returns null.
    </summary>
    <param name="index">zero-based index of level.</param>
    <returns>Formatting of level <see cref="T:Spire.Presentation.TextParagraphProperties" />. </returns>
        """
        
        GetDllLibPpt().TextStyle_GetListLevelTextStyle.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().TextStyle_GetListLevelTextStyle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextStyle_GetListLevelTextStyle,self.Ptr, index)
        ret = None if intPtr==None else TextParagraphProperties(intPtr)
        return ret



    def GetOrCreateListLevelTextStyle(self ,index:int)->'TextParagraphProperties':
        """
    <summary>
        If level of style exist returns it, otherwise create and returns it.
    </summary>
    <param name="index">zero-based index of level.</param>
    <returns>Formatting of level <see cref="T:Spire.Presentation.TextParagraphProperties" />. </returns>
        """
        
        GetDllLibPpt().TextStyle_GetOrCreateListLevelTextStyle.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().TextStyle_GetOrCreateListLevelTextStyle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextStyle_GetOrCreateListLevelTextStyle,self.Ptr, index)
        ret = None if intPtr==None else TextParagraphProperties(intPtr)
        return ret


    @property

    def DefaultParagraphStyle(self)->'TextParagraphProperties':
        """
    <summary>
        Default paragraph propertiies.
    </summary>
        """
        GetDllLibPpt().TextStyle_get_DefaultParagraphStyle.argtypes=[c_void_p]
        GetDllLibPpt().TextStyle_get_DefaultParagraphStyle.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextStyle_get_DefaultParagraphStyle,self.Ptr)
        ret = None if intPtr==None else TextParagraphProperties(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TextStyle_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TextStyle_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextStyle_Equals,self.Ptr, intPtrobj)
        return ret

