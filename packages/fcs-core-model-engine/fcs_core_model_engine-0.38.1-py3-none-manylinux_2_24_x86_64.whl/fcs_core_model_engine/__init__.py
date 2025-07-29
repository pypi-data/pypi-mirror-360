# Salome legacy
from .fcscore import (
    GEOM_Object,
    GEOM_Field,
    GEOMAlgo_State
)

# OCC legacy
from .fcscore import (
    TColStd_HSequenceOfTransient,
    TopAbs_ShapeEnum,
    ExplodeType,
    ComparisonConditionGeometry,
    ShapeKind,
    SICheckLevel
)

# Core
from .fcscore import (
    ComparisonCondition,
    Color,
    ColorSelection,
    Palette,
    XYZ
)

# Geometry
from .fcscore import (
    GeometricShape,
    Geometry3DPrimitives,
    ExtGeometry3DPrimitives,
    GeometryBasicOperations,
    GeometryBlockOperations,
    GeometryBooleanOperations,
    ExtGeometryBooleanOperations,
    GeometryCurveOperations,
    GeometryFieldOperations,
    GeometryGroupOperations,
    GeometryHealingOperations,
    ExtGeometryHealingOperations,
    GeometryInsertOperations,
    GeometryLocalOperations,
    GeometryMeasureOperations,
    ExtGeometryMeasureOperations,
    GeometryShapeOperations,
    ExtGeometryShapeOperations,
    GeometryTransformOperations,
    ImportOperations,
    ExportOperations
)

# Mesh
from .fcscore import (
    EdgeSeedingParameters,
    ElementDimension,
    ElementReferences,
    ElementShape,
    SolverElementType,
    MeshElementOrder,
    Mesh2DAlgorithmChoice,
    Mesh3DAlgorithmChoice,
    Target3DMeshType,
    RecombineAll,
    RecombinationAlgorithm,
    RecombineNodePositioning,
    Mesh2DSettings,
    Mesh3DSettings,
    Mesh,
    Element,
    Node,
    ElementSet,
    NodeSet,
    MasterMesh,
    ComponentMesh,
    MeshFactory,
    Mesher3D,
    Quality2DResult,
    QualityMeasure,
    MeshReferenceType,
    MeshFileFormat,
    MeshTransaction,
    SolverProfile,
    ElementShapeToModel,
    ElementAttributes,
    GenericElementType
)

# Model
from .fcscore import (
    Model,
    ItemType,
    StoredEntityType,
    ModelConfiguration,
    ModelItemInstance,
    GeometryInstance,
    MeshComponentInstance,
    MeshSetInstance
)
# Backend Service template
from .fcsservice import ( 
    BackendService,
    fcs_command
)  

# Logger
from .fcslogger import ( 
    FCSLogger,
    DiagnosticLog,
    create_generic_logger
)

# Enum options 
from .fcsoptions import ( 
    StatusMessageType,
    ContainerTypes,
    DataTypes
)

# Geometry builder
from .geometrybuilder import GeometryBuilder

# Cloud model session communicator base class
from .fcsmodelsession import CloudModelCommunicatorBase