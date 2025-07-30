"""Protocol and message type definitions for the Nanograph SDK"""

from typing import TypedDict, List, Dict, Any, Literal, Optional, Union

class NodeDefinition(TypedDict):
    """Node definition structure"""
    uid: str
    name: str
    description: str
    type: Literal['client', 'server']
    inputs: List[Dict[str, Any]]
    outputs: List[Dict[str, Any]]
    parameters: List[Dict[str, Any]]

class NodeStatus(TypedDict):
    """Node status information"""
    status: str
    message: Optional[str]

class NodeInputs(TypedDict):
    """Node input data"""
    pass

class NodeOutputs(TypedDict):
    """Node output data"""
    pass

class NodeContext(TypedDict):
    """Node execution context"""
    inputs: NodeInputs
    outputs: NodeOutputs
    status: NodeStatus

class NodeResponse(TypedDict):
    """Node execution response"""
    outputs: NodeOutputs
    status: NodeStatus

class NodeDefinitionsMessage(TypedDict):
    """Message containing node definitions"""
    type: Literal['definitions']
    definitions: List[NodeDefinition]

class ExecuteNodeMessage(TypedDict):
    """Message for node execution request"""
    type: Literal['execute']
    nodeUid: str
    inputs: NodeInputs

class NodeStatusMessage(TypedDict):
    """Message for node status update"""
    type: Literal['status']
    nodeUid: str
    status: NodeStatus

class NodeOutputsMessage(TypedDict):
    """Message for node outputs update"""
    type: Literal['outputs']
    nodeUid: str
    outputs: NodeOutputs 