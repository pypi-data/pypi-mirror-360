from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class TabStop (SpireObject) :
    """
    <summary>
        Represents a tabulation for a text.
    </summary>
    """
    @property
    def Position(self)->float:
        """
    <summary>
        Gets or sets position of a tab.
            Assigning this property can change tab's index in collection and invalidate Enumerator.
            Read/write <see cref="T:System.Double" />.
    </summary>
        """
        GetDllLibPpt().TabStop_get_Position.argtypes=[c_void_p]
        GetDllLibPpt().TabStop_get_Position.restype=c_double
        ret = CallCFunction(GetDllLibPpt().TabStop_get_Position,self.Ptr)
        return ret

    @Position.setter
    def Position(self, value:float):
        GetDllLibPpt().TabStop_set_Position.argtypes=[c_void_p, c_double]
        CallCFunction(GetDllLibPpt().TabStop_set_Position,self.Ptr, value)

    @property

    def Alignment(self)->'TabAlignmentType':
        """
    <summary>
        Gets or sets align style of a tab.
            Read/write <see cref="T:Spire.Presentation.Converter.Entity.TabAlignment" />.
    </summary>
        """
        GetDllLibPpt().TabStop_get_Alignment.argtypes=[c_void_p]
        GetDllLibPpt().TabStop_get_Alignment.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TabStop_get_Alignment,self.Ptr)
        objwraped = TabAlignmentType(ret)
        return objwraped

    @Alignment.setter
    def Alignment(self, value:'TabAlignmentType'):
        GetDllLibPpt().TabStop_set_Alignment.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPpt().TabStop_set_Alignment,self.Ptr, value.value)


    def CompareTo(self ,obj:'SpireObject')->int:
        """
    <summary>
        Compares the current instance with another object of the same type.
    </summary>
    <param name="obj">An object to compare with this instance.</param>
    <returns>A 32-bit integer that indicates the relative order of the comparands.
            The return value has these meanings:
            <UL><LI> &lt; 0 - This instance is less than obj.</LI><LI> = 0 - This instance is equal to obj.</LI><LI> &gt; 0 - This instance is greater than obj.</LI></UL></returns>
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().TabStop_CompareTo.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().TabStop_CompareTo.restype=c_int
        ret = CallCFunction(GetDllLibPpt().TabStop_CompareTo,self.Ptr, intPtrobj)
        return ret

