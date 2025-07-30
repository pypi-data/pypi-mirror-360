from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartRotationThreeD (SpireObject) :
    """
    <summary>
        Represents 3D rotation of a chart.
    </summary>
    """
    @property
    def XDegree(self)->int:
        """
    <summary>
        Gets or sets the rotation degree in the X direction for 3D charts.
            Read/write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().ChartRotationThreeD_get_XDegree.argtypes=[c_void_p]
        GetDllLibPpt().ChartRotationThreeD_get_XDegree.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartRotationThreeD_get_XDegree,self.Ptr)
        return ret

    @XDegree.setter
    def XDegree(self, value:int):
        GetDllLibPpt().ChartRotationThreeD_set_XDegree.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartRotationThreeD_set_XDegree,self.Ptr, value)

    @property
    def YDegree(self)->int:
        """
    <summary>
        Gets or sets the rotation degree in the Y direction for 3D charts.
            Read/write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().ChartRotationThreeD_get_YDegree.argtypes=[c_void_p]
        GetDllLibPpt().ChartRotationThreeD_get_YDegree.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartRotationThreeD_get_YDegree,self.Ptr)
        return ret

    @YDegree.setter
    def YDegree(self, value:int):
        GetDllLibPpt().ChartRotationThreeD_set_YDegree.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartRotationThreeD_set_YDegree,self.Ptr, value)

    @property
    def IsPerspective(self)->int:
        """
    <summary>
        Gets or sets the perspective value for 3D charts.
            Read/write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().ChartRotationThreeD_get_IsPerspective.argtypes=[c_void_p]
        GetDllLibPpt().ChartRotationThreeD_get_IsPerspective.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartRotationThreeD_get_IsPerspective,self.Ptr)
        return ret

    @IsPerspective.setter
    def IsPerspective(self, value:int):
        GetDllLibPpt().ChartRotationThreeD_set_IsPerspective.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartRotationThreeD_set_IsPerspective,self.Ptr, value)

    @property
    def Depth(self)->int:
        """
    <summary>
        Depth of points relative to width.
            Read/write <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().ChartRotationThreeD_get_Depth.argtypes=[c_void_p]
        GetDllLibPpt().ChartRotationThreeD_get_Depth.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartRotationThreeD_get_Depth,self.Ptr)
        return ret

    @Depth.setter
    def Depth(self, value:int):
        GetDllLibPpt().ChartRotationThreeD_set_Depth.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartRotationThreeD_set_Depth,self.Ptr, value)

