"""Core interfaces and types for the Nanograph SDK"""

import asyncio
from typing import TypedDict, List, Dict, Any, Callable, Coroutine, Union, Optional, Literal
from ..types.protocol import (
    NodeDefinition,
    NodeStatus,
    NodeInputs,
    NodeOutputs,
    NodeContext,
    NodeResponse,
    NodeDefinitionsMessage
)

# Type Aliases from shared/src/types.ts
PortType = Literal[
    "string",
    "number",
    "boolean",
    "array",
    "object",
    "any",
    "asset"
]

NodeType = Literal['client', 'server']

ParameterType = Literal['number', 'text', 'slider', 'boolean', 'select', 'color', 'filepicker']

NodeStatusType = Literal['idle', 'running', 'complete', 'error', 'missing']

class Port(TypedDict):
    """Port definition for node inputs/outputs"""
    uid: str
    name: str
    type: str

class ParameterOption(TypedDict):
    value: str
    label: str

class Parameter(TypedDict):
    """Parameter definition"""
    uid: str
    name: str
    type: str
    value: Any
    default: Any
    label: Optional[str]
    description: Optional[str]
    min: Optional[Union[int, float]]
    max: Optional[Union[int, float]]
    step: Optional[Union[int, float]]
    precision: Optional[int]
    range: Optional[List[Union[int, float]]]
    options: Optional[List[ParameterOption]]
    multiline: Optional[bool]

class NodeStatus(TypedDict):
    type: NodeStatusType
    message: Optional[str]
    progress: Optional[Dict[str, int]] # {'step': 1, 'total': 10}
    outputs: Optional[Dict[str, Any]]

class NodeDefinition(TypedDict):
    uid: str
    name: str
    category: str
    version: str
    description: Optional[str]
    type: NodeType 
    inputs: List[Port]
    outputs: List[Port]
    parameters: List[Parameter]
    active: Optional[bool]
    muted: Optional[bool]
    resizable: Optional[bool]
    width: Optional[int]
    height: Optional[int]
    minWidth: Optional[int]
    maxWidth: Optional[int]
    minHeight: Optional[int]
    maxHeight: Optional[int]
    layout: Optional[str]
    serverUid: Optional[str]
    domain: Optional[str]
    status: Optional[NodeStatus]

class GraphNode(TypedDict):
    """Node in the execution graph"""
    id: int
    uid: str
    name: str
    category: str
    version: str
    description: Optional[str]
    inputs: List[Port]
    outputs: List[Port]
    parameters: List[Parameter]
    serverUid: str
    domain: Optional[str]
    # Optional UI-related fields that might be needed
    x: Optional[float]
    y: Optional[float]
    width: Optional[float]
    height: Optional[float]
    muted: Optional[bool]
    active: Optional[bool]
    status: Optional[NodeStatus]

NodeInputs = Dict[str, List[Any]]
NodeOutputs = Dict[str, List[Any]]

# Interfaces from nodejs/src/interfaces.ts, adapted for Python

class NanoSDKConfig(TypedDict, total=False):
    """Configuration for the NanoSDK"""
    domain: str
    server_name: str
    server_uid: str
    language: Literal['python', 'javascript']
    port: Optional[int]
    nodes_path: Optional[str]
    auto_watch: Optional[bool]
    watch_debounce_time: Optional[int]

# Type aliases
ExecuteFunction = Callable[[NodeContext], Union[NodeResponse, Coroutine[Any, Any, NodeResponse]]]

class NodeInstance(TypedDict):
    """Instance of a node with its definition and execute function"""
    definition: NodeDefinition
    execute: ExecuteFunction

# Protocol types from shared/src/protocol.ts
NanoServerStatus = Literal['disconnected', 'connecting', 'connected', 'error']

class NanoServer(TypedDict):
    name: str
    serverUid: str # Maintained camelCase for consistency with JS side
    domain: Optional[str] # i.e: "local-eu-west-1.nanograph"
    url: Optional[str]
    status: Optional[NanoServerStatus]
    nodeDefinitions: Optional[List[NodeDefinition]] # Maintained camelCase

class BaseMessage(TypedDict):
    type: str
    serverUid: str # Maintained camelCase
    instanceId: Optional[str] # Maintained camelCase
    payload: Optional[Any]

class HandshakeMessage(BaseMessage):
    # type: Literal['handshake'] # Already in BaseMessage, will be set by sender
    payload: NanoServer

class NodeDefinitionsMessagePayload(TypedDict):
    nodeDefinitions: List[NodeDefinition] # Maintained camelCase

class NodeDefinitionsMessage(BaseMessage):
    # type: Literal['definitions_update']
    payload: NodeDefinitionsMessagePayload

class RequestExecutionMessagePayload(TypedDict):
    nodeId: int # Maintained camelCase
    nodeUid: str # Maintained camelCase
    graphNode: GraphNode # Maintained camelCase
    inputs: NodeInputs

class RequestExecutionMessage(BaseMessage):
    # type: Literal['request_execution']
    instanceId: str # This is required
    payload: RequestExecutionMessagePayload

class NodeStatusMessagePayload(TypedDict):
    nodeId: int # Maintained camelCase
    status: NodeStatus

class NodeStatusMessage(BaseMessage):
    # type: Literal['node_status']
    instanceId: str # This is required
    payload: NodeStatusMessagePayload

class StopWorkflowInstanceMessage(BaseMessage):
    # type: Literal['stop_workflow_instance']
    instanceId: str # This is required

class AckMessagePayload(TypedDict):
    message: Optional[str]
    success: Optional[bool]
    nodeId: Optional[int] # Maintained camelCase

class AckMessage(BaseMessage):
    # type will be specific like 'ack_stop_workflow'
    payload: Optional[AckMessagePayload]

# Graph-related types
class ExecutionContextData(TypedDict):
    """Execution context data for node execution"""
    send_status: Callable[[NodeStatus], asyncio.Task]
    is_aborted: Callable[[], bool]
    graph_node: GraphNode
    instance_id: str

class ExecutionContext(TypedDict):
    """Complete execution context for node execution"""
    inputs: NodeInputs
    parameters: List[Parameter]
    context: ExecutionContextData 