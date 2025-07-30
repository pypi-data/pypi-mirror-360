import asyncio
import json
import logging
from typing import Callable, Dict, Optional, Any, Union

from aiohttp import web

from .interfaces import (
    NodeInstance,
    RequestExecutionMessage,
    StopWorkflowInstanceMessage,
    AckMessage,
    NodeStatusMessage,
    NodeStatus,
    BaseMessage # For type checking parsed message
)
from .node_executor import execute_node, abort_executions_for_instance, active_node_execution_tasks, get_execution_key

class MessageHandler:
    def __init__(self,
                 server_uid: str,
                 node_registry: Dict[str, NodeInstance],
                 logger: Optional[logging.Logger] = None):
        self.server_uid = server_uid
        self.node_registry = node_registry
        self.logger = logger or logging.getLogger(f"NanoSDK.MessageHandler.{server_uid}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'[%(asctime)s] [%(levelname)s] [NanoSDK] @{self.server_uid} (MessageHandler) %(message)s',
                '%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.propagate = False
            self.logger.setLevel(logging.INFO)

    async def process_message(self, message_str: str, ws: web.WebSocketResponse) -> bool:
        try:
            parsed_message: BaseMessage = json.loads(message_str)
            msg_type = parsed_message.get('type')

            if not msg_type:
                self.logger.warning("Received message without type")
                return False

            self.logger.debug(f"Processing message type: {msg_type}")

            if msg_type == 'request_execution':
                # Cast to the specific message type
                exec_request_msg = RequestExecutionMessage(**parsed_message)
                # Don't await, let it run in the background
                asyncio.create_task(self._handle_execution_request(exec_request_msg, ws))
                return True
            
            elif msg_type == 'stop_workflow_instance':
                stop_workflow_msg = StopWorkflowInstanceMessage(**parsed_message)
                return await self._handle_stop_workflow(stop_workflow_msg, ws)
            
            else:
                self.logger.info(f"Unhandled message type: {msg_type}")
                return False
                
        except json.JSONDecodeError:
            self.logger.error(f"Error decoding JSON message: {message_str[:200]}") # Log a snippet
            return False
        except TypeError as e: # Catches errors from Pydantic-like **unpacking if fields are missing/wrong type
            self.logger.error(f"Error processing message due to type mismatch or missing fields: {e}. Message: {message_str[:200]}")
            return False
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    async def _send_status_update(self, 
                                 ws: web.WebSocketResponse, 
                                 instance_id: str, 
                                 node_id: int, 
                                 node_uid: str, # For logging purposes
                                 status: NodeStatus) -> None:
        message = NodeStatusMessage(
            type='node_status',
            serverUid=self.server_uid,
            instanceId=instance_id,
            payload={
                'nodeId': node_id,
                'status': status
            }
        )
        try:
            if not ws.closed:
                await ws.send_str(json.dumps(message))
                status_type = status.get('type', 'unknown')
                status_msg = status.get('message', '')
                log_msg_suffix = f" - {status_msg}" if status_msg else ""
                self.logger.debug(f"Instance {instance_id}: Sent status update for Node ID {node_id} (UID {node_uid}): {status_type}{log_msg_suffix}")
            else:
                self.logger.warning(f"Instance {instance_id}: WebSocket closed for Node ID {node_id} status {status.get('type')}. Cannot send update.")
        except Exception as e:
            self.logger.error(f"Instance {instance_id}: Error sending status update for Node ID {node_id}: {e}")

    async def _handle_execution_request(self, message: RequestExecutionMessage, ws: web.WebSocketResponse) -> None:
        instance_id = message['instanceId']
        payload = message['payload']
        node_id = payload['nodeId']
        node_uid = payload['nodeUid']
        graph_node = payload['graphNode']
        inputs = payload['inputs']

        self.logger.info(f"Instance {instance_id}: Received request_execution for Node ID: {node_id}, UID: {node_uid}, graphNode.id: {graph_node['id']}")

        # Create a closure for on_status_update
        async def on_status_update_for_node(status: NodeStatus) -> None:
            await self._send_status_update(ws, instance_id, node_id, node_uid, status)
        
        execution_key = get_execution_key(instance_id, graph_node['id'])
        
        try:
            self.logger.debug(f"Instance {instance_id}: Calling node_executor for Node ID {node_id} (UID {node_uid}).")
            
            # Create and store the task
            current_task = asyncio.create_task(
                execute_node(
                    instance_id=instance_id,
                    node_uid=node_uid,
                    graph_node=graph_node,
                    inputs=inputs,
                    on_status_update=on_status_update_for_node,
                    node_registry=self.node_registry,
                    logger=self.logger # Pass logger to executor
                )
            )
            active_node_execution_tasks[execution_key] = current_task
            await current_task # Wait for the node execution to complete or raise an error
            self.logger.debug(f"Instance {instance_id}: node_executor finished for Node ID {node_id} (UID {node_uid}).")
        
        except asyncio.CancelledError:
            self.logger.info(f"Instance {instance_id}: Execution task for Node ID {node_id} (UID {node_uid}) was cancelled.")
            await on_status_update_for_node({'type': 'error', 'message': 'Execution cancelled'})
        except Exception as e: # Catch errors from execute_node itself (e.g., node not found)
            self.logger.error(f"Instance {instance_id}: Error during execute_node setup or synchronous part for Node ID {node_id} (UID {node_uid}): {e}")
            # Error status would have been sent by execute_node or its on_status_update
            # Ensure it is, or send a generic one if not.
            # Typically, execute_node should handle its own error reporting via on_status_update.
            pass # Assuming execute_node sends its own error status
        finally:
            if execution_key in active_node_execution_tasks:
                del active_node_execution_tasks[execution_key]

    async def _handle_stop_workflow(self, message: StopWorkflowInstanceMessage, ws: web.WebSocketResponse) -> bool:
        instance_id = message['instanceId']
        self.logger.info(f"Instance {instance_id}: Processing stop_workflow_instance request.")

        aborted_count = abort_executions_for_instance(instance_id, self.server_uid, self.logger)
        
        ack_payload: Dict[str, Any] = {
            'success': True,
            'message': f'Stop workflow request acknowledged. Attempted to abort {aborted_count} active node(s) on this server for instance {instance_id}.'
        }
        
        ack_message = AckMessage(
            type='ack_stop_workflow',
            serverUid=self.server_uid,
            instanceId=instance_id,
            payload=ack_payload
        )
        
        try:
            if not ws.closed:
                await ws.send_str(json.dumps(ack_message))
                self.logger.info(f"Sent ack_stop_workflow for instance {instance_id}")
            else:
                self.logger.warning(f"WebSocket closed for instance {instance_id}. Cannot send ack_stop_workflow.")
            return True
        except Exception as e:
            self.logger.error(f"Error sending ack_stop_workflow for instance {instance_id}: {e}")
            return False 