"""Decorators for serverless functions"""

import functools
import inspect
import threading
from typing import Any, Callable, Optional, TypeVar, cast

# Thread-local storage for tracking decorator usage
_context = threading.local()

F = TypeVar("F", bound=Callable[..., Any])


def keynet_function(name: str) -> Callable[[F], F]:
    """
    Decorator to mark a function as a Keynet serverless function.

    This decorator must be applied to the main function to enable validation,
    packaging, and deployment through FunctionBuilder. Once applied to main,
    it enables usage in nested function calls.

    The decorated function must have exactly one parameter named 'args'.

    Args:
        name: The name of the function (required)

    Returns:
        The decorated function

    Example:
        @keynet_function("my-serverless-function")
        def main(args):
            # In OpenWhisk runtime, args will contain:
            # {"__ow_runtime": True, "your_param": "value", ...}
            return {"message": "Hello World"}

    """
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Function name must be a non-empty string")

    def decorator(func: F) -> F:
        # Validate function signature
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())

        # Must have exactly one parameter named 'args'
        if len(params) != 1 or params[0] != "args":
            raise ValueError(
                f"@keynet_function decorated function must have exactly one parameter "
                f"named 'args'. Found: {params}"
            )

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Set context to indicate we're inside a keynet function
            is_root = not hasattr(_context, "inside_keynet_function")
            if is_root:
                _context.inside_keynet_function = True

            try:
                # Check if running in OpenWhisk runtime
                if args and len(args) > 0:
                    # Validate args[0] is a dict
                    if not isinstance(args[0], dict):
                        raise TypeError(
                            f"Expected 'args' parameter to be a dict, got {type(args[0]).__name__}"
                        )

                    # Check for OpenWhisk runtime flag
                    if args[0].get("__ow_runtime", False):
                        # Import here to avoid circular dependency
                        from ..config import load_env

                        load_env(args[0])

                result = func(*args, **kwargs)
                return result
            finally:
                # Clear context only if this was the root function
                if is_root and hasattr(_context, "inside_keynet_function"):
                    del _context.inside_keynet_function

        # Add metadata to the function
        wrapper._keynet_function = True  # type: ignore[attr-defined]
        wrapper._keynet_name = name  # type: ignore[attr-defined]

        return cast("F", wrapper)

    return decorator


def is_inside_keynet_function() -> bool:
    """
    Check if the current execution context is inside a keynet function.

    Returns:
        True if currently executing inside a function decorated with @keynet_function

    """
    return getattr(_context, "inside_keynet_function", False)


def get_function_metadata(func: Callable) -> Optional[dict[str, Any]]:
    """
    Get metadata for a keynet function.

    Args:
        func: The function to check

    Returns:
        Dictionary with metadata if the function is decorated, None otherwise

    """
    if hasattr(func, "_keynet_function") and getattr(func, "_keynet_function", False):
        return {"name": getattr(func, "_keynet_name", ""), "is_keynet_function": True}
    return None
