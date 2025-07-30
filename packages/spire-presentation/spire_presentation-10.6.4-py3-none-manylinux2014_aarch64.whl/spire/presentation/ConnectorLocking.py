from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.presentation.common import *
from spire.presentation import *
from ctypes import *
import abc

class ConnectorLocking (  SimpleShapeBaseLocking) :
    """
    <summary>
        Indicates which operations are disabled on the parent Connector.
    </summary>
    """
