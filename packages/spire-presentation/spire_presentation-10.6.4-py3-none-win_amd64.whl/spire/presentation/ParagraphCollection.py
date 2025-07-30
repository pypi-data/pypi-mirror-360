from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *

class ParagraphCollection (  ParagraphList) :
    """
    <summary>
        Represents a collection of a paragraphs.
    </summary>
    """

    def Equals(self ,obj:'SpireObject')->bool:
        """

        """
        intPtrobj:c_void_p = obj.Ptr

        GetDllLibPpt().ParagraphCollection_Equals.argtypes=[c_void_p ,c_void_p]
        GetDllLibPpt().ParagraphCollection_Equals.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ParagraphCollection_Equals,self.Ptr, intPtrobj)
        return ret

#
#    def CopyTo(self ,array:'Array',index:int):
#        """
#    <summary>
#        Copies all elements from the collection to the specified array.
#    </summary>
#    <param name="array">Target array.</param>
#    <param name="index">Starting index in the target array.</param>
#        """
#        intPtrarray:c_void_p = array.Ptr
#
#        GetDllLibPpt().ParagraphCollection_CopyTo.argtypes=[c_void_p ,c_void_p,c_int]
#        CallCFunction(GetDllLibPpt().ParagraphCollection_CopyTo,self.Ptr, intPtrarray,index)


    @property
    def IsSynchronized(self)->bool:
        """
    <summary>
        Gets a value indicating whether access to the collection is synchronized (thread-safe).
    </summary>
        """
        GetDllLibPpt().ParagraphCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ParagraphCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """
    <summary>
        Gets a synchronization root.
            Readonly <see cref="T:System.Object" />.
    </summary>
        """
        GetDllLibPpt().ParagraphCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().ParagraphCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ParagraphCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret



    #def AddParagraphFromLatexMathCode(self ,latexMathCode:str)->'TextParagraph':
    #    """
    #<summary>
    #    Creat math equation from latex math code.
    #</summary>
    #<param name="latexMathCode">latex math code.</param>
    #    """
        
    #    GetDllLibPpt().ParagraphCollection_AddParagraphFromLatexMathCode.argtypes=[c_void_p ,c_wchar_p]
    #    GetDllLibPpt().ParagraphCollection_AddParagraphFromLatexMathCode.restype=c_void_p
    #    intPtr = CallCFunction(GetDllLibPpt().ParagraphCollection_AddParagraphFromLatexMathCode,self.Ptr, latexMathCode)
    #    ret = None if intPtr==None else TextParagraph(intPtr)
    #    return ret



    #def AddParagraphFromMathMLCode(self ,MathMLCode:str)->'TextParagraph':
    #    """
    #<summary>
    #    Creat math equation from mathML code.
    #</summary>
    #<param name="MathMLCode">mathML code.</param>
    #    """
        
    #    GetDllLibPpt().ParagraphCollection_AddParagraphFromMathMLCode.argtypes=[c_void_p ,c_wchar_p]
    #    GetDllLibPpt().ParagraphCollection_AddParagraphFromMathMLCode.restype=c_void_p
    #    intPtr = CallCFunction(GetDllLibPpt().ParagraphCollection_AddParagraphFromMathMLCode,self.Ptr, MathMLCode)
    #    ret = None if intPtr==None else TextParagraph(intPtr)
    #    return ret


