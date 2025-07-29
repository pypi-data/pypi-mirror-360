# src/toolflow/core/tool_execution.py
import asyncio
import os
import threading
from concurrent.futures import ThreadPoolExecutor, wait
from typing import List, Dict, Callable, Any, Coroutine, Optional, Union, get_origin, get_args, Tuple
import inspect
from pydantic import BaseModel
import dataclasses
from enum import Enum
from .constants import RESPONSE_FORMAT_TOOL_NAME
from .exceptions import MaxToolCallsError

# ===== GLOBAL EXECUTOR (SHARED BY SYNC AND ASYNC) =====

_custom_executor: Optional[ThreadPoolExecutor] = None
_global_executor: Optional[ThreadPoolExecutor] = None
_executor_lock = threading.Lock()
_MAX_WORKERS = 4

def set_max_workers(max_workers: int) -> None:
    """Set the number of worker threads for the global executor."""
    global _global_executor
    global _MAX_WORKERS
    _MAX_WORKERS = max_workers
    with _executor_lock:
        if _global_executor:
            _global_executor.shutdown(wait=True)
            _global_executor = None

def get_max_workers() -> int:
    """Get the number of worker threads for the global executor."""
    return _MAX_WORKERS if _MAX_WORKERS else int(os.getenv("TOOLFLOW_SYNC_MAX_WORKERS", 4))

def set_executor(executor: ThreadPoolExecutor) -> None:
    """Set a custom global executor (used by both sync and async)."""
    global _global_executor
    global _custom_executor
    with _executor_lock:
        if _global_executor:
            _global_executor.shutdown(wait=True) 
        if _custom_executor:
            _custom_executor.shutdown(wait=True)
        _custom_executor = executor

def _get_sync_executor() -> ThreadPoolExecutor:
    """Get the executor for sync tool execution.
    Returns the custom executor if set, otherwise the global executor.
    """
    global _global_executor
    global _custom_executor
    
    with _executor_lock:
        if _global_executor is None and _custom_executor is None:
            max_workers = get_max_workers()
            _global_executor = ThreadPoolExecutor(
                max_workers=max_workers,
                thread_name_prefix="toolflow-"
            )
        result = _custom_executor if _custom_executor else _global_executor
        assert result is not None  # Should never be None due to logic above
        return result

def _get_async_executor() -> Optional[ThreadPoolExecutor]:
    """
    Get the executor for async tool execution.
    Returns the custom executor if set, otherwise None (uses asyncio's default).
    """
    with _executor_lock:
        return _custom_executor

# ===== TOOL EXECUTION FUNCTIONS =====
async def execute_tools_async(
    tool_calls: List[Dict[str, Any]],
    tool_map: Dict[str, Callable[..., Any]],
    graceful_error_handling: bool = True,
    parallel: bool = False
) -> List[Dict[str, Any]]:
    loop = asyncio.get_running_loop()
    results = []
    unknown_tool_results = []

    if parallel and len(tool_calls) > 1:
        all_tasks = []
        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]
            if tool_name == RESPONSE_FORMAT_TOOL_NAME:
                continue
            tool_func = tool_map.get(tool_name)
            if not tool_func:
                if graceful_error_handling:
                    unknown_tool_results.append({
                        "tool_call_id": tool_call["id"],
                        "output": f"Error: Unknown tool '{tool_name}' - tool not found in available tools",
                        "is_error": True,
                    })
                    continue
                else:
                    raise KeyError(f"Unknown tool: {tool_name}")

            if asyncio.iscoroutinefunction(tool_func):
                coro = run_async_tool(tool_call, tool_func, graceful_error_handling)
            else:
                coro = loop.run_in_executor(
                    _get_async_executor(), run_sync_tool, tool_call, tool_func, graceful_error_handling
                )
            all_tasks.append(coro)

        gathered = await asyncio.gather(*all_tasks)
        return list(gathered) + unknown_tool_results

    else:
        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]
            if tool_name == RESPONSE_FORMAT_TOOL_NAME:
                continue
            tool_func = tool_map.get(tool_name)
            if not tool_func:
                if graceful_error_handling:
                    results.append({
                        "tool_call_id": tool_call["id"],
                        "output": f"Error: Unknown tool '{tool_name}' - tool not found in available tools",
                        "is_error": True,
                    })
                    continue
                else:
                    raise KeyError(f"Unknown tool: {tool_name}")

            if asyncio.iscoroutinefunction(tool_func):
                result = await run_async_tool(tool_call, tool_func, graceful_error_handling)
            else:
                result = await loop.run_in_executor(
                    _get_async_executor(), run_sync_tool, tool_call, tool_func, graceful_error_handling
                )
            results.append(result)

        return results

