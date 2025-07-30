from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationFilterEffect (  CommonBehavior) :
    """
    <summary>
        Represents a filter effect for an animation behavior..
    </summary>
    """
    @property

    def Reveal(self)->'FilterRevealType':
        """
    <summary>
        Determines how the embedded objects will be revealed.
            Read/write <see cref="T:Spire.Presentation.Drawing.Animation.FilterRevealType" />.
    </summary>
        """
        GetDllLibPpt().AnimationFilterEffect_get_Reveal.argtypes=[c_void_p]
        GetDllLibPpt().AnimationFilterEffect_get_Reveal.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationFilterEffect_get_Reveal,self.Ptr)
        objwraped = FilterRevealType(ret)
        return objwraped

    @Reveal.setter
    def Reveal(self, value:'FilterRevealType'):
        GetDllLibPpt().AnimationFilterEffect_set_Reveal.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AnimationFilterEffect_set_Reveal,self.Ptr, value.value)

    @property

    def Type(self)->'FilterEffectType':
        """
    <summary>
        Represents the type of animation
            Read/write <see cref="T:Spire.Presentation.Drawing.Animation.FilterEffectType" />.
    </summary>
        """
        GetDllLibPpt().AnimationFilterEffect_get_Type.argtypes=[c_void_p]
        GetDllLibPpt().AnimationFilterEffect_get_Type.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationFilterEffect_get_Type,self.Ptr)
        objwraped = FilterEffectType(ret)
        return objwraped

    @Type.setter
    def Type(self, value:'FilterEffectType'):
        GetDllLibPpt().AnimationFilterEffect_set_Type.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AnimationFilterEffect_set_Type,self.Ptr, value.value)

    @property

    def Subtype(self)->'FilterEffectSubtype':
        """
    <summary>
        Sets or returns the subtype of the filter effect.
            Read/write <see cref="T:Spire.Presentation.Drawing.Animation.FilterEffectSubtype" />.
    </summary>
        """
        GetDllLibPpt().AnimationFilterEffect_get_Subtype.argtypes=[c_void_p]
        GetDllLibPpt().AnimationFilterEffect_get_Subtype.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationFilterEffect_get_Subtype,self.Ptr)
        objwraped = FilterEffectSubtype(ret)
        return objwraped

    @Subtype.setter
    def Subtype(self, value:'FilterEffectSubtype'):
        GetDllLibPpt().AnimationFilterEffect_set_Subtype.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AnimationFilterEffect_set_Subtype,self.Ptr, value.value)

