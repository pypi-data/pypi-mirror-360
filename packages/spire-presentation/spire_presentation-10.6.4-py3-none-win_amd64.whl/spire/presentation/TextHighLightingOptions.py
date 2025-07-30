from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextHighLightingOptions (SpireObject) :

    @dispatch
    def __init__(self):
        GetDllLibPpt().TextHighLightingOptions_Create.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextHighLightingOptions_Create)
        super(TextHighLightingOptions, self).__init__(intPtr)
    """

    """
    @property
    def CaseSensitive(self)->bool:
        """
    <summary>
        Set true to use case-sensitive search,false-otherwise. Red/write System.Boolean.
    </summary>
        """
        GetDllLibPpt().TextHighLightingOptions_get_CaseSensitive.argtypes=[c_void_p]
        GetDllLibPpt().TextHighLightingOptions_get_CaseSensitive.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextHighLightingOptions_get_CaseSensitive,self.Ptr)
        return ret

    @CaseSensitive.setter
    def CaseSensitive(self, value:bool):
        GetDllLibPpt().TextHighLightingOptions_set_CaseSensitive.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().TextHighLightingOptions_set_CaseSensitive,self.Ptr, value)

    @property
    def WholeWordsOnly(self)->bool:
        """
    <summary>
        Set true to match only whole words,false-otherwise. Red/write System.Boolean.
    </summary>
        """
        GetDllLibPpt().TextHighLightingOptions_get_WholeWordsOnly.argtypes=[c_void_p]
        GetDllLibPpt().TextHighLightingOptions_get_WholeWordsOnly.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextHighLightingOptions_get_WholeWordsOnly,self.Ptr)
        return ret

    @WholeWordsOnly.setter
    def WholeWordsOnly(self, value:bool):
        GetDllLibPpt().TextHighLightingOptions_set_WholeWordsOnly.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().TextHighLightingOptions_set_WholeWordsOnly,self.Ptr, value)

