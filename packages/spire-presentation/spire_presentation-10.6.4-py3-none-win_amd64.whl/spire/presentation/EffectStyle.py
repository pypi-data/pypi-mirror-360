from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class EffectStyle (SpireObject) :
    """
    <summary>
        Represents an effect style.
    </summary>
    """
    @property

    def EffectDag(self)->'EffectDag':
        """
    <summary>
        Gets an effect format.
            Readonly <see cref="P:Spire.Presentation.Drawing.EffectStyle.EffectDag" />.
    </summary>
        """
        GetDllLibPpt().EffectStyle_get_EffectDag.argtypes=[c_void_p]
        GetDllLibPpt().EffectStyle_get_EffectDag.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectStyle_get_EffectDag,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def FormatThreeDFormat(self)->'FormatThreeD':
        """
    <summary>
        Gets an 3d format.
            Readonly <see cref="T:Spire.Presentation.Drawing.FormatThreeD" />.
    </summary>
        """
        GetDllLibPpt().EffectStyle_get_FormatThreeDFormat.argtypes=[c_void_p]
        GetDllLibPpt().EffectStyle_get_FormatThreeDFormat.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectStyle_get_FormatThreeDFormat,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().EffectStyle_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().EffectStyle_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().EffectStyle_Equals,self.Ptr, intPtrobj)
        return ret

