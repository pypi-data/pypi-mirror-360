import asyncio
import logging
from typing import Dict, Callable, Optional, Coroutine, Any
from types import SimpleNamespace

from .interfaces import (
    GraphNode,
    NodeInputs,
    NodeOutputs,
    NodeStatus,
    NodeInstance,
    ExecutionContext,
    ExecutionContextData
)

# Map to store active asyncio.Tasks for cancellable node executions
active_node_execution_tasks: Dict[str, asyncio.Task] = {}
# Map to store AbortController-like events for signaling cancellation
active_node_abort_events: Dict[str, asyncio.Event] = {}

def get_execution_key(instance_id: str, node_id: int) -> str:
    return f"{instance_id}-{node_id}"

async def execute_node(
    instance_id: str,
    node_uid: str,
    graph_node: GraphNode,
    inputs: NodeInputs,
    on_status_update: Callable[[NodeStatus], Coroutine[Any, Any, None]], # Takes NodeStatus, returns an awaitable
    node_registry: Dict[str, NodeInstance],
    logger: Optional[logging.Logger] = None
) -> NodeOutputs:
    
    effective_logger = logger or logging.getLogger(f"NanoSDK.NodeExecutor.{graph_node.get('serverUid', 'unknown')}")
    if not effective_logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            f"[%(asctime)s] [%(levelname)s] [NanoSDK] @{graph_node.get('serverUid', 'unknown')} (NodeExecutor) %(message)s",
            '%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        effective_logger.addHandler(handler)
        effective_logger.propagate = False
        effective_logger.setLevel(logging.INFO) # Reverted to INFO
    else:
        # If logger already exists, revert its level if we changed it, or ensure it's INFO
        # This logic might need to be smarter if levels are managed more dynamically elsewhere
        # For now, ensure it's at least INFO if we had set it to DEBUG
        if effective_logger.level == logging.DEBUG: # Check if we specifically set it to DEBUG
             effective_logger.setLevel(logging.INFO) # Revert to INFO

    execution_key = get_execution_key(instance_id, graph_node['id'])
    server_uid = graph_node.get('serverUid') or 'unknown'

    abort_event = asyncio.Event()
    active_node_abort_events[execution_key] = abort_event
    effective_logger.info("--------------------------------------------------------")
    effective_logger.info(f"EXECUTE_NODE: Created abort_event for key {execution_key}. Event object_id: {id(abort_event)}, initial state: {abort_event.is_set()}")
    effective_logger.info("--------------------------------------------------------")
    effective_logger.info(f"Instance {instance_id}: Attempting to execute node {graph_node['id']} (UID: {node_uid}). Key: {execution_key}")

    node_instance = node_registry.get(node_uid)

    if not node_instance:
        error_msg = f"Node definition not found: {node_uid}"
        await on_status_update({'type': 'error', 'message': error_msg})
        if execution_key in active_node_abort_events: # Clean up abort event
            del active_node_abort_events[execution_key]
        raise ValueError(error_msg)

    try:
        await on_status_update({'type': 'running', 'message': 'Starting execution...'})

        def is_aborted_with_logging():
            is_set = abort_event.is_set()
            effective_logger.debug(f"IS_ABORTED_CHECK: Key {execution_key}, Event object_id: {id(abort_event)}, is_set() -> {is_set}")
            return is_set

        context_data: ExecutionContextData = {
            'send_status': lambda status: asyncio.create_task(on_status_update(status)),
            'is_aborted': is_aborted_with_logging, # Use the new logging wrapper
            'graph_node': graph_node,
            'instance_id': instance_id
        }
        
        # Create a dictionary first, then convert to SimpleNamespace
        execution_context_dict: ExecutionContext = {
            'inputs': inputs,
            'parameters': graph_node['parameters'],
            'context': context_data
        }
        execution_context_obj = SimpleNamespace(**execution_context_dict)

        # The user's execute function can be a regular function or an async function
        node_execute_fn = node_instance['execute']
        
        if asyncio.iscoroutinefunction(node_execute_fn):
            outputs = await node_execute_fn(execution_context_obj)
        else:
            # Run synchronous function in a thread pool to avoid blocking asyncio event loop
            loop = asyncio.get_event_loop()
            outputs = await loop.run_in_executor(None, node_execute_fn, execution_context_obj)

        if not abort_event.is_set():
            status_update: NodeStatus = {
                'type': 'complete',
                'message': 'Execution finished.',
                'outputs': outputs
            }
            await on_status_update(status_update)
            effective_logger.info(f"Instance {instance_id}: Node {graph_node['id']} (UID: {node_uid}) execution successful.")
        else:
            effective_logger.info(f"Instance {instance_id}: Node {graph_node['id']} (UID: {node_uid}) execution was aborted.")
            # Optionally send a specific 'aborted' status if your protocol supports it
            # await on_status_update({'type': 'error', 'message': 'Execution aborted by request'}) 

        return outputs

    except Exception as e:
        error_message = str(e)
        effective_logger.error(f"Instance {instance_id}: Error executing node {graph_node['id']} (UID: {node_uid}): {error_message}")
        import traceback
        effective_logger.error(traceback.format_exc())
        
        if not abort_event.is_set():
            await on_status_update({'type': 'error', 'message': error_message})
        # Do not re-raise if aborted, as the abort itself is the primary event.
        # Re-raising here might cause an additional error message to be sent if not handled carefully.
        if not abort_event.is_set():
             raise # Re-raise the original error if not aborted
        return {} # Return empty dict or similar if aborted during an error

    finally:
        if execution_key in active_node_abort_events:
            del active_node_abort_events[execution_key]
        if execution_key in active_node_execution_tasks:
            del active_node_execution_tasks[execution_key]
        effective_logger.info(f"Instance {instance_id}: Cleaned up for {execution_key}. AbortEvents: {len(active_node_abort_events)}, Tasks: {len(active_node_execution_tasks)}")

