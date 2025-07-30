from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class EffectDag (  PptObject, IActiveSlide, IActivePresentation) :
    """
    <summary>
        Represents effect properties of shape.
    </summary>
    """
    @property

    def BlendEffect(self)->'BlendEffect':
        """
    <summary>
        Blur effect.
    </summary>
        """
        GetDllLibPpt().EffectDag_get_BlendEffect.argtypes=[c_void_p]
        GetDllLibPpt().EffectDag_get_BlendEffect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectDag_get_BlendEffect,self.Ptr)
        ret = None if intPtr==None else BlendEffect(intPtr)
        return ret


    @BlendEffect.setter
    def BlendEffect(self, value:'BlendEffect'):
        GetDllLibPpt().EffectDag_set_BlendEffect.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().EffectDag_set_BlendEffect,self.Ptr, value.Ptr)

    @property

    def FillOverlayEffect(self)->'FillOverlayEffect':
        """
    <summary>
        Fill overlay effect.
    </summary>
        """
        GetDllLibPpt().EffectDag_get_FillOverlayEffect.argtypes=[c_void_p]
        GetDllLibPpt().EffectDag_get_FillOverlayEffect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectDag_get_FillOverlayEffect,self.Ptr)
        ret = None if intPtr==None else FillOverlayEffect(intPtr)
        return ret


    @FillOverlayEffect.setter
    def FillOverlayEffect(self, value:'FillOverlayEffect'):
        GetDllLibPpt().EffectDag_set_FillOverlayEffect.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().EffectDag_set_FillOverlayEffect,self.Ptr, value.Ptr)

    @property

    def GlowEffect(self)->'GlowEffect':
        """
    <summary>
        Glow effect.
    </summary>
        """
        GetDllLibPpt().EffectDag_get_GlowEffect.argtypes=[c_void_p]
        GetDllLibPpt().EffectDag_get_GlowEffect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectDag_get_GlowEffect,self.Ptr)
        ret = None if intPtr==None else GlowEffect(intPtr)
        return ret


    @GlowEffect.setter
    def GlowEffect(self, value:'GlowEffect'):
        GetDllLibPpt().EffectDag_set_GlowEffect.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().EffectDag_set_GlowEffect,self.Ptr, value.Ptr)

    @property

    def InnerShadowEffect(self)->'InnerShadowEffect':
        """
    <summary>
        Inner shadow.
    </summary>
        """
        GetDllLibPpt().EffectDag_get_InnerShadowEffect.argtypes=[c_void_p]
        GetDllLibPpt().EffectDag_get_InnerShadowEffect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectDag_get_InnerShadowEffect,self.Ptr)
        ret = None if intPtr==None else InnerShadowEffect(intPtr)
        return ret


    @InnerShadowEffect.setter
    def InnerShadowEffect(self, value:'InnerShadowEffect'):
        GetDllLibPpt().EffectDag_set_InnerShadowEffect.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().EffectDag_set_InnerShadowEffect,self.Ptr, value.Ptr)

    @property

    def OuterShadowEffect(self)->'OuterShadowEffect':
        """
    <summary>
        Outer shadow.
    </summary>
        """
        GetDllLibPpt().EffectDag_get_OuterShadowEffect.argtypes=[c_void_p]
        GetDllLibPpt().EffectDag_get_OuterShadowEffect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectDag_get_OuterShadowEffect,self.Ptr)
        ret = None if intPtr==None else OuterShadowEffect(intPtr)
        return ret


    @OuterShadowEffect.setter
    def OuterShadowEffect(self, value:'OuterShadowEffect'):
        GetDllLibPpt().EffectDag_set_OuterShadowEffect.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().EffectDag_set_OuterShadowEffect,self.Ptr, value.Ptr)

    @property

    def PresetShadowEffect(self)->'PresetShadow':
        """
    <summary>
        Preset shadow.
    </summary>
        """
        GetDllLibPpt().EffectDag_get_PresetShadowEffect.argtypes=[c_void_p]
        GetDllLibPpt().EffectDag_get_PresetShadowEffect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectDag_get_PresetShadowEffect,self.Ptr)
        ret = None if intPtr==None else PresetShadow(intPtr)
        return ret


    @PresetShadowEffect.setter
    def PresetShadowEffect(self, value:'PresetShadow'):
        GetDllLibPpt().EffectDag_set_PresetShadowEffect.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().EffectDag_set_PresetShadowEffect,self.Ptr, value.Ptr)

    @property

    def ReflectionEffect(self)->'ReflectionEffect':
        """
    <summary>
        Reflection. 
    </summary>
        """
        GetDllLibPpt().EffectDag_get_ReflectionEffect.argtypes=[c_void_p]
        GetDllLibPpt().EffectDag_get_ReflectionEffect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectDag_get_ReflectionEffect,self.Ptr)
        ret = None if intPtr==None else ReflectionEffect(intPtr)
        return ret


    @ReflectionEffect.setter
    def ReflectionEffect(self, value:'ReflectionEffect'):
        GetDllLibPpt().EffectDag_set_ReflectionEffect.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().EffectDag_set_ReflectionEffect,self.Ptr, value.Ptr)

    @property

    def SoftEdgeEffect(self)->'SoftEdgeEffect':
        """
    <summary>
        Soft edge.
    </summary>
        """
        GetDllLibPpt().EffectDag_get_SoftEdgeEffect.argtypes=[c_void_p]
        GetDllLibPpt().EffectDag_get_SoftEdgeEffect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().EffectDag_get_SoftEdgeEffect,self.Ptr)
        ret = None if intPtr==None else SoftEdgeEffect(intPtr)
        return ret


    @SoftEdgeEffect.setter
    def SoftEdgeEffect(self, value:'SoftEdgeEffect'):
        GetDllLibPpt().EffectDag_set_SoftEdgeEffect.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().EffectDag_set_SoftEdgeEffect,self.Ptr, value.Ptr)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().EffectDag_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().EffectDag_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().EffectDag_Equals,self.Ptr, intPtrobj)
        return ret

