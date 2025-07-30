import asyncio
import inspect
import threading
from typing import Any
from langchain.tools import StructuredTool
from langchain_mcp_adapters.client import MultiServerMCPClient

class MultiServerMCPClient_Sync:
    """The upstream langchain-mcp-adapters client is written in async, so we need to wrap it in a sync class."""
    def __init__(self, servers_config):
        self.servers_config = servers_config
        self.client = None
        self.tools = []

        # Create a new event loop in a separate thread
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.thread.start()

        # Initialize client and get tools
        future = asyncio.run_coroutine_threadsafe(self._setup_client(), self.loop)
        # Wait for initialization to complete
        future.result()

    def _run_event_loop(self):
        """Runs the event loop in a separate thread."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def _setup_client(self):
        """Initialize the client and tools."""
        self.client = MultiServerMCPClient(self.servers_config)
        await self.client.__aenter__()
        
        # Get tools and create sync wrappers
        tools_async = self.client.get_tools()
        for tool in tools_async:
            self.tools.append(self._wrap_async_tool(tool))

    def _wrap_async_tool(self, async_tool):
        """Creates a synchronous wrapper for an async tool with proper signature."""

        schema_fields = {}

        if async_tool.args_schema:
            if isinstance(async_tool.args_schema, dict) and 'properties' in async_tool.args_schema:
                # JSON Schema format
                properties = async_tool.args_schema.get('properties', {})
                required_params = async_tool.args_schema.get('required', [])

                for param_name, param_info in properties.items():
                     # Map JSON Schema types to Python types
                    type_map = {
                        'string': str,
                        'integer': int,
                        'number': float,
                        'boolean': bool,
                        'array': list,
                        'object': dict
                    }
                    param_type = type_map.get(param_info.get('type'), Any)

                    if param_name in required_params:
                        default_value = inspect._empty
                    else:
                        default_value = param_info.get('default', None)

                    schema_fields[param_name] = (param_type, default_value)
            else:
                raise NotImplementedError("Only JSON Schema format is supported for tool.args_schema")

        # Create parameter string for the dynamic function definition
        param_parts = []
        for name, (type_hint, default) in schema_fields.items():
            type_name = getattr(type_hint, "__name__", "Any")
            param_part = f"{name}: {type_name}"
            if default is not inspect._empty:
                param_part += f" = {repr(default)}"
            param_parts.append(param_part)

        param_str = ", ".join(param_parts)

        # Escaped tool name (to avoid conflicts with Python keywords and leading decimals in names)
        _async_tool_name = f'_{async_tool.name}'.replace('-', '_').replace('.', '_')

        def _execute_async_func(kwargs):
            filtered_kwargs = {}
            for k, v in kwargs.items():
                _, default_value = schema_fields.get(k, (Any, inspect._empty))
                if default_value is inspect._empty:
                    filtered_kwargs[k] = v
                elif v != default_value:
                    filtered_kwargs[k] = v
                else:
                    # v == default_value: skip passing values already declared as defaults
                    pass

            return asyncio.run_coroutine_threadsafe(
                async_tool.coroutine(**filtered_kwargs),
                self.loop
            ).result()

        func_str = f"""
def {_async_tool_name}({param_str}):
    \"\"\"
{async_tool.description}
    \"\"\"
    kwargs = locals()
    return _execute_async_func(kwargs)
"""

        namespace = {
            '_execute_async_func': _execute_async_func,
            'Any': Any,
        }

        exec(func_str, namespace)

        sync_func = namespace[_async_tool_name]

        return StructuredTool(
            name=_async_tool_name,
            description=async_tool.description,
            func=sync_func,
            args_schema=async_tool.args_schema,
            return_direct=getattr(async_tool, "return_direct", False),
            tags=getattr(async_tool, "tags", None),
            coroutine=None
        )

    def get_tools_sync(self):
        """Get all tools as synchronous functions."""
        return self.tools
    
    def close(self):
        """Properly shut down the client and event loop."""
        if self.client:
            future = asyncio.run_coroutine_threadsafe(
                self.client.__aexit__(None, None, None), 
                self.loop
            )
            future.result()  # Wait for exit to complete
            
            # Stop the event loop and join the thread
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.thread.join()

