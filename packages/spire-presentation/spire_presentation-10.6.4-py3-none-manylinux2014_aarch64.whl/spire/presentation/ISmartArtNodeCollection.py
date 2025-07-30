from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *

class ISmartArtNodeCollection (  SpireObject) :
    """

    """
    @property
    def Count(self)->int:
        """

        """
        GetDllLibPpt().ISmartArtNodeCollection_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNodeCollection_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().ISmartArtNodeCollection_get_Count,self.Ptr)
        return ret

    @dispatch
    def __getitem__(self, key):
        if key >= self.Count:
            raise StopIteration
        GetDllLibPpt().ISmartArtNodeCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ISmartArtNodeCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISmartArtNodeCollection_get_Item,self.Ptr, key)
        ret = None if intPtr==None else ISmartArtNode(intPtr)
        return ret

    def get_Item(self ,index:int)->'ISmartArtNode':
        """

        """
        
        GetDllLibPpt().ISmartArtNodeCollection_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ISmartArtNodeCollection_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISmartArtNodeCollection_get_Item,self.Ptr, index)
        ret = None if intPtr==None else ISmartArtNode(intPtr)
        return ret



    def AddNode(self)->'ISmartArtNode':
        """

        """
        GetDllLibPpt().ISmartArtNodeCollection_AddNode.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNodeCollection_AddNode.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISmartArtNodeCollection_AddNode,self.Ptr)
        ret = None if intPtr==None else ISmartArtNode(intPtr)
        return ret


    def RemoveNodeByIndex(self ,index:int):
        """

        """
        
        GetDllLibPpt().ISmartArtNodeCollection_RemoveNode.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPpt().ISmartArtNodeCollection_RemoveNode,self.Ptr, index)


    def RemoveNode(self ,node:'ISmartArtNode'):
        """

        """
        intPtrnode:c_void_p = node.Ptr

        GetDllLibPpt().ISmartArtNodeCollection_RemoveNodeN.argtypes=[c_void_p ,c_void_p]
        CallCFunction(GetDllLibPpt().ISmartArtNodeCollection_RemoveNodeN,self.Ptr, intPtrnode)


    def GetNodeByPosition(self ,position:int)->'ISmartArtNode':
        """

        """
        
        GetDllLibPpt().ISmartArtNodeCollection_GetNodeByPosition.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ISmartArtNodeCollection_GetNodeByPosition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISmartArtNodeCollection_GetNodeByPosition,self.Ptr, position)
        ret = None if intPtr==None else ISmartArtNode(intPtr)
        return ret



    def RemoveNodeByPosition(self ,position:int)->bool:
        """

        """
        
        GetDllLibPpt().ISmartArtNodeCollection_RemoveNodeByPosition.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ISmartArtNodeCollection_RemoveNodeByPosition.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ISmartArtNodeCollection_RemoveNodeByPosition,self.Ptr, position)
        return ret


    def AddNodeByPosition(self ,position:int)->'ISmartArtNode':
        """

        """
        
        GetDllLibPpt().ISmartArtNodeCollection_AddNodeByPosition.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().ISmartArtNodeCollection_AddNodeByPosition.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISmartArtNodeCollection_AddNodeByPosition,self.Ptr, position)
        ret = None if intPtr==None else ISmartArtNode(intPtr)
        return ret


#
#    def CopyTo(self ,array:'Array',index:int):
#        """
#
#        """
#        intPtrarray:c_void_p = array.Ptr
#
#        GetDllLibPpt().ISmartArtNodeCollection_CopyTo.argtypes=[c_void_p ,c_void_p,c_int]
#        CallCFunction(GetDllLibPpt().ISmartArtNodeCollection_CopyTo,self.Ptr, intPtrarray,index)


    @property
    def IsSynchronized(self)->bool:
        """

        """
        GetDllLibPpt().ISmartArtNodeCollection_get_IsSynchronized.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNodeCollection_get_IsSynchronized.restype=c_bool
        ret = CallCFunction(GetDllLibPpt().ISmartArtNodeCollection_get_IsSynchronized,self.Ptr)
        return ret

    @property

    def SyncRoot(self)->'SpireObject':
        """

        """
        GetDllLibPpt().ISmartArtNodeCollection_get_SyncRoot.argtypes=[c_void_p]
        GetDllLibPpt().ISmartArtNodeCollection_get_SyncRoot.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().ISmartArtNodeCollection_get_SyncRoot,self.Ptr)
        ret = None if intPtr==None else SpireObject(intPtr)
        return ret


