from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class AnimationEffect (  PptObject) :
    """
    <summary>
        Represents timing information about a slide animation.
    </summary>
    """
    @property

    def TimeNodeAudios(self)->List['TimeNodeAudio']:
        """
    <summary>
        TimeNodeAudios
    </summary>
        """
        GetDllLibPpt().AnimationEffect_get_TimeNodeAudios.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffect_get_TimeNodeAudios.restype=IntPtrArray
        intPtrArray = CallCFunction(GetDllLibPpt().AnimationEffect_get_TimeNodeAudios,self.Ptr)
        ret = GetObjVectorFromArray(intPtrArray, TimeNodeAudio)
        return ret


    @property
    def IterateTimeValue(self)->float:
        """
    <summary>
        if the value is less than 0,
            this element describes the duration of the iteration interval in absolute time.
            if the value is greater than 0,
            this element describes the duration of the iteration interval in percentage of time.
    </summary>
        """
        GetDllLibPpt().AnimationEffect_get_IterateTimeValue.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffect_get_IterateTimeValue.restype=c_float
        ret = CallCFunction(GetDllLibPpt().AnimationEffect_get_IterateTimeValue,self.Ptr)
        return ret

    @IterateTimeValue.setter
    def IterateTimeValue(self, value:float):
        GetDllLibPpt().AnimationEffect_set_IterateTimeValue.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().AnimationEffect_set_IterateTimeValue,self.Ptr, value)

    @property

    def IterateType(self)->'AnimateType':
        """

        """
        GetDllLibPpt().AnimationEffect_get_IterateType.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffect_get_IterateType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationEffect_get_IterateType,self.Ptr)
        objwraped = AnimateType(ret)
        return objwraped

    @IterateType.setter
    def IterateType(self, value:'AnimateType'):
        GetDllLibPpt().AnimationEffect_set_IterateType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AnimationEffect_set_IterateType,self.Ptr, value.value)

    @property

    def Effects(self)->'AnimationEffectCollection':
        """
    <summary>
        Gets a sequence for an effect.
            Read-only <see cref="P:Spire.Presentation.Drawing.Animation.AnimationEffect.Effects" />.
    </summary>
        """
        GetDllLibPpt().AnimationEffect_get_Effects.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffect_get_Effects.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationEffect_get_Effects,self.Ptr)
        ret = None if intPtr==None else AnimationEffectCollection(intPtr)
        return ret


    @property

    def TextAnimation(self)->'TextAnimation':
        """
<summary></summary>
        """
        GetDllLibPpt().AnimationEffect_get_TextAnimation.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffect_get_TextAnimation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationEffect_get_TextAnimation,self.Ptr)
        ret = None if intPtr==None else TextAnimation(intPtr)
        return ret


    @property

    def GraphicAnimation(self)->'GraphicAnimation':
        """

        """
        GetDllLibPpt().AnimationEffect_get_GraphicAnimation.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffect_get_GraphicAnimation.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationEffect_get_GraphicAnimation,self.Ptr)
        ret = None if intPtr==None else GraphicAnimation(intPtr)
        return ret


    @property

    def ShapeTarget(self)->'Shape':
        """
    <summary>
        Returns the shape that is applied with the specific animation effect.
    </summary>
        """
        GetDllLibPpt().AnimationEffect_get_ShapeTarget.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffect_get_ShapeTarget.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationEffect_get_ShapeTarget,self.Ptr)
        ret = None if intPtr==None else Shape(intPtr)
        return ret


    @property

    def PresetClassType(self)->'TimeNodePresetClassType':
        """
    <summary>
        Defines class of effect.
            Read/write <see cref="T:Spire.Presentation.Drawing.Animation.TimeNodePresetClassType" />.
    </summary>
        """
        GetDllLibPpt().AnimationEffect_get_PresetClassType.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffect_get_PresetClassType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationEffect_get_PresetClassType,self.Ptr)
        objwraped = TimeNodePresetClassType(ret)
        return objwraped

    @PresetClassType.setter
    def PresetClassType(self, value:'TimeNodePresetClassType'):
        GetDllLibPpt().AnimationEffect_set_PresetClassType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AnimationEffect_set_PresetClassType,self.Ptr, value.value)

    @property

    def AnimationEffectType(self)->'AnimationEffectType':
        """
    <summary>
        Defines type of effect.
            Read/write <see cref="P:Spire.Presentation.Drawing.Animation.AnimationEffect.AnimationEffectType" />.
    </summary>
        """
        GetDllLibPpt().AnimationEffect_get_AnimationEffectType.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffect_get_AnimationEffectType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationEffect_get_AnimationEffectType,self.Ptr)
        objwraped = AnimationEffectType(ret)
        return objwraped

    @AnimationEffectType.setter
    def AnimationEffectType(self, value:'AnimationEffectType'):
        GetDllLibPpt().AnimationEffect_set_AnimationEffectType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AnimationEffect_set_AnimationEffectType,self.Ptr, value.value)

    @property

    def Subtype(self)->'AnimationEffectSubtype':
        """

        """
        GetDllLibPpt().AnimationEffect_get_Subtype.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffect_get_Subtype.restype=c_int
        ret = CallCFunction(GetDllLibPpt().AnimationEffect_get_Subtype,self.Ptr)
        objwraped = AnimationEffectSubtype(ret)
        return objwraped

    @Subtype.setter
    def Subtype(self, value:'AnimationEffectSubtype'):
        GetDllLibPpt().AnimationEffect_set_Subtype.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().AnimationEffect_set_Subtype,self.Ptr, value.value)

    @property

    def CommonBehaviorCollection(self)->'CommonBehaviorCollection':
        """
    <summary>
        Gets collection of behavior for effect.
            Read/write <see cref="P:Spire.Presentation.Drawing.Animation.AnimationEffect.CommonBehaviorCollection" />.
    </summary>
        """
        from spire.presentation import CommonBehaviorCollection
        GetDllLibPpt().AnimationEffect_get_CommonBehaviorCollection.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffect_get_CommonBehaviorCollection.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationEffect_get_CommonBehaviorCollection,self.Ptr)
        ret = None if intPtr==None else CommonBehaviorCollection(intPtr)
        return ret


    @CommonBehaviorCollection.setter
    def CommonBehaviorCollection(self, value:'CommonBehaviorCollection'):
        GetDllLibPpt().AnimationEffect_set_CommonBehaviorCollection.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().AnimationEffect_set_CommonBehaviorCollection,self.Ptr, value.Ptr)

    @property

    def Timing(self)->'Timing':
        """
    <summary>
        Defines timing value for effect.
            Read/write <see cref="T:Spire.Presentation.Drawing.Animation.Timing" />.
    </summary>
        """
        from spire.presentation import Timing;
        GetDllLibPpt().AnimationEffect_get_Timing.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffect_get_Timing.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationEffect_get_Timing,self.Ptr)
        ret = None if intPtr==None else Timing(intPtr)
        return ret


    @Timing.setter
    def Timing(self, value:'Timing'):
        GetDllLibPpt().AnimationEffect_set_Timing.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().AnimationEffect_set_Timing,self.Ptr, value.Ptr)

    @property

    def StartParagraph(self)->'TextParagraph':
        """
    <summary>
        Starting text paragraph which effect is applied to.
            Read-only
    </summary>
        """
        GetDllLibPpt().AnimationEffect_get_StartParagraph.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffect_get_StartParagraph.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationEffect_get_StartParagraph,self.Ptr)
        ret = None if intPtr==None else TextParagraph(intPtr)
        return ret


    @property

    def EndParagraph(self)->'TextParagraph':
        """
    <summary>
        Ending text paragraph which effect is applied to.
            Read-only
    </summary>
        """
        GetDllLibPpt().AnimationEffect_get_EndParagraph.argtypes=[c_void_p]
        GetDllLibPpt().AnimationEffect_get_EndParagraph.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().AnimationEffect_get_EndParagraph,self.Ptr)
        ret = None if intPtr==None else TextParagraph(intPtr)
        return ret



    def SetStartEndParagraphs(self ,startParaIndex:int,endParaIndex:int):
        """
    <summary>
        Starting and Ending text paragraph which effect is applied to.
    </summary>
        """
        
        GetDllLibPpt().AnimationEffect_SetStartEndParagraphs.argtypes=[c_void_p ,c_int,c_int]
        CallCFunction(GetDllLibPpt().AnimationEffect_SetStartEndParagraphs,self.Ptr, startParaIndex,endParaIndex)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().AnimationEffect_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().AnimationEffect_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().AnimationEffect_Equals,self.Ptr, intPtrobj)
        return ret

