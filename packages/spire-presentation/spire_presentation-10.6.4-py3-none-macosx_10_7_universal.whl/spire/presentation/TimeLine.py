from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TimeLine (  PptObject) :
    """
    <summary>
        Represent timline of animation.
    </summary>
    """
    @property

    def InteractiveSequences(self)->'SequenceCollection':
        """
    <summary>
        Gets collection of interactive sequences.
    </summary>
        """
        GetDllLibPpt().TimeLine_get_InteractiveSequences.argtypes=[c_void_p]
        GetDllLibPpt().TimeLine_get_InteractiveSequences.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TimeLine_get_InteractiveSequences,self.Ptr)
        ret = None if intPtr==None else SequenceCollection(intPtr)
        return ret


    @property

    def MainSequence(self)->'AnimationEffectCollection':
        """
    <summary>
        Gets main sequence which may contain only main effects collection.
    </summary>
        """
        GetDllLibPpt().TimeLine_get_MainSequence.argtypes=[c_void_p]
        GetDllLibPpt().TimeLine_get_MainSequence.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TimeLine_get_MainSequence,self.Ptr)
        ret = None if intPtr==None else AnimationEffectCollection(intPtr)
        return ret


    @property

    def TextAnimations(self)->'TextAnimationCollection':
        """

        """
        GetDllLibPpt().TimeLine_get_TextAnimations.argtypes=[c_void_p]
        GetDllLibPpt().TimeLine_get_TextAnimations.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TimeLine_get_TextAnimations,self.Ptr)
        ret = None if intPtr==None else TextAnimationCollection(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TimeLine_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TimeLine_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TimeLine_Equals,self.Ptr, intPtrobj)
        return ret

