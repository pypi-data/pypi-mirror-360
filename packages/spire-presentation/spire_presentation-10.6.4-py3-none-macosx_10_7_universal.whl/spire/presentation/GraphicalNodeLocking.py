from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class GraphicalNodeLocking (  BaseShapeLocking) :
    """
    <summary>
        Indicates which operations are disabled on the parent GraphicalObject.
    </summary>
    """
    @property
    def GroupingProtection(self)->bool:
        """
    <summary>
        Indicates whether an adding this shape to a group Disallow.
    </summary>
        """
        GetDllLibPpt().GraphicalNodeLocking_get_GroupingProtection.argtypes=[c_void_p]
        GetDllLibPpt().GraphicalNodeLocking_get_GroupingProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GraphicalNodeLocking_get_GroupingProtection,self.Ptr)
        return ret

    @GroupingProtection.setter
    def GroupingProtection(self, value:bool):
        GetDllLibPpt().GraphicalNodeLocking_set_GroupingProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().GraphicalNodeLocking_set_GroupingProtection,self.Ptr, value)

    @property
    def DrilldownProtection(self)->bool:
        """
    <summary>
        Indicates whether selecting subshapes of this object Disallow.
    </summary>
        """
        GetDllLibPpt().GraphicalNodeLocking_get_DrilldownProtection.argtypes=[c_void_p]
        GetDllLibPpt().GraphicalNodeLocking_get_DrilldownProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GraphicalNodeLocking_get_DrilldownProtection,self.Ptr)
        return ret

    @DrilldownProtection.setter
    def DrilldownProtection(self, value:bool):
        GetDllLibPpt().GraphicalNodeLocking_set_DrilldownProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().GraphicalNodeLocking_set_DrilldownProtection,self.Ptr, value)

    @property
    def SelectionProtection(self)->bool:
        """
    <summary>
        Indicates whether a selecting this shape Disallow.
    </summary>
        """
        GetDllLibPpt().GraphicalNodeLocking_get_SelectionProtection.argtypes=[c_void_p]
        GetDllLibPpt().GraphicalNodeLocking_get_SelectionProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GraphicalNodeLocking_get_SelectionProtection,self.Ptr)
        return ret

    @SelectionProtection.setter
    def SelectionProtection(self, value:bool):
        GetDllLibPpt().GraphicalNodeLocking_set_SelectionProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().GraphicalNodeLocking_set_SelectionProtection,self.Ptr, value)

    @property
    def AspectRatioProtection(self)->bool:
        """
    <summary>
        Indicates whether a shape have to preserve aspect ratio on resizing.
    </summary>
        """
        GetDllLibPpt().GraphicalNodeLocking_get_AspectRatioProtection.argtypes=[c_void_p]
        GetDllLibPpt().GraphicalNodeLocking_get_AspectRatioProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GraphicalNodeLocking_get_AspectRatioProtection,self.Ptr)
        return ret

    @AspectRatioProtection.setter
    def AspectRatioProtection(self, value:bool):
        GetDllLibPpt().GraphicalNodeLocking_set_AspectRatioProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().GraphicalNodeLocking_set_AspectRatioProtection,self.Ptr, value)

    @property
    def PositionProtection(self)->bool:
        """
    <summary>
        Indicates whether a moving this shape Disallow.
    </summary>
        """
        GetDllLibPpt().GraphicalNodeLocking_get_PositionProtection.argtypes=[c_void_p]
        GetDllLibPpt().GraphicalNodeLocking_get_PositionProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GraphicalNodeLocking_get_PositionProtection,self.Ptr)
        return ret

    @PositionProtection.setter
    def PositionProtection(self, value:bool):
        GetDllLibPpt().GraphicalNodeLocking_set_PositionProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().GraphicalNodeLocking_set_PositionProtection,self.Ptr, value)

    @property
    def ResizeProtection(self)->bool:
        """
    <summary>
        Indicates whether a resizing this shape Disallow.
    </summary>
        """
        GetDllLibPpt().GraphicalNodeLocking_get_ResizeProtection.argtypes=[c_void_p]
        GetDllLibPpt().GraphicalNodeLocking_get_ResizeProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().GraphicalNodeLocking_get_ResizeProtection,self.Ptr)
        return ret

    @ResizeProtection.setter
    def ResizeProtection(self, value:bool):
        GetDllLibPpt().GraphicalNodeLocking_set_ResizeProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().GraphicalNodeLocking_set_ResizeProtection,self.Ptr, value)

