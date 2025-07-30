from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class IImageData (SpireObject) :
    """

    """
    def GetHashCode(self)->int:
        """
    <summary>
        Gets the hash code of an image.
    </summary>
    <returns>Hash code.</returns>
        """
        GetDllLibPpt().IImageData_GetHashCode.argtypes=[c_void_p]
        GetDllLibPpt().IImageData_GetHashCode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IImageData_GetHashCode,self.Ptr)
        return ret

    @property

    def ContentType(self)->str:
        """
    <summary>
        Gets a MIME type of an image, encoded in <see cref="P:Spire.Presentation.Drawing.IImageData.Data" />.
            Read-only <see cref="T:System.String" />.
    </summary>
        """
        GetDllLibPpt().IImageData_get_ContentType.argtypes=[c_void_p]
        GetDllLibPpt().IImageData_get_ContentType.restype=c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPpt().IImageData_get_ContentType,self.Ptr))
        return ret


#    @property
#
#    def Data(self)->List['Byte']:
#        """
#    <summary>
#        Gets the copy of an image's data.
#            Read-only <see cref="T:System.Byte" />[].
#    </summary>
#        """
#        GetDllLibPpt().IImageData_get_Data.argtypes=[c_void_p]
#        GetDllLibPpt().IImageData_get_Data.restype=IntPtrArray
#        intPtrArray = CallCFunction(GetDllLibPpt().IImageData_get_Data,self.Ptr)
#        ret = GetVectorFromArray(intPtrArray, Byte)
#        return ret


    @property

    def Image(self)->'Stream':
        """
    <summary>
        Gets the copy of an image.
            Read-only <see cref="P:Spire.Presentation.Drawing.IImageData.Image" />.
    </summary>
        """
        GetDllLibPpt().IImageData_get_Image.argtypes=[c_void_p]
        GetDllLibPpt().IImageData_get_Image.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().IImageData_get_Image,self.Ptr)
        ret = None if intPtr==None else Stream(intPtr)
        return ret


    @property
    def Width(self)->int:
        """
    <summary>
        Gets a width of an image.
            Read-only <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().IImageData_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().IImageData_get_Width.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IImageData_get_Width,self.Ptr)
        return ret

    @property
    def Height(self)->int:
        """
    <summary>
        Gets a height of an image.
            Read-only <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().IImageData_get_Height.argtypes=[c_void_p]
        GetDllLibPpt().IImageData_get_Height.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IImageData_get_Height,self.Ptr)
        return ret

    @property
    def X(self)->int:
        """
    <summary>
        Gets a X-offset of an image.
            Read-only <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().IImageData_get_X.argtypes=[c_void_p]
        GetDllLibPpt().IImageData_get_X.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IImageData_get_X,self.Ptr)
        return ret

    @property
    def Y(self)->int:
        """
    <summary>
        Gets a Y-offset of an image.
            Read-only <see cref="T:System.Int32" />.
    </summary>
        """
        GetDllLibPpt().IImageData_get_Y.argtypes=[c_void_p]
        GetDllLibPpt().IImageData_get_Y.restype=c_int
        ret = CallCFunction(GetDllLibPpt().IImageData_get_Y,self.Ptr)
        return ret

