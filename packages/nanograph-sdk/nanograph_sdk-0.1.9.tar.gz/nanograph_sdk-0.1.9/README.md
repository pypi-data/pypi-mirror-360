# Nano SDK for Python

This package provides the Python implementation of the Nano SDK, allowing you to create node servers that communicate with the Nano orchestrator.

## Installation

The package is available on PyPI and can be installed using pip:

```bash
pip install nanograph-sdk
```

## Using with NanoCore

[NanoCore](https://github.com/nanograph/NanoCore) is the orchestrator for Nanograph servers. It manages both JavaScript and Python servers. To use your Python server with NanoCore:

1. Create a `nanoserver.json` in your project root (see [Configuration](#configuration) section for all options)
2. Register your server with [NanoCore](https://github.com/nanograph/NanoCore):
```bash
nanocore register /path/to/your/server
```
This will:
- Validate your `nanoserver.json`
- Create a Python virtual environment
- Install dependencies if you have a `requirements.txt`

3. Start all registered servers:
```bash
nanocore start
```

[NanoCore](https://github.com/nanograph/NanoCore) will:
- Start an asset server for file management
- Assign a port to your server
- Set up required environment variables (NANOCORE_ENDPOINT, NANOCORE_TOKEN)
- Start and monitor your server process
- Restart it if configuration changes

For additional commands and features, please refer to the [NanoCore documentation](https://github.com/nanograph/NanoCore).

## Usage

### Creating a Server

```python
from nanograph_sdk import NanoSDK
import asyncio

# Initialize SDK (configuration is loaded from nanoserver.json)
sdk = NanoSDK()

# Start the server
async def main():
    await sdk.start()
    print('Python Server started')

# Handle shutdown
async def shutdown_handler():
    print('Python Server is shutting down')
    # Add any cleanup logic here

sdk.on_shutdown(shutdown_handler)

# Graceful shutdown
async def run():
    try:
        await main()
    except KeyboardInterrupt:
        print('Interrupted, stopping server...')
    finally:
        await sdk.stop()

if __name__ == '__main__':
    asyncio.run(run())
```

### Configuration

The SDK requires a `nanoserver.json` file in your project root. Here's a complete example with all available options:

```json
{
    "domain": "local-python.nanograph",     // Required: Domain to group servers
    "serverName": "My Python Server",       // Required: Name of your server
    "serverUid": "my-python-server",        // Required: Unique server identifier
    "language": "python",                   // Required: Must be 'python'
    "port": 3017,                          // Optional: HTTP port (default: 3017)
    "nodesPath": "nodes",                  // Optional: Path to nodes directory
    "autoWatch": true,                     // Optional: Auto-reload on changes
    "watchDebounceTime": 500               // Optional: Debounce time for reload
}
```

| Key               | Type      | Default   | Description                                                        |
|-------------------|-----------|-----------|--------------------------------------------------------------------|
| `domain`          | `str`     | —         | Domain to group servers (required)                                |
| `serverName`      | `str`     | —         | Name of your server (required)                                     |
| `serverUid`       | `str`     | —         | Unique server identifier (required)                                |
| `language`        | `str`     | —         | Must be 'python' for Python servers (required)                    |
| `port`            | `int`     | `3017`    | HTTP port to listen on                                             |
| `nodesPath`       | `str`     | `'nodes'` | Path to the directory containing node files                        |
| `autoWatch`       | `bool`    | `True`    | If true, automatically reload nodes on file changes                |
| `watchDebounceTime`| `int`     | `500`     | Debounce time in milliseconds for file watcher reloads             |

Note: The `port` can be overridden by setting the `PORT` environment variable.

### Asset Handling

The SDK provides built-in support for handling assets through the following methods:

```python
# Instance methods
await sdk.resolve_asset(ref, options)  # Resolve an asset reference to data
sdk.get_asset_download_url(ref)        # Get direct download URL
await sdk.get_asset_presigned_url(ref) # Get a presigned URL
await sdk.upload_asset(file, options)  # Upload an asset

# Static methods (can be used without SDK instance)
await NanoSDK.resolve_asset_static(ref, options)
NanoSDK.get_asset_download_url_static(ref)
await NanoSDK.get_asset_presigned_url_static(ref)
await NanoSDK.upload_asset_static(file, options)
```

To use asset handling capabilities, the following environment variables must be set:
- `NANOCORE_ENDPOINT`: The endpoint URL for the Nanocore asset server
- `NANOCORE_TOKEN`: Authentication token for accessing the asset server

### Node Initialization

Nodes can have an optional async initialization function that will be called when the node is loaded:

```python
from nanograph_sdk import NanoSDK, NodeDefinition

# Define the node
definition = {
    'uid': 'my-node',
    'name': 'My Node',
    # ... other definition fields ...
}

# Create node instance
node = NanoSDK.register_node(definition)

# Optional async initialization function
async def init(node_instance):
    # Perform any async initialization here
    # This will be called when the node is loaded
    pass

# Export both the node and init function
export = node
```

### Creating Nodes

```python
from nanograph_sdk import NanoSDK, NodeDefinition, NodeInstance, ExecutionContext

# Define the node
definition = {
    'uid': 'my-unique-python-node-id',
    'name': 'My Python Node',
    'category': 'Processing',
    'version': '1.0.0',
    'description': 'Description of my python node',
    'inputs': [
        {'name': 'input1', 'type': 'string', 'description': 'First input'}
    ],
    'outputs': [
        {'name': 'output1', 'type': 'string', 'description': 'First output'}
    ],
    'parameters': [
        {
            'name': 'param1',
            'type': 'boolean',
            'value': True,
            'default': True,
            'label': 'Parameter 1',
            'description': 'Description of parameter 1'
        }
    ]
}

# Register the node
my_node = NanoSDK.register_node(definition)

# Implement the execution logic
async def execute_node(ctx: ExecutionContext):
    # Get input values
    input1 = ctx.inputs.get('input1', '')
    
    # Send status update
    await ctx.context['send_status']({'type': 'running', 'message': 'Processing...'})
    
    # Check for abort
    if ctx.context['is_aborted']():
        raise Exception('Execution aborted')
    
    # Process the inputs
    output1 = f'Processed by Python: {input1}'
    
    # Return the outputs
    return {'output1': output1}

my_node['execute'] = execute_node

# To export the node if it's in its own file:
# export = my_node 

Nodes are defined in `node.py` files. You can organize your nodes by placing each `node.py`
file (along with any helper modules it might need) into its own subdirectory within the
main `nodes` directory (or the path specified in `nodes_path` in the SDK configuration).
The SDK will scan these directories for `node.py` files to load the definitions.

---

## ExecutionContext Reference

When you implement a node's `execute` function, it receives a single argument: `ctx` (the execution context). This object provides everything your node needs to process inputs, parameters, and interact with the workflow engine.

**The `ExecutionContext` object has the following structure:**

| Field         | Type                | Description                                                                 |
|---------------|---------------------|-----------------------------------------------------------------------------|
| `inputs`      | `dict`              | Input values for this node, keyed by input name.                            |
| `parameters`  | `list`              | List of parameter dicts for this node (see your node definition).           |
| `context`     | `dict`              | Runtime context utilities and metadata (see below).                         |

### `ctx.context` fields

| Key            | Type        | Description                                                                 |
|----------------|-------------|-----------------------------------------------------------------------------|
| `send_status`  | `callable`  | `await ctx.context['send_status']({...})` to send a status/progress update. |
| `is_aborted`   | `callable`  | `ctx.context['is_aborted']()` returns `True` if execution was aborted.      |
| `graph_node`   | `dict`      | The full graph node definition (with position, etc).                        |
| `instance_id`  | `str`       | The workflow instance ID for this execution.                                |

**Example usage in a node:**

```python
async def execute_node(ctx):
    # Access input
    value = ctx.inputs.get('input1')
    # Access parameter
    param = next((p for p in ctx.parameters if p['name'] == 'param1'), None)
    # Send a running status
    await ctx.context['send_status']({'type': 'running', 'message': 'Working...'})
    # Check for abort
    if ctx.context['is_aborted']():
        raise Exception('Aborted!')
    # ...
```

---

## NodeStatus Reference

The `NodeStatus` object is used to communicate the current status, progress, or result of a node execution back to the orchestrator. You send it using `await ctx.context['send_status'](status)` from within your node's `execute` function.

**NodeStatus fields:**

| Field      | Type                | Description                                                          |
|------------|---------------------|----------------------------------------------------------------------|
| `type`     | `str`               | One of: `'idle'`, `'running'`, `'complete'`, `'error'`, `'missing'`  |
| `message`  | `str` (optional)    | Human-readable status or error message                               |
| `progress` | `dict` (optional)   | Progress info, e.g. `{ 'step': 2, 'total': 5 }`                      |
| `outputs`  | `dict` (optional)   | Output values (only for `'complete'` status)                         |

**Example: Sending progress updates from a node**

```python
async def execute_node(ctx):
    total_steps = 5
    for step in range(1, total_steps + 1):
        # Abort fast if needed
        if ctx.context['is_aborted']():
            raise Exception('Aborted!')
        # Simulate work
        await asyncio.sleep(1)
        # Send progress update
        await ctx.context['send_status']({
            'type': 'running',
            'message': f'Processing step {step}/{total_steps}',
            'progress': {'step': step, 'total': total_steps}
        })
    # Just return the outputs; the SDK will send the 'complete' status automatically
    return {'result': 'done'}
```

> **Note:** You do **not** need to manually send a `'complete'` status at the end. The SDK will automatically send a `'complete'` status with the outputs you return from your `execute` function.

---

## Folder Structure

Recommended project structure for a Python NanoServer:

```
my-python-nodeserver/
├── main.py           # Entry point
├── nanoserver.json   # Server configuration (required)
├── nodes/            # Nodes directory (scans for node.py files in subdirectories)
│   ├── processing/   # Category directory (optional organization)
│   │   ├── simple_text_node/   # Directory for a single node
│   │   │   └── node.py          # Node definition for simple_text_node
│   │   └── complex_math_node/ # Directory for a more complex node
│   │       ├── __init__.py    # Optional, makes 'complex_math_node' a Python package
│   │       ├── node.py        # Main node definition for complex_math_node
│   │       └── math_utils.py  # Helper functions specific to this node
│   └── another_category/      # Another category directory
│       └── another_node/      # Directory for another_node
│           └── node.py        # Node definition for another_node
├── pyproject.toml    # Dependencies and package info
└── README.md
```

## License

MIT
