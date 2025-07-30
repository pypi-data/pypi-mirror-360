from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GraphicAnimation (  PptObject) :
    """
    <summary>
        Represent text animation.
    </summary>
    """
    @property

    def ShapeRef(self)->'Shape':
        """

        """
        GetDllLibPpt().GraphicAnimation_get_ShapeRef.argtypes=[c_void_p]
        GetDllLibPpt().GraphicAnimation_get_ShapeRef.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GraphicAnimation_get_ShapeRef,self.Ptr)
        ret = None if intPtr==None else Shape(intPtr)
        return ret


    @property

    def BuildType(self)->'GraphicBuildType':
        """

        """
        GetDllLibPpt().GraphicAnimation_get_BuildType.argtypes=[c_void_p]
        GetDllLibPpt().GraphicAnimation_get_BuildType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().GraphicAnimation_get_BuildType,self.Ptr)
        objwraped = GraphicBuildType(ret)
        return objwraped

    @BuildType.setter
    def BuildType(self, value:'GraphicBuildType'):
        GetDllLibPpt().GraphicAnimation_set_BuildType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().GraphicAnimation_set_BuildType,self.Ptr, value.value)


    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().GraphicAnimation_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().GraphicAnimation_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GraphicAnimation_Equals,self.Ptr, intPtrobj)
        return ret

