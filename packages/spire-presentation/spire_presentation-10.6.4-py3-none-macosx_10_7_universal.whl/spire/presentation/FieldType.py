from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class FieldType (SpireObject) :
    """
    <summary>
        Represents a type of field. 
    </summary>
    """

    def Equals(self ,obj:'SpireObject')->bool:
        """
    <summary>
        Checks if this field is equal to another.
    </summary>
    <param name="obj">Field to compare.</param>
    <returns>True if fields are equal.</returns>
        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().FieldType_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().FieldType_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().FieldType_Equals,self.Ptr, intPtrobj)
        return ret

    def GetHashCode(self)->int:
        """
    <summary>
        Gets hashcode for this object.
    </summary>
    <returns>Hashcode <see cref="T:System.Int32" />.</returns>
        """
        GetDllLibPpt().FieldType_GetHashCode.argtypes=[c_void_p]
        GetDllLibPpt().FieldType_GetHashCode.restype=c_int
        ret = CallCFunction(GetDllLibPpt().FieldType_GetHashCode,self.Ptr)
        return ret

    @staticmethod

    def op_Equality(a:'FieldType',b:'FieldType')->bool:
        """
    <summary>
        Checks Objects is equal.
    </summary>
        """
        intPtra:c_void_p = a.Ptr
        intPtrb:c_void_p = b.Ptr

        GetDllLibPpt().FieldType_op_Equality.argtypes=[ c_void_p,c_void_p]
        GetDllLibPpt().FieldType_op_Equality.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().FieldType_op_Equality, intPtra,intPtrb)
        return ret

    @staticmethod

    def op_Inequality(a:'FieldType',b:'FieldType')->bool:
        """
    <summary>
        Checks Objects is inequal.
    </summary>
        """
        intPtra:c_void_p = a.Ptr
        intPtrb:c_void_p = b.Ptr

        GetDllLibPpt().FieldType_op_Inequality.argtypes=[ c_void_p,c_void_p]
        GetDllLibPpt().FieldType_op_Inequality.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().FieldType_op_Inequality, intPtra,intPtrb)
        return ret

    @staticmethod

    def get_DateTime()->'FieldType':
        """
    <summary>
        Gets current date and time in default date time format.
    </summary>
        """
        #GetDllLibPpt().FieldType_get_DateTime.argtypes=[]
        GetDllLibPpt().FieldType_get_DateTime.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FieldType_get_DateTime)
        ret = None if intPtr==None else FieldType(intPtr)
        return ret


    @staticmethod

    def get_DateTime1()->'FieldType':
        """
    <summary>
        Gets current date and time in a first predefined format (MM/DD/YYYY).
    </summary>
        """
        #GetDllLibPpt().FieldType_get_DateTime1.argtypes=[]
        GetDllLibPpt().FieldType_get_DateTime1.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FieldType_get_DateTime1)
        ret = None if intPtr==None else FieldType(intPtr)
        return ret


    @staticmethod

    def get_DateTime2()->'FieldType':
        """
    <summary>
        Gets current date and time in a second predefined format (Day, Month DD, YYYY).
    </summary>
        """
        #GetDllLibPpt().FieldType_get_DateTime2.argtypes=[]
        GetDllLibPpt().FieldType_get_DateTime2.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FieldType_get_DateTime2)
        ret = None if intPtr==None else FieldType(intPtr)
        return ret


    @staticmethod

    def get_DateTime3()->'FieldType':
        """
    <summary>
        Gets current date and time in a third predefined format (DD Month YYYY).
    </summary>
        """
        #GetDllLibPpt().FieldType_get_DateTime3.argtypes=[]
        GetDllLibPpt().FieldType_get_DateTime3.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FieldType_get_DateTime3)
        ret = None if intPtr==None else FieldType(intPtr)
        return ret


    @staticmethod

    def get_DateTime4()->'FieldType':
        """
    <summary>
        Gets current date and time in a fourth predefined format (Month DD, YYYY).
    </summary>
        """
        #GetDllLibPpt().FieldType_get_DateTime4.argtypes=[]
        GetDllLibPpt().FieldType_get_DateTime4.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FieldType_get_DateTime4)
        ret = None if intPtr==None else FieldType(intPtr)
        return ret


    @staticmethod

    def get_DateTime5()->'FieldType':
        """
    <summary>
        Gets current date and time in a fifth predefined format (DD-Mon-YY).
    </summary>
        """
        #GetDllLibPpt().FieldType_get_DateTime5.argtypes=[]
        GetDllLibPpt().FieldType_get_DateTime5.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FieldType_get_DateTime5)
        ret = None if intPtr==None else FieldType(intPtr)
        return ret


    @staticmethod

    def get_DateTime6()->'FieldType':
        """
    <summary>
        Gets current date and time in a sixth predefined format (Month YY).
    </summary>
        """
        #GetDllLibPpt().FieldType_get_DateTime6.argtypes=[]
        GetDllLibPpt().FieldType_get_DateTime6.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FieldType_get_DateTime6)
        ret = None if intPtr==None else FieldType(intPtr)
        return ret


    @staticmethod

    def get_DateTime7()->'FieldType':
        """
    <summary>
        Gets current date and time in a seventh predefined format (Mon-YY).
    </summary>
        """
        #GetDllLibPpt().FieldType_get_DateTime7.argtypes=[]
        GetDllLibPpt().FieldType_get_DateTime7.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FieldType_get_DateTime7)
        ret = None if intPtr==None else FieldType(intPtr)
        return ret


    @staticmethod

    def get_DateTime8()->'FieldType':
        """
    <summary>
        Gets current date and time in a eighth predefined format (MM/DD/YYYY hh:mm AM/PM).
    </summary>
        """
        #GetDllLibPpt().FieldType_get_DateTime8.argtypes=[]
        GetDllLibPpt().FieldType_get_DateTime8.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FieldType_get_DateTime8)
        ret = None if intPtr==None else FieldType(intPtr)
        return ret


    @staticmethod

    def get_DateTime9()->'FieldType':
        """
    <summary>
        Gets current date and time in a ninth predefined format (MM/DD/YYYY hh:mm:ss AM/PM).
    </summary>
        """
        #GetDllLibPpt().FieldType_get_DateTime9.argtypes=[]
        GetDllLibPpt().FieldType_get_DateTime9.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FieldType_get_DateTime9)
        ret = None if intPtr==None else FieldType(intPtr)
        return ret


    @staticmethod

    def get_DateTime10()->'FieldType':
        """
    <summary>
        Gets current date and time in a tenth predefined format (hh:mm).
    </summary>
        """
        #GetDllLibPpt().FieldType_get_DateTime10.argtypes=[]
        GetDllLibPpt().FieldType_get_DateTime10.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FieldType_get_DateTime10)
        ret = None if intPtr==None else FieldType(intPtr)
        return ret


    @staticmethod

    def get_DateTime11()->'FieldType':
        """
    <summary>
        Gets current date and time in a eleventh predefined format (hh:mm:ss).
    </summary>
        """
        #GetDllLibPpt().FieldType_get_DateTime11.argtypes=[]
        GetDllLibPpt().FieldType_get_DateTime11.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FieldType_get_DateTime11)
        ret = None if intPtr==None else FieldType(intPtr)
        return ret


    @staticmethod

    def get_DateTime12()->'FieldType':
        """
    <summary>
        Gets current date and time in a twelfth predefined format (hh:mm AM/PM)
    </summary>
        """
        #GetDllLibPpt().FieldType_get_DateTime12.argtypes=[]
        GetDllLibPpt().FieldType_get_DateTime12.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FieldType_get_DateTime12)
        ret = None if intPtr==None else FieldType(intPtr)
        return ret


    @staticmethod

    def get_DateTime13()->'FieldType':
        """
    <summary>
        Gets current date and time in a thirteenth predefined format (hh:mm:ss AM/PM)
    </summary>
        """
        #GetDllLibPpt().FieldType_get_DateTime13.argtypes=[]
        GetDllLibPpt().FieldType_get_DateTime13.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().FieldType_get_DateTime13)
        ret = None if intPtr==None else FieldType(intPtr)
        return ret


