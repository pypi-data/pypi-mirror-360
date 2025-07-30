from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PptObject (SpireObject) :
    """

    """
    @property

    def Parent(self)->'SpireObject':
        """
    <summary>
        Reference to Parent object. Read-only.
    </summary>
        """
        GetDllLibPpt().PptObject_get_Parent.argtypes=[c_void_p]
        GetDllLibPpt().PptObject_get_Parent.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().PptObject_get_Parent,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


    def Dispose(self):
        """
    <summary>
        Dispose object and free resources.
    </summary>
        """
        GetDllLibPpt().PptObject_Dispose.argtypes=[c_void_p]
        CallCFunction(GetDllLibPpt().PptObject_Dispose,self.Ptr)

