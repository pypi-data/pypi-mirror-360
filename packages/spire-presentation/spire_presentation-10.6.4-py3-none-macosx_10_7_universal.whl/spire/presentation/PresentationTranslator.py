from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class PresentationTranslator (SpireObject) :
    """
    <summary>
        Presetation translator
    </summary>
<author>linyaohu</author>
    """
#
#    def AddDrawingRel(self ,xdoc:'XmlDocument',nm:'XmlNamespaceManager',resultFile:str):
#        """
#    <summary>
#         add the drawing relationships to the files bescause of the smartArt picture fill
#    </summary>
#    <param name="xdoc">origianl file</param>
#    <param name="resultFile">result</param>
#        """
#        intPtrxdoc:c_void_p = xdoc.Ptr
#        intPtrnm:c_void_p = nm.Ptr
#
#        GetDllLibPpt().PresentationTranslator_AddDrawingRel.argtypes=[c_void_p ,c_void_p,c_void_p,c_wchar_p]
#        CallCFunction(GetDllLibPpt().PresentationTranslator_AddDrawingRel,self.Ptr, intPtrxdoc,intPtrnm,resultFile)


