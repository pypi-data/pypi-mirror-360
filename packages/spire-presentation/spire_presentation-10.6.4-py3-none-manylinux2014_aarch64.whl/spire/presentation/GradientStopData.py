from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GradientStopData (SpireObject) :
    """
    <summary>
        Represents a gradient stop.
    </summary>
    """
    @property
    def Position(self)->float:
        """
    <summary>
        Gets the position (0..1) of a gradient stop.
            Readonly <see cref="T:System.Single" />.
    </summary>
        """
        GetDllLibPpt().GradientStopData_get_Position.argtypes=[c_void_p]
        GetDllLibPpt().GradientStopData_get_Position.restype=c_float
        ret = CallCFunction(GetDllLibPpt().GradientStopData_get_Position,self.Ptr)
        return ret

    @property

    def Color(self)->'Color':
        """
    <summary>
        Gets the color of a gradient stop.
            Read-only <see cref="T:Spire.Presentation.Drawing.ColorFormat" />.
    </summary>
        """
        GetDllLibPpt().GradientStopData_get_Color.argtypes=[c_void_p]
        GetDllLibPpt().GradientStopData_get_Color.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().GradientStopData_get_Color,self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret


