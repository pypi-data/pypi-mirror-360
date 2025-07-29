from enum import Enum, auto

class StatusMessageType(Enum):
    """
    Simple flags for status messages.
    """
    InfoStatus = 0
    WarningStatus = auto()
    ErrorStatus = auto()
    SuccessStatus = auto()
    DebugStatus = auto()
    
class ContainerTypes(Enum):
    NotSpecified = 0
    Geometry = auto()
    Mesh = auto()
    Collaboration = auto()

class DataTypes(Enum):
    # Sub-shapes
    Face = 0
    Vertex = auto()
    Edge = auto()
    Element = auto()
    Node = auto()

    # Shapes
    TopoFace = auto()
    TopoEdge = auto()
    TopoVertex = auto()
    TopoWire = auto()
    TopoShell = auto()
    TopoSolid = auto()
    TopoElement = auto()
    TopoNode = auto()
    TopoMesh = auto()

    # Files
    Part = auto()
    Vector = auto()
    CoordinateSystem = auto()
    Thread = auto()
    Mesh = auto()

    # Folders
    Assembly = auto()
    Set = auto()
    Group = auto()

    # Containers
    GeometryCnt = auto()
    MeshCnt = auto()
