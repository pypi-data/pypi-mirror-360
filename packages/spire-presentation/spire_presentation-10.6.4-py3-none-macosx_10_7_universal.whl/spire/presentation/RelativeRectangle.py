from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class RelativeRectangle (SpireObject) :
    """

    """
    @property
    def X(self)->float:
        """

        """
        GetDllLibPpt().RelativeRectangle_get_X.argtypes=[c_void_p]
        GetDllLibPpt().RelativeRectangle_get_X.restype=c_float
        ret = CallCFunction(GetDllLibPpt().RelativeRectangle_get_X,self.Ptr)
        return ret

    @X.setter
    def X(self, value:float):
        GetDllLibPpt().RelativeRectangle_set_X.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().RelativeRectangle_set_X,self.Ptr, value)

    @property
    def Y(self)->float:
        """

        """
        GetDllLibPpt().RelativeRectangle_get_Y.argtypes=[c_void_p]
        GetDllLibPpt().RelativeRectangle_get_Y.restype=c_float
        ret = CallCFunction(GetDllLibPpt().RelativeRectangle_get_Y,self.Ptr)
        return ret

    @Y.setter
    def Y(self, value:float):
        GetDllLibPpt().RelativeRectangle_set_Y.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().RelativeRectangle_set_Y,self.Ptr, value)

    @property
    def Width(self)->float:
        """

        """
        GetDllLibPpt().RelativeRectangle_get_Width.argtypes=[c_void_p]
        GetDllLibPpt().RelativeRectangle_get_Width.restype=c_float
        ret = CallCFunction(GetDllLibPpt().RelativeRectangle_get_Width,self.Ptr)
        return ret

    @Width.setter
    def Width(self, value:float):
        GetDllLibPpt().RelativeRectangle_set_Width.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().RelativeRectangle_set_Width,self.Ptr, value)

    @property
    def Height(self)->float:
        """

        """
        GetDllLibPpt().RelativeRectangle_get_Height.argtypes=[c_void_p]
        GetDllLibPpt().RelativeRectangle_get_Height.restype=c_float
        ret = CallCFunction(GetDllLibPpt().RelativeRectangle_get_Height,self.Ptr)
        return ret

    @Height.setter
    def Height(self, value:float):
        GetDllLibPpt().RelativeRectangle_set_Height.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().RelativeRectangle_set_Height,self.Ptr, value)

    @property
    def Left(self)->float:
        """

        """
        GetDllLibPpt().RelativeRectangle_get_Left.argtypes=[c_void_p]
        GetDllLibPpt().RelativeRectangle_get_Left.restype=c_float
        ret = CallCFunction(GetDllLibPpt().RelativeRectangle_get_Left,self.Ptr)
        return ret

    @Left.setter
    def Left(self, value:float):
        GetDllLibPpt().RelativeRectangle_set_Left.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().RelativeRectangle_set_Left,self.Ptr, value)

    @property
    def Top(self)->float:
        """

        """
        GetDllLibPpt().RelativeRectangle_get_Top.argtypes=[c_void_p]
        GetDllLibPpt().RelativeRectangle_get_Top.restype=c_float
        ret = CallCFunction(GetDllLibPpt().RelativeRectangle_get_Top,self.Ptr)
        return ret

    @Top.setter
    def Top(self, value:float):
        GetDllLibPpt().RelativeRectangle_set_Top.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().RelativeRectangle_set_Top,self.Ptr, value)

    @property
    def Right(self)->float:
        """

        """
        GetDllLibPpt().RelativeRectangle_get_Right.argtypes=[c_void_p]
        GetDllLibPpt().RelativeRectangle_get_Right.restype=c_float
        ret = CallCFunction(GetDllLibPpt().RelativeRectangle_get_Right,self.Ptr)
        return ret

    @Right.setter
    def Right(self, value:float):
        GetDllLibPpt().RelativeRectangle_set_Right.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().RelativeRectangle_set_Right,self.Ptr, value)

    @property
    def Bottom(self)->float:
        """

        """
        GetDllLibPpt().RelativeRectangle_get_Bottom.argtypes=[c_void_p]
        GetDllLibPpt().RelativeRectangle_get_Bottom.restype=c_float
        ret = CallCFunction(GetDllLibPpt().RelativeRectangle_get_Bottom,self.Ptr)
        return ret

    @Bottom.setter
    def Bottom(self, value:float):
        GetDllLibPpt().RelativeRectangle_set_Bottom.argtypes=[c_void_p, c_float]
        CallCFunction(GetDllLibPpt().RelativeRectangle_set_Bottom,self.Ptr, value)

    @dispatch

    def Transform(self ,rect:RectangleF)->RectangleF:
        """

        """
        intPtrrect:c_void_p = rect.Ptr

        GetDllLibPpt().RelativeRectangle_Transform.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().RelativeRectangle_Transform.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().RelativeRectangle_Transform,self.Ptr, intPtrrect)
        ret = None if intPtr==None else RectangleF(intPtr)
        return ret


    @dispatch

    def Transform(self ,rect:'RelativeRectangle')->'RelativeRectangle':
        """

        """
        intPtrrect:c_void_p = rect.Ptr

        GetDllLibPpt().RelativeRectangle_TransformR.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().RelativeRectangle_TransformR.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().RelativeRectangle_TransformR,self.Ptr, intPtrrect)
        ret = None if intPtr==None else RelativeRectangle(intPtr)
        return ret


