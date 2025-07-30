from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class MotionPath ( SpireObject ) :

    @dispatch
    def __init__(self):
        GetDllLibPpt().MotionPath_CreateMotionPath.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPpt().MotionPath_CreateMotionPath)
        super(MotionPath, self).__init__(intPtr)
    """

    """
    @dispatch
    def __getitem__(self, key):
        if key >= self.Count:
            raise StopIteration
        GetDllLibPpt().MotionPath_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().MotionPath_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().MotionPath_get_Item,self.Ptr, key)
        ret = None if intPtr==None else MotionCmdPath(intPtr)
        return ret

    def Add(self ,pathType:'MotionCommandPathType',pts:'PointF[]',ptsType:'MotionPathPointsType',bRelativeCoord:bool)->int:
    #    """
    #<summary>
    #    Add new command to path
    #</summary>
    #<param name="type">Motion Command Path Type</param>
    #<param name="pts">Motion Path Points</param>
    #<param name="ptsType">Motion Path PointsType</param>
    #<param name="bRelativeCoord">Relative Coord</param>
    #    """
        enumtype:c_int = pathType.value
        #arraypts:ArrayTypepts = ""
        countpts = len(pts)
        ArrayTypepts = c_void_p * countpts
        arraypts = ArrayTypepts()
        for i in range(0, countpts):
            arraypts[i] = pts[i].Ptr

        enumptsType:c_int = ptsType.value

        GetDllLibPpt().MotionPath_Add.argtypes=[c_void_p ,c_int,ArrayTypepts,c_int,c_int,c_bool]
        GetDllLibPpt().MotionPath_Add.restype=c_int
        ret = CallCFunction(GetDllLibPpt().MotionPath_Add,self.Ptr, enumtype,arraypts,countpts,enumptsType,bRelativeCoord)
        return ret


    @property
    def Count(self)->int:
        """
    <summary>
        Gets the number of paths in the collection.
    </summary>
        """
        GetDllLibPpt().MotionPath_get_Count.argtypes=[c_void_p]
        GetDllLibPpt().MotionPath_get_Count.restype=c_int
        ret = CallCFunction(GetDllLibPpt().MotionPath_get_Count,self.Ptr)
        return ret


    def get_Item(self ,index:int)->'MotionCmdPath':
        """
    <summary>
        Gets a command at the specified index.
    </summary>
    <param name="index"></param>
    <returns></returns>
        """
        
        GetDllLibPpt().MotionPath_get_Item.argtypes=[c_void_p ,c_int]
        GetDllLibPpt().MotionPath_get_Item.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().MotionPath_get_Item,self.Ptr, index)
        ret = None if intPtr==None else MotionCmdPath(intPtr)
        return ret



    def GetEnumerator(self)->'IEnumerator':
        """
    <summary>
        Gets an iterator for the collection.
    </summary>
    <returns>Iterator.</returns>
        """
        GetDllLibPpt().MotionPath_GetEnumerator.argtypes=[c_void_p]
        GetDllLibPpt().MotionPath_GetEnumerator.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPpt().MotionPath_GetEnumerator,self.Ptr)
        ret = None if intPtr==None else IEnumerator(intPtr)
        return ret


