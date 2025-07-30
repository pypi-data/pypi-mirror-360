from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ChartWallsOrFloor (  PptObject) :
    """
    <summary>
        Represents walls on 3d charts.
    </summary>
    """
    @property
    def Thickness(self)->int:
        """
    <summary>
        Gets or sets the walls thickness.
    </summary>
        """
        GetDllLibPpt().ChartWallsOrFloor_get_Thickness.argtypes=[c_void_p]
        GetDllLibPpt().ChartWallsOrFloor_get_Thickness.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartWallsOrFloor_get_Thickness,self.Ptr)
        return ret

    @Thickness.setter
    def Thickness(self, value:int):
        GetDllLibPpt().ChartWallsOrFloor_set_Thickness.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartWallsOrFloor_set_Thickness,self.Ptr, value)

    @property

    def Fill(self)->'FillFormat':
        """
    <summary>
        Gets fill style properties of a chart.
            Read-only <see cref="T:Spire.Presentation.Drawing.FillFormat" />.
    </summary>
        """
        GetDllLibPpt().ChartWallsOrFloor_get_Fill.argtypes=[c_void_p]
        GetDllLibPpt().ChartWallsOrFloor_get_Fill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartWallsOrFloor_get_Fill,self.Ptr)
        ret = None if intPtr==None else FillFormat(intPtr)
        return ret


    @property

    def Line(self)->'IChartGridLine':
        """
    <summary>
        Gets line style properties of a chart.
    </summary>
        """
        GetDllLibPpt().ChartWallsOrFloor_get_Line.argtypes=[c_void_p]
        GetDllLibPpt().ChartWallsOrFloor_get_Line.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartWallsOrFloor_get_Line,self.Ptr)
        ret = None if intPtr==None else IChartGridLine(intPtr)
        return ret


    @property

    def Effect(self)->'EffectDag':
        """
    <summary>
        Gets effects used for a chart.
            Read-only <see cref="T:Spire.Presentation.Drawing.EffectDag" />.
    </summary>
        """
        GetDllLibPpt().ChartWallsOrFloor_get_Effect.argtypes=[c_void_p]
        GetDllLibPpt().ChartWallsOrFloor_get_Effect.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartWallsOrFloor_get_Effect,self.Ptr)
        ret = None if intPtr==None else EffectDag(intPtr)
        return ret


    @property

    def Effect3D(self)->'FormatThreeD':
        """
    <summary>
        Gets 3D format of a chart.
            Read-only <see cref="T:Spire.Presentation.Drawing.FormatThreeD" />.
    </summary>
        """
        GetDllLibPpt().ChartWallsOrFloor_get_Effect3D.argtypes=[c_void_p]
        GetDllLibPpt().ChartWallsOrFloor_get_Effect3D.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ChartWallsOrFloor_get_Effect3D,self.Ptr)
        ret = None if intPtr==None else FormatThreeD(intPtr)
        return ret


    @property

    def PictureType(self)->'PictureType':
        """
    <summary>
        Gets or sets the picture type.
    </summary>
        """
        GetDllLibPpt().ChartWallsOrFloor_get_PictureType.argtypes=[c_void_p]
        GetDllLibPpt().ChartWallsOrFloor_get_PictureType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ChartWallsOrFloor_get_PictureType,self.Ptr)
        objwraped = PictureType(ret)
        return objwraped

    @PictureType.setter
    def PictureType(self, value:'PictureType'):
        GetDllLibPpt().ChartWallsOrFloor_set_PictureType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().ChartWallsOrFloor_set_PictureType,self.Ptr, value.value)

