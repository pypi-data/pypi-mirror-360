from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class Placeholder (  PptObject) :
    """
    <summary>
        Represents a placeholder on a slide.
    </summary>
    """
    @property

    def Orientation(self)->'Direction':
        """
    <summary>
        Gets the orientation of a placeholder.
            Read-only <see cref="P:Spire.Presentation.Placeholder.Orientation" />.
    </summary>
        """
        GetDllLibPpt().Placeholder_get_Orientation.argtypes=[c_void_p]
        GetDllLibPpt().Placeholder_get_Orientation.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Placeholder_get_Orientation,self.Ptr)
        objwraped = Direction(ret)
        return objwraped

    @property

    def Size(self)->'PlaceholderSize':
        """
    <summary>
        Gets the size of a placeholder.
            Read-only <see cref="T:Spire.Presentation.PlaceholderSize" />.
    </summary>
        """
        GetDllLibPpt().Placeholder_get_Size.argtypes=[c_void_p]
        GetDllLibPpt().Placeholder_get_Size.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Placeholder_get_Size,self.Ptr)
        objwraped = PlaceholderSize(ret)
        return objwraped

    @property

    def Type(self)->'PlaceholderType':
        """
    <summary>
        Gets the type of a placeholder.
            Read-only <see cref="T:Spire.Presentation.Converter.Entity.PlaceholderType" />.
    </summary>
        """
        GetDllLibPpt().Placeholder_get_Type.argtypes=[c_void_p]
        GetDllLibPpt().Placeholder_get_Type.restype=c_int
        ret = CallCFunction(GetDllLibPpt().Placeholder_get_Type,self.Ptr)
        objwraped = PlaceholderType(ret)
        return objwraped

    @property

    def Index(self)->'UInt32':
        """
    <summary>
        Gets the index of a placeholder.
            Read-only <see cref="T:System.UInt32" />.
    </summary>
        """
        GetDllLibPpt().Placeholder_get_Index.argtypes=[c_void_p]
        GetDllLibPpt().Placeholder_get_Index.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().Placeholder_get_Index,self.Ptr)
        ret = None if intPtr==None else UInt32(intPtr)
        return ret



    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().Placeholder_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().Placeholder_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().Placeholder_Equals,self.Ptr, intPtrobj)
        return ret

