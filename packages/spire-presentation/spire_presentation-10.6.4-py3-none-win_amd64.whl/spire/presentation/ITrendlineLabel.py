from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ITrendlineLabel (SpireObject) :
    """

    """
    @property

    def TextFrameProperties(self)->'ITextFrameProperties':
        """
    <summary>
        Gets the Trendlines DataLabel TextFrameProperties. 
            Read <see cref="P:Spire.Presentation.Charts.ITrendlineLabel.TextFrameProperties" />.
    </summary>
        """
        GetDllLibPpt().ITrendlineLabel_get_TextFrameProperties.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlineLabel_get_TextFrameProperties.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ITrendlineLabel_get_TextFrameProperties,self.Ptr)
        ret = None if intPtr==None else ITextFrameProperties(intPtr)
        return ret


    @property
    def OffsetX(self)->float:
        """
    <summary>
        Gets or Sets the Trendlines DataLabel Offset on X Coodinate Axis .
            the position is relative to default position for the chart width. 
            Read/Write <see cref="P:Spire.Presentation.Charts.ITrendlineLabel.OffsetX" />.
    </summary>
        """
        GetDllLibPpt().ITrendlineLabel_get_OffsetX.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlineLabel_get_OffsetX.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ITrendlineLabel_get_OffsetX,self.Ptr)
        return ret

    @OffsetX.setter
    def OffsetX(self, value:float):
        GetDllLibPpt().ITrendlineLabel_set_OffsetX.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ITrendlineLabel_set_OffsetX,self.Ptr, value)

    @property
    def OffsetY(self)->float:
        """
    <summary>
        Gets or Sets the Trendlines DataLabel Offset on Y Coodinate Axis.
            the position is relative to default position for the chart height.
            Read/Write <see cref="P:Spire.Presentation.Charts.ITrendlineLabel.OffsetY" />.
    </summary>
        """
        GetDllLibPpt().ITrendlineLabel_get_OffsetY.argtypes=[c_void_p]
        GetDllLibPpt().ITrendlineLabel_get_OffsetY.restype=c_float
        ret = CallCFunction(GetDllLibPpt().ITrendlineLabel_get_OffsetY,self.Ptr)
        return ret

    @OffsetY.setter
    def OffsetY(self, value:float):
        GetDllLibPpt().ITrendlineLabel_set_OffsetY.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().ITrendlineLabel_set_OffsetY,self.Ptr, value)

