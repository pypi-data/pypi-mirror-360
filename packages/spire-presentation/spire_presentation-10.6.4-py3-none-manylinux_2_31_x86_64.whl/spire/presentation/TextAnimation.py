from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TextAnimation (  PptObject) :
    """
    <summary>
        Represent text animation.
    </summary>
    """
    @property

    def ShapeRef(self)->'Shape':
        """

        """
        GetDllLibPpt().TextAnimation_get_ShapeRef.argtypes=[c_void_p]
        GetDllLibPpt().TextAnimation_get_ShapeRef.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextAnimation_get_ShapeRef,self.Ptr)
        ret = None if intPtr==None else Shape(intPtr)
        return ret


    @property

    def ParagraphBuildType(self)->'ParagraphBuildType':
        """
    <summary>
        Paragraph build type of text animation.
    </summary>
        """
        GetDllLibPpt().TextAnimation_get_ParagraphBuildType.argtypes=[c_void_p]
        GetDllLibPpt().TextAnimation_get_ParagraphBuildType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TextAnimation_get_ParagraphBuildType,self.Ptr)
        objwraped = ParagraphBuildType(ret)
        return objwraped

    @ParagraphBuildType.setter
    def ParagraphBuildType(self, value:'ParagraphBuildType'):
        GetDllLibPpt().TextAnimation_set_ParagraphBuildType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TextAnimation_set_ParagraphBuildType,self.Ptr, value.value)

    @property

    def Background(self)->'AnimationEffect':
        """
    <summary>
        Shape effect.
    </summary>
        """
        GetDllLibPpt().TextAnimation_get_Background.argtypes=[c_void_p]
        GetDllLibPpt().TextAnimation_get_Background.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().TextAnimation_get_Background,self.Ptr)
        ret = None if intPtr==None else AnimationEffect(intPtr)
        return ret


    @Background.setter
    def Background(self, value:'AnimationEffect'):
        GetDllLibPpt().TextAnimation_set_Background.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().TextAnimation_set_Background,self.Ptr, value.Ptr)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TextAnimation_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TextAnimation_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().TextAnimation_Equals,self.Ptr, intPtrobj)
        return ret