def execute_tools_sync(
    tool_calls: List[Dict[str, Any]],
    tool_map: Dict[str, Callable[..., Any]],
    parallel: bool = False,
    graceful_error_handling: bool = True
) -> List[Dict[str, Any]]:
    if not tool_calls:
        return []

    for tool_call in tool_calls:
        tool_name = tool_call["function"]["name"]
        if tool_name == RESPONSE_FORMAT_TOOL_NAME:
            continue
        tool_func = tool_map.get(tool_name)
        if tool_func and asyncio.iscoroutinefunction(tool_func):
            raise RuntimeError("Async tools are not supported in sync toolflow execution")

    results = []

    if parallel and len(tool_calls) > 1:
        executor = _get_sync_executor()
        futures = []

        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]
            if tool_name == RESPONSE_FORMAT_TOOL_NAME:
                continue
            tool_func = tool_map.get(tool_name)
            if not tool_func:
                if graceful_error_handling:
                    results.append({
                        "tool_call_id": tool_call["id"],
                        "output": f"Error: Unknown tool '{tool_name}' - tool not found in available tools",
                        "is_error": True,
                    })
                    continue
                else:
                    raise KeyError(f"Unknown tool: {tool_name}")

            futures.append(executor.submit(run_sync_tool, tool_call, tool_func, graceful_error_handling))

        done, _ = wait(futures)
        for future in done:
            results.append(future.result())

    else:
        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]
            if tool_name == RESPONSE_FORMAT_TOOL_NAME:
                continue
            tool_func = tool_map.get(tool_name)
            if not tool_func:
                if graceful_error_handling:
                    results.append({
                        "tool_call_id": tool_call["id"],
                        "output": f"Error: Unknown tool '{tool_name}' - tool not found in available tools",
                        "is_error": True,
                    })
                    continue
                else:
                    raise KeyError(f"Unknown tool: {tool_name}")

            result = run_sync_tool(tool_call, tool_func, graceful_error_handling)
            results.append(result)

    return results

