from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SimpleShapeBaseLocking (  BaseShapeLocking) :
    """

    """
    @property
    def GroupingProtection(self)->bool:
        """
    <summary>
        Indicates whether an adding this shape to a group Disallow.
    </summary>
        """
        GetDllLibPpt().SimpleShapeBaseLocking_get_GroupingProtection.argtypes=[c_void_p]
        GetDllLibPpt().SimpleShapeBaseLocking_get_GroupingProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_get_GroupingProtection,self.Ptr)
        return ret

    @GroupingProtection.setter
    def GroupingProtection(self, value:bool):
        GetDllLibPpt().SimpleShapeBaseLocking_set_GroupingProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_set_GroupingProtection,self.Ptr, value)

    @property
    def SelectionProtection(self)->bool:
        """
    <summary>
        Indicates whether a selecting this shape Disallow.
    </summary>
        """
        GetDllLibPpt().SimpleShapeBaseLocking_get_SelectionProtection.argtypes=[c_void_p]
        GetDllLibPpt().SimpleShapeBaseLocking_get_SelectionProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_get_SelectionProtection,self.Ptr)
        return ret

    @SelectionProtection.setter
    def SelectionProtection(self, value:bool):
        GetDllLibPpt().SimpleShapeBaseLocking_set_SelectionProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_set_SelectionProtection,self.Ptr, value)

    @property
    def RotationProtection(self)->bool:
        """
    <summary>
        Indicates whether a changing rotation angle of this shape Disallow.
    </summary>
        """
        GetDllLibPpt().SimpleShapeBaseLocking_get_RotationProtection.argtypes=[c_void_p]
        GetDllLibPpt().SimpleShapeBaseLocking_get_RotationProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_get_RotationProtection,self.Ptr)
        return ret

    @RotationProtection.setter
    def RotationProtection(self, value:bool):
        GetDllLibPpt().SimpleShapeBaseLocking_set_RotationProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_set_RotationProtection,self.Ptr, value)

    @property
    def AspectRatioProtection(self)->bool:
        """
    <summary>
        Indicates whether a shape have to preserve aspect ratio on resizing.
    </summary>
        """
        GetDllLibPpt().SimpleShapeBaseLocking_get_AspectRatioProtection.argtypes=[c_void_p]
        GetDllLibPpt().SimpleShapeBaseLocking_get_AspectRatioProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_get_AspectRatioProtection,self.Ptr)
        return ret

    @AspectRatioProtection.setter
    def AspectRatioProtection(self, value:bool):
        GetDllLibPpt().SimpleShapeBaseLocking_set_AspectRatioProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_set_AspectRatioProtection,self.Ptr, value)

    @property
    def PositionProtection(self)->bool:
        """
    <summary>
        Indicates whether a moving this shape Disallow.
    </summary>
        """
        GetDllLibPpt().SimpleShapeBaseLocking_get_PositionProtection.argtypes=[c_void_p]
        GetDllLibPpt().SimpleShapeBaseLocking_get_PositionProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_get_PositionProtection,self.Ptr)
        return ret

    @PositionProtection.setter
    def PositionProtection(self, value:bool):
        GetDllLibPpt().SimpleShapeBaseLocking_set_PositionProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_set_PositionProtection,self.Ptr, value)

    @property
    def ResizeProtection(self)->bool:
        """
    <summary>
        Indicates whether a resizing this shape Disallow.
    </summary>
        """
        GetDllLibPpt().SimpleShapeBaseLocking_get_ResizeProtection.argtypes=[c_void_p]
        GetDllLibPpt().SimpleShapeBaseLocking_get_ResizeProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_get_ResizeProtection,self.Ptr)
        return ret

    @ResizeProtection.setter
    def ResizeProtection(self, value:bool):
        GetDllLibPpt().SimpleShapeBaseLocking_set_ResizeProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_set_ResizeProtection,self.Ptr, value)

    @property
    def EditPointProtection(self)->bool:
        """
    <summary>
        Indicates whether a direct changing of contour of this shape Disallow.
    </summary>
        """
        GetDllLibPpt().SimpleShapeBaseLocking_get_EditPointProtection.argtypes=[c_void_p]
        GetDllLibPpt().SimpleShapeBaseLocking_get_EditPointProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_get_EditPointProtection,self.Ptr)
        return ret

    @EditPointProtection.setter
    def EditPointProtection(self, value:bool):
        GetDllLibPpt().SimpleShapeBaseLocking_set_EditPointProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_set_EditPointProtection,self.Ptr, value)

    @property
    def AdjustHandlesProtection(self)->bool:
        """
    <summary>
        Indicates whether a changing adjust values Disallow.
    </summary>
        """
        GetDllLibPpt().SimpleShapeBaseLocking_get_AdjustHandlesProtection.argtypes=[c_void_p]
        GetDllLibPpt().SimpleShapeBaseLocking_get_AdjustHandlesProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_get_AdjustHandlesProtection,self.Ptr)
        return ret

    @AdjustHandlesProtection.setter
    def AdjustHandlesProtection(self, value:bool):
        GetDllLibPpt().SimpleShapeBaseLocking_set_AdjustHandlesProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_set_AdjustHandlesProtection,self.Ptr, value)

    @property
    def ArrowheadChangesProtection(self)->bool:
        """
    <summary>
        Indicates whether a changing arrowheads Disallow.
    </summary>
        """
        GetDllLibPpt().SimpleShapeBaseLocking_get_ArrowheadChangesProtection.argtypes=[c_void_p]
        GetDllLibPpt().SimpleShapeBaseLocking_get_ArrowheadChangesProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_get_ArrowheadChangesProtection,self.Ptr)
        return ret

    @ArrowheadChangesProtection.setter
    def ArrowheadChangesProtection(self, value:bool):
        GetDllLibPpt().SimpleShapeBaseLocking_set_ArrowheadChangesProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_set_ArrowheadChangesProtection,self.Ptr, value)

    @property
    def ShapeTypeProtection(self)->bool:
        """
    <summary>
        Indicates whether a changing of a shape type Disallow.
    </summary>
        """
        GetDllLibPpt().SimpleShapeBaseLocking_get_ShapeTypeProtection.argtypes=[c_void_p]
        GetDllLibPpt().SimpleShapeBaseLocking_get_ShapeTypeProtection.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_get_ShapeTypeProtection,self.Ptr)
        return ret

    @ShapeTypeProtection.setter
    def ShapeTypeProtection(self, value:bool):
        GetDllLibPpt().SimpleShapeBaseLocking_set_ShapeTypeProtection.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SimpleShapeBaseLocking_set_ShapeTypeProtection,self.Ptr, value)