def abort_node_execution(instance_id: str, node_id: int, server_uid: str, logger: Optional[logging.Logger] = None) -> bool:
    effective_logger = logger or logging.getLogger(f"NanoSDK.NodeExecutor.{server_uid}")
    # Ensure logger is configured if it was dynamically created
    if not effective_logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            f"[%(asctime)s] [%(levelname)s] [NanoSDK] @{server_uid} (NodeExecutor - Abort) %(message)s",
            '%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        effective_logger.addHandler(handler)
        effective_logger.propagate = False
        effective_logger.setLevel(logging.INFO) # Reverted to INFO
    else:
        # Revert level if we changed it
        if effective_logger.level == logging.DEBUG: # Check if we specifically set it to DEBUG
            effective_logger.setLevel(logging.INFO) # Revert to INFO

    key = get_execution_key(instance_id, node_id)
    abort_event = active_node_abort_events.get(key)
    if abort_event:
        effective_logger.info(f"ABORT_NODE_EXECUTION: Found event for key: {key}. Event object_id: {id(abort_event)}. Current state before set: {abort_event.is_set()}")
        abort_event.set()
        effective_logger.info(f"ABORT_NODE_EXECUTION: Event for key {key} set. New state after set: {abort_event.is_set()}")
        
        # Cancel the task if it's still tracked (it might have finished)
        task = active_node_execution_tasks.get(key)
        if task and not task.done():
            task.cancel()
            effective_logger.info(f"Cancelled task for key: {key}")
        return True
    else:
        effective_logger.warning(f"No active execution found to abort for key: {key}")
        return False

def abort_executions_for_instance(instance_id: str, server_uid: str, logger: Optional[logging.Logger] = None) -> int:
    effective_logger = logger or logging.getLogger(f"NanoSDK.NodeExecutor.{server_uid}")
    aborted_count = 0
    effective_logger.info(f"Attempting to abort all executions for instance: {instance_id}")
    
    # Iterate over a copy of keys as the dictionary might change during iteration
    keys_to_check = list(active_node_abort_events.keys())

    for key in keys_to_check:
        if key.startswith(f"{instance_id}-"):
            node_id_str = key.split("-")[-1]
            try:
                node_id = int(node_id_str)
                if abort_node_execution(instance_id, node_id, server_uid, effective_logger):
                    aborted_count += 1
            except ValueError:
                 effective_logger.error(f"Could not parse node_id from key {key} (extracted part: '{node_id_str}') during instance abort.")
            except Exception as e:
                 effective_logger.error(f"Error aborting node for key {key} during instance abort: {e}")

    if aborted_count > 0:
        effective_logger.info(f"Aborted {aborted_count} node executions for instance {instance_id}.")
    else:
        effective_logger.info(f"No active node executions found to abort for instance {instance_id}.")
    
    return aborted_count 