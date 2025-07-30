from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SaveToPdfOption (SpireObject) :
    """
    <summary>
        save to pdf option
    </summary>
    """
    @property
    def ContainHiddenSlides(self)->bool:
        """
    <summary>
        if contain hidden slides when convert to pdf.
    </summary>
        """
        GetDllLibPpt().SaveToPdfOption_get_ContainHiddenSlides.argtypes=[c_void_p]
        GetDllLibPpt().SaveToPdfOption_get_ContainHiddenSlides.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SaveToPdfOption_get_ContainHiddenSlides,self.Ptr)
        return ret

    @ContainHiddenSlides.setter
    def ContainHiddenSlides(self, value:bool):
        GetDllLibPpt().SaveToPdfOption_SetContainHiddenSlides.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPpt().SaveToPdfOption_SetContainHiddenSlides,self.Ptr, value)

    @property

    def PageSlideCount(self)->'PageSlideCount':
        """

        """
        GetDllLibPpt().SaveToPdfOption_get_PageSlideCount.argtypes=[c_void_p]
        GetDllLibPpt().SaveToPdfOption_get_PageSlideCount.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SaveToPdfOption_get_PageSlideCount,self.Ptr)
        objwraped = PageSlideCount(ret)
        return objwraped

    @PageSlideCount.setter
    def PageSlideCount(self, value:'PageSlideCount'):
        GetDllLibPpt().SaveToPdfOption_set_PageSlideCount.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().SaveToPdfOption_set_PageSlideCount,self.Ptr, value.value)

    @property

    def Order(self)->'Order':
        """

        """
        GetDllLibPpt().SaveToPdfOption_get_Order.argtypes=[c_void_p]
        GetDllLibPpt().SaveToPdfOption_get_Order.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SaveToPdfOption_get_Order,self.Ptr)
        objwraped = Order(ret)
        return objwraped

    @Order.setter
    def Order(self, value:'Order'):
        GetDllLibPpt().SaveToPdfOption_set_Order.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().SaveToPdfOption_set_Order,self.Ptr, value.value)

    @property

    def PdfConformanceLevel(self)->'PdfConformanceLevel':
        """
    <summary>
        Gets or sets the Pdf document's Conformance-level.
    </summary>
        """
        GetDllLibPpt().SaveToPdfOption_get_PdfConformanceLevel.argtypes=[c_void_p]
        GetDllLibPpt().SaveToPdfOption_get_PdfConformanceLevel.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SaveToPdfOption_get_PdfConformanceLevel,self.Ptr)
        objwraped = PdfConformanceLevel(ret)
        return objwraped


    @PdfConformanceLevel.setter
    def PdfConformanceLevel(self, value:'PdfConformanceLevel'):
        GetDllLibPpt().SaveToPdfOption_set_PdfConformanceLevel.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().SaveToPdfOption_set_PdfConformanceLevel,self.Ptr, value.value)


#    @property
#
#    def PdfSecurity(self)->'PdfSecurity':
#        """
#    <summary>
#        Represents the security settings of the PDF document.
#    </summary>
#        """
#        GetDllLibPpt().SaveToPdfOption_get_PdfSecurity.argtypes=[c_void_p]
#        GetDllLibPpt().SaveToPdfOption_get_PdfSecurity.restype=c_void_p
#        intPtr = CallCFunction(GetDllLibPpt().SaveToPdfOption_get_PdfSecurity,self.Ptr)
#        ret = None if intPtr==None else PdfSecurity(intPtr)
#        return ret
#


