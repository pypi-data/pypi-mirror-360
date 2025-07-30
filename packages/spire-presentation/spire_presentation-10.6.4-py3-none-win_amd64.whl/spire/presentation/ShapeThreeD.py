from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ShapeThreeD (SpireObject) :
    """

    """
    @property
    def ContourWidth(self)->float:
        """
    <summary>
        Gets or sets the width of a 3D contour.
            Read/write <see cref="T:System.Double" />.
    </summary>
        """
        GetDllLibPpt().ShapeThreeD_get_ContourWidth.argtypes=[c_void_p]
        GetDllLibPpt().ShapeThreeD_get_ContourWidth.restype=c_double
        ret = CallCFunction(GetDllLibPpt().ShapeThreeD_get_ContourWidth,self.Ptr)
        return ret

    @ContourWidth.setter
    def ContourWidth(self, value:float):
        GetDllLibPpt().ShapeThreeD_set_ContourWidth.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().ShapeThreeD_set_ContourWidth,self.Ptr, value)

    @property
    def ExtrusionHeight(self)->float:
        """
    <summary>
        Gets or sets the height of an extrusion effect.
            Read/write <see cref="T:System.Double" />.
    </summary>
        """
        GetDllLibPpt().ShapeThreeD_get_ExtrusionHeight.argtypes=[c_void_p]
        GetDllLibPpt().ShapeThreeD_get_ExtrusionHeight.restype=c_double
        ret = CallCFunction(GetDllLibPpt().ShapeThreeD_get_ExtrusionHeight,self.Ptr)
        return ret

    @ExtrusionHeight.setter
    def ExtrusionHeight(self, value:float):
        GetDllLibPpt().ShapeThreeD_set_ExtrusionHeight.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().ShapeThreeD_set_ExtrusionHeight,self.Ptr, value)

    @property
    def Depth(self)->float:
        """
    <summary>
        Gets or sets the depth of a 3D shape.
            Read/write <see cref="T:System.Double" />.
    </summary>
        """
        GetDllLibPpt().ShapeThreeD_get_Depth.argtypes=[c_void_p]
        GetDllLibPpt().ShapeThreeD_get_Depth.restype=c_double
        ret = CallCFunction(GetDllLibPpt().ShapeThreeD_get_Depth,self.Ptr)
        return ret

    @Depth.setter
    def Depth(self, value:float):
        GetDllLibPpt().ShapeThreeD_set_Depth.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().ShapeThreeD_set_Depth,self.Ptr, value)

    @property

    def TopBevel(self)->'ShapeBevelStyle':
        """
    <summary>
        Gets or sets the type of a top 3D bevel.
            Read <see cref="T:Spire.Presentation.ShapeBevelStyle" />,
    </summary>
        """
        GetDllLibPpt().ShapeThreeD_get_TopBevel.argtypes=[c_void_p]
        GetDllLibPpt().ShapeThreeD_get_TopBevel.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeThreeD_get_TopBevel,self.Ptr)
        ret = None if intPtr==None else ShapeBevelStyle(intPtr)
        return ret


    @property

    def BottomBevel(self)->'ShapeBevelStyle':
        """
    <summary>
        Gets or sets the type of a bottom 3D bevel.
            Read <see cref="T:Spire.Presentation.ShapeBevelStyle" />.
    </summary>
        """
        GetDllLibPpt().ShapeThreeD_get_BottomBevel.argtypes=[c_void_p]
        GetDllLibPpt().ShapeThreeD_get_BottomBevel.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeThreeD_get_BottomBevel,self.Ptr)
        ret = None if intPtr==None else ShapeBevelStyle(intPtr)
        return ret


    @property

    def ContourColor(self)->'ColorFormat':
        """
    <summary>
        Gets or sets the color of a contour.
            Read/write <see cref="T:Spire.Presentation.Drawing.ColorFormat" />.
    </summary>
        """
        GetDllLibPpt().ShapeThreeD_get_ContourColor.argtypes=[c_void_p]
        GetDllLibPpt().ShapeThreeD_get_ContourColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeThreeD_get_ContourColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @ContourColor.setter
    def ContourColor(self, value:'ColorFormat'):
        GetDllLibPpt().ShapeThreeD_set_ContourColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ShapeThreeD_set_ContourColor,self.Ptr, value.Ptr)

    @property

    def ExtrusionColor(self)->'ColorFormat':
        """
    <summary>
        Gets or sets the color of an extrusion.
            Read/write <see cref="T:Spire.Presentation.Drawing.ColorFormat" /></summary>
        """
        GetDllLibPpt().ShapeThreeD_get_ExtrusionColor.argtypes=[c_void_p]
        GetDllLibPpt().ShapeThreeD_get_ExtrusionColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ShapeThreeD_get_ExtrusionColor,self.Ptr)
        ret = None if intPtr==None else ColorFormat(intPtr)
        return ret


    @ExtrusionColor.setter
    def ExtrusionColor(self, value:'ColorFormat'):
        GetDllLibPpt().ShapeThreeD_set_ExtrusionColor.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPpt().ShapeThreeD_set_ExtrusionColor,self.Ptr, value.Ptr)

    @property

    def BevelColorMode(self)->'BevelColorType':
        """
    <summary>
        Gets or sets the color mode used for 3D effects.
            Read/write <see cref="T:Spire.Presentation.Drawing.BevelColorType" />.
    </summary>
        """
        GetDllLibPpt().ShapeThreeD_get_BevelColorMode.argtypes=[c_void_p]
        GetDllLibPpt().ShapeThreeD_get_BevelColorMode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ShapeThreeD_get_BevelColorMode,self.Ptr)
        objwraped = BevelColorType(ret)
        return objwraped

    @BevelColorMode.setter
    def BevelColorMode(self, value:'BevelColorType'):
        GetDllLibPpt().ShapeThreeD_set_BevelColorMode.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ShapeThreeD_set_BevelColorMode,self.Ptr, value.value)

    @property

    def PresetMaterial(self)->'PresetMaterialType':
        """
    <summary>
        Gets or sets the type of a material.
            Read/write <see cref="T:Spire.Presentation.PresetMaterialType" />.
    </summary>
        """
        GetDllLibPpt().ShapeThreeD_get_PresetMaterial.argtypes=[c_void_p]
        GetDllLibPpt().ShapeThreeD_get_PresetMaterial.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ShapeThreeD_get_PresetMaterial,self.Ptr)
        objwraped = PresetMaterialType(ret)
        return objwraped

    @PresetMaterial.setter
    def PresetMaterial(self, value:'PresetMaterialType'):
        GetDllLibPpt().ShapeThreeD_set_PresetMaterial.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ShapeThreeD_set_PresetMaterial,self.Ptr, value.value)

