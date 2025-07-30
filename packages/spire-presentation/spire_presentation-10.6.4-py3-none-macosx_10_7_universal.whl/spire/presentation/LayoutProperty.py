from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class LayoutProperty (SpireObject) :
    """

    """
    @property
    def ShowConnectorLines(self)->bool:
        """
    <summary>
        Gets or sets a boolean value indicating whether to display 
            Connector Lines between data points
    </summary>
<remarks>Applies only to Waterfall Charts</remarks>
        """
        GetDllLibPpt().LayoutProperty_get_ShowConnectorLines.argtypes=[c_void_p]
        GetDllLibPpt().LayoutProperty_get_ShowConnectorLines.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().LayoutProperty_get_ShowConnectorLines,self.Ptr)
        return ret

    @ShowConnectorLines.setter
    def ShowConnectorLines(self, value:bool):
        GetDllLibPpt().LayoutProperty_set_ShowConnectorLines.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().LayoutProperty_set_ShowConnectorLines,self.Ptr, value)

    @property
    def ShowMeanLine(self)->bool:
        """
    <summary>
        Gets or sets a boolean value indicating whether to display
            Mean Line in Box and Whisker chart
    </summary>
        """
        GetDllLibPpt().LayoutProperty_get_ShowMeanLine.argtypes=[c_void_p]
        GetDllLibPpt().LayoutProperty_get_ShowMeanLine.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().LayoutProperty_get_ShowMeanLine,self.Ptr)
        return ret

    @ShowMeanLine.setter
    def ShowMeanLine(self, value:bool):
        GetDllLibPpt().LayoutProperty_set_ShowMeanLine.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().LayoutProperty_set_ShowMeanLine,self.Ptr, value)

    @property
    def ShowMeanMarkers(self)->bool:
        """
    <summary>
        Gets or sets a boolean value indicating whether to display
            Mean Marker in Box and Whisker chart
    </summary>
        """
        GetDllLibPpt().LayoutProperty_get_ShowMeanMarkers.argtypes=[c_void_p]
        GetDllLibPpt().LayoutProperty_get_ShowMeanMarkers.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().LayoutProperty_get_ShowMeanMarkers,self.Ptr)
        return ret

    @ShowMeanMarkers.setter
    def ShowMeanMarkers(self, value:bool):
        GetDllLibPpt().LayoutProperty_set_ShowMeanMarkers.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().LayoutProperty_set_ShowMeanMarkers,self.Ptr, value)

    @property
    def ShowOutlierPoints(self)->bool:
        """
    <summary>
        Gets or sets a boolean value indicating whether to display
            Outlier Points in Box and Whisker chart
    </summary>
        """
        GetDllLibPpt().LayoutProperty_get_ShowOutlierPoints.argtypes=[c_void_p]
        GetDllLibPpt().LayoutProperty_get_ShowOutlierPoints.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().LayoutProperty_get_ShowOutlierPoints,self.Ptr)
        return ret

    @ShowOutlierPoints.setter
    def ShowOutlierPoints(self, value:bool):
        GetDllLibPpt().LayoutProperty_set_ShowOutlierPoints.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().LayoutProperty_set_ShowOutlierPoints,self.Ptr, value)

    @property
    def ShowInnerPoints(self)->bool:
        """
    <summary>
        Gets or sets a boolean value indicating whether to display
            Inner Points in Box and Whisker chart
    </summary>
        """
        GetDllLibPpt().LayoutProperty_get_ShowInnerPoints.argtypes=[c_void_p]
        GetDllLibPpt().LayoutProperty_get_ShowInnerPoints.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().LayoutProperty_get_ShowInnerPoints,self.Ptr)
        return ret

    @ShowInnerPoints.setter
    def ShowInnerPoints(self, value:bool):
        GetDllLibPpt().LayoutProperty_set_ShowInnerPoints.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().LayoutProperty_set_ShowInnerPoints,self.Ptr, value)

    @property

    def QuartileCalculationType(self)->'QuartileCalculation':
        """
    <summary>
         Gets / Sets whether the Quartile calculation is Exclusive or Inclusive
    </summary>
<remarks>Applies only to Box and Whisker Charts</remarks>
        """
        GetDllLibPpt().LayoutProperty_get_QuartileCalculationType.argtypes=[c_void_p]
        GetDllLibPpt().LayoutProperty_get_QuartileCalculationType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().LayoutProperty_get_QuartileCalculationType,self.Ptr)
        objwraped = QuartileCalculation(ret)
        return objwraped

    @QuartileCalculationType.setter
    def QuartileCalculationType(self, value:'QuartileCalculation'):
        GetDllLibPpt().LayoutProperty_set_QuartileCalculationType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().LayoutProperty_set_QuartileCalculationType,self.Ptr, value.value)

