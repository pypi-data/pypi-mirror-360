from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class SlidePicture (  ShapeNode, IEmbedImage) :
    """

    """
    @property

    def ShapeLocking(self)->'SlidePictureLocking':
        """

        """
        GetDllLibPpt().SlidePicture_get_ShapeLocking.argtypes=[c_void_p]
        GetDllLibPpt().SlidePicture_get_ShapeLocking.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlidePicture_get_ShapeLocking,self.Ptr)
        ret = None if intPtr==None else SlidePictureLocking(intPtr)
        return ret


    @property

    def ShapeType(self)->'ShapeType':
        """

        """
        GetDllLibPpt().SlidePicture_get_ShapeType.argtypes=[c_void_p]
        GetDllLibPpt().SlidePicture_get_ShapeType.restype=c_int
        ret = CallCFunction(GetDllLibPpt().SlidePicture_get_ShapeType,self.Ptr)
        objwraped = ShapeType(ret)
        return objwraped

    @ShapeType.setter
    def ShapeType(self, value:'ShapeType'):
        GetDllLibPpt().SlidePicture_set_ShapeType.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().SlidePicture_set_ShapeType,self.Ptr, value.value)

    @property
    def IsCropped(self)->bool:
        """
    <summary>
        Determines if the picture is cropped.
    </summary>
    <returns>
            If the picture is cropped,the value is "true",otherwise the value is "false"
            ,the default value is "false".</returns>
        """
        GetDllLibPpt().SlidePicture_get_IsCropped.argtypes=[c_void_p]
        GetDllLibPpt().SlidePicture_get_IsCropped.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().SlidePicture_get_IsCropped,self.Ptr)
        return ret

    @property

    def PictureFill(self)->'PictureFillFormat':
        """

        """
        GetDllLibPpt().SlidePicture_get_PictureFill.argtypes=[c_void_p]
        GetDllLibPpt().SlidePicture_get_PictureFill.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().SlidePicture_get_PictureFill,self.Ptr)
        ret = None if intPtr==None else PictureFillFormat(intPtr)
        return ret


    def PictureAdjust(self):
        """
    <summary>
        Adjust the picture of slide
    </summary>
        """
        GetDllLibPpt().SlidePicture_PictureAdjust.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().SlidePicture_PictureAdjust,self.Ptr)


    def Crop(self ,x:float,y:float,width:float,height:float):
        """
    <summary>
        Crop the picture of slide
    </summary>
    <param name="x"> x coordinate </param>
    <param name="y"> y coordinate </param>
    <param name="width"> cropped width </param>
    <param name="height"> cropped height </param>
        """
        
        GetDllLibPpt().SlidePicture_Crop.argtypes=[c_void_p ,c_float,c_float,c_float,c_float]
        CallCFunction(GetDllLibPpt().SlidePicture_Crop,self.Ptr, x,y,width,height)