def _prepare_tool_arguments(tool_func: Callable[..., Any], arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare function arguments by converting JSON-like values to proper Python types.
    
    This handles conversion of:
    - Pydantic models: dict -> model.model_validate(dict)
    - Dataclasses: dict -> dataclass(**dict)
    - Enums: str/int -> enum member
    - Collections: recursive conversion of elements
    - Optional types: handle None and wrapped type
    - Generic types: List[T], Dict[K,V] with element conversion
    - Custom classes: dict -> class instance (if accepts **kwargs)
    
    Args:
        tool_func: The tool function to inspect
        arguments: Dictionary of arguments from the tool call
        
    Returns:
        Prepared arguments with proper Python types instantiated
        
    Raises:
        Exception: If argument conversion fails (validation errors are not suppressed)
    """
    sig = inspect.signature(tool_func)
    prepared_args = {}
    
    for param_name, param in sig.parameters.items():
        if param_name in arguments:
            param_annotation = param.annotation
            arg_value = arguments[param_name]
            
            # Always convert arguments and let validation errors bubble up
            # This allows the model to see validation errors and retry with corrected data
            converted_value = _convert_argument_type(param_annotation, arg_value)
            prepared_args[param_name] = converted_value
        # Note: We don't add missing arguments - let the function handle defaults/required params
    
    return prepared_args

def _convert_argument_type(target_type: Any, value: Any) -> Any:
    """
    Convert a value to the target type.
    
    Args:
        target_type: The target type annotation
        value: The value to convert
        
    Returns:
        Converted value
        
    Raises:
        Exception: If conversion fails
    """
    # If no type annotation or Any, return as-is
    if target_type is inspect.Parameter.empty or target_type is Any:
        return value
    
    # Handle Union types (including Optional which is Union[T, None]) first
    origin = get_origin(target_type)
    if origin is Union:
        union_args = get_args(target_type)
        
        # Handle Optional[T] (which is Union[T, None])
        if len(union_args) == 2 and type(None) in union_args:
            if value is None:
                return None
            # Try to convert to the non-None type
            non_none_type = next(arg for arg in union_args if arg is not type(None))
            return _convert_argument_type(non_none_type, value)
        
        # Try each type in the union until one works
        for union_type in union_args:
            try:
                return _convert_argument_type(union_type, value)
            except Exception:
                continue
        # If none worked, raise exception
        raise ValueError(f"Could not convert {value} to any type in Union {union_args}")
    
    # Handle generic types (List, Dict, etc.) before isinstance checks
    if origin is not None:
        return _convert_generic_type(target_type, value)
    
    # Now we can safely do isinstance checks for non-generic types
    # If value is already the correct type, return as-is
    try:
        if isinstance(value, target_type):
            return value
    except TypeError:
        # If isinstance fails (e.g., with some special types), continue with conversion
        pass
    
    # Handle specific types
    if inspect.isclass(target_type):
        # Pydantic BaseModel
        if issubclass(target_type, BaseModel) and isinstance(value, dict):
            return target_type.model_validate(value)
        
        # Dataclass
        if dataclasses.is_dataclass(target_type) and isinstance(value, dict):
            return target_type(**value)
        
        # Enum
        if issubclass(target_type, Enum):
            if isinstance(value, str):
                # Try by value first, then by name
                try:
                    return target_type(value)
                except ValueError:
                    return target_type[value]
            elif isinstance(value, (int, float)):
                return target_type(value)
        
        # NamedTuple
        if hasattr(target_type, '_fields') and isinstance(value, dict):
            # This is likely a NamedTuple
            return target_type(**value)
        
        # Custom class - try to instantiate with dict as kwargs
        if isinstance(value, dict):
            try:
                return target_type(**value)
            except Exception:
                pass
    
    # If we can't convert, return the original value
    return value

def _convert_generic_type(target_type: Any, value: Any) -> Any:
    """Convert values for generic types like List[T], Dict[K,V], etc."""
    origin = get_origin(target_type)
    args = get_args(target_type)
    
    # List[T]
    if origin is list and isinstance(value, list):
        if args:  # If type args provided
            element_type = args[0]
            return [_convert_argument_type(element_type, item) for item in value]
        return value
    
    # Dict[K, V]  
    if origin is dict and isinstance(value, dict):
        if len(args) >= 2:  # If key and value types provided
            key_type, value_type = args[0], args[1]
            return {
                _convert_argument_type(key_type, k): _convert_argument_type(value_type, v)
                for k, v in value.items()
            }
        return value
    
    # Tuple[T, ...] or Tuple[T1, T2, ...]
    if origin is tuple and isinstance(value, (list, tuple)):
        if args:
            # Handle Tuple[T, ...] (variable length)
            if len(args) == 2 and args[1] is Ellipsis:
                element_type = args[0]
                return tuple(_convert_argument_type(element_type, item) for item in value)
            # Handle Tuple[T1, T2, ...] (fixed length)
            else:
                converted_items = []
                for i, item in enumerate(value):
                    if i < len(args):
                        converted_items.append(_convert_argument_type(args[i], item))
                    else:
                        converted_items.append(item)
                return tuple(converted_items)
        return tuple(value)
    
    # Set[T]
    if origin is set and isinstance(value, (list, set)):
        if args:
            element_type = args[0]
            return {_convert_argument_type(element_type, item) for item in value}
        return set(value)
    
    # If we can't handle this generic type, return as-is
    return value

def run_sync_tool(tool_call: Dict[str, Any], tool_func: Callable[..., Any], graceful_error_handling: bool = True) -> Dict[str, Any]:
    try:
        # Prepare arguments by converting dictionaries to Pydantic models when needed
        prepared_args = _prepare_tool_arguments(tool_func, tool_call["function"]["arguments"])
        result = tool_func(**prepared_args)
        return {"tool_call_id": tool_call["id"], "output": result}
    except Exception as e:
        if graceful_error_handling:
            return {
                "tool_call_id": tool_call["id"],
                "output": f"Error executing tool {tool_call['function']['name']}: {e}",
                "is_error": True,
            }
        else:
            error_msg = f"""Error executing tool {tool_call['function']['name']}: {e}
            TIP: If this is a data format issue, consider clearly documenting the tool's parameters.
            """
            raise type(e)(error_msg) from e

async def run_async_tool(tool_call: Dict[str, Any], tool_func: Callable[..., Coroutine[Any, Any, Any]], graceful_error_handling: bool = True) -> Dict[str, Any]:
    try:
        # Prepare arguments by converting dictionaries to Pydantic models when needed
        prepared_args = _prepare_tool_arguments(tool_func, tool_call["function"]["arguments"])
        result = await tool_func(**prepared_args)
        return {"tool_call_id": tool_call["id"], "output": result}
    except Exception as e:
        if graceful_error_handling:
            return {
                "tool_call_id": tool_call["id"],
                "output": f"Error executing tool {tool_call['function']['name']}: {e}",
                "is_error": True,
            }
        else:
            error_msg = f"""Error executing tool {tool_call['function']['name']}: {e}
            TIP: If this is a data format issue, consider clearly documenting the tool's parameters.
            """
            raise type(e)(error_msg) from e
