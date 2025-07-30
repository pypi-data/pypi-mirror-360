# Copyright (c) 2025 Kris Jordan
# Licensed under the MIT License.
from vibe_farm.__about__ import __license__, __copyright__
from typing import Callable, Any
import inspect
import importlib.util
import os


def farm(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator that replaces a function/method with a .vibe.py implementation if available.

    This decorator looks for a corresponding .vibe.py file in the same directory as
    the decorated function or method. If found, it attempts to load a function/method
    with the same name and compatible signature from that file and use it as a replacement.

    The replacement strategy:
    1. Locate the original function's module file
    2. Look for a corresponding .vibe.py file
    3. Load the vibe module and find a function/method with the same name
    4. For methods, look inside the same class name in the vibe module
    5. Verify the function signatures are compatible (same parameter names)
    6. Return the vibe function/method if all checks pass, otherwise return the original

    Args:
        fn: The function or method to potentially replace.

    Returns:
        Either the replacement function/method from .vibe.py or the original function/method.
    """
    # Step 1: Get the module containing the original function
    module = inspect.getmodule(fn)
    if not module or not hasattr(module, "__file__"):
        return fn

    # Step 2: Determine the path to the corresponding .vibe.py file
    original_file = module.__file__
    if original_file is None:
        return fn

    vibe_file_path = _get_vibe_file_path(original_file)
    if not os.path.exists(vibe_file_path):
        return fn

    # Step 3: Load the vibe module
    vibe_module = _load_vibe_module(vibe_file_path, module.__name__)
    if vibe_module is None:
        return fn

    # Step 4: Find the replacement function/method in the vibe module
    vibe_function = _find_vibe_function(fn, vibe_module)
    if vibe_function is None:
        return fn

    # Step 5: Verify the function signatures are compatible
    if not _signatures_match(fn, vibe_function):
        return fn

    # Step 6: Return the replacement function/method
    return vibe_function


def _get_vibe_file_path(original_file: str) -> str:
    """Return the path to the companion ``.vibe.py`` file.

    ``original_file`` may be a relative path depending on how the module was
    executed. Using :func:`os.path.abspath` normalises the value so that the
    accompanying vibe file can be reliably located regardless of the current
    working directory.
    """
    absolute = os.path.abspath(original_file)
    base, _ = os.path.splitext(absolute)
    return base + ".vibe.py"


def _load_vibe_module(vibe_file_path: str, module_name: str) -> object | None:
    """Loads and returns the vibe module, or None if loading fails."""
    try:
        spec = importlib.util.spec_from_file_location(
            module_name + "_vibe", vibe_file_path
        )
        if not spec or not spec.loader:
            return None

        vibe_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(vibe_module)
        return vibe_module
    except Exception:
        return None


def _find_vibe_function(
    original_fn: Callable[..., Any], vibe_module: object
) -> Callable[..., Any] | None:
    """Finds the corresponding function/method in the vibe module.

    For standalone functions, looks for a function with the same name.
    For class methods, looks for the method within the same class name.

    Args:
        original_fn: The original function/method to find a replacement for
        vibe_module: The loaded vibe module to search in

    Returns:
        The replacement function/method, or None if not found
    """
    # Check if this is a method by looking at the qualified name
    # Methods will have a qualified name like "ClassName.method_name"
    qualname_parts = original_fn.__qualname__.split(".")

    if len(qualname_parts) == 1:
        # This is a standalone function
        vibe_function = getattr(vibe_module, original_fn.__name__, None)
        return vibe_function if callable(vibe_function) else None

    elif len(qualname_parts) == 2:
        # This is a method: get class name and method name
        class_name, method_name = qualname_parts

        # Look for the class in the vibe module
        vibe_class = getattr(vibe_module, class_name, None)
        if vibe_class is None or not inspect.isclass(vibe_class):
            return None

        # Look for the method in the vibe class
        vibe_method = getattr(vibe_class, method_name, None)
        return vibe_method if callable(vibe_method) else None

    else:
        # Nested classes or other complex cases - try as standalone function first
        vibe_function = getattr(vibe_module, original_fn.__name__, None)
        return vibe_function if callable(vibe_function) else None


def _signatures_match(
    original_fn: Callable[..., Any], vibe_fn: Callable[..., Any]
) -> bool:
    """Checks if two functions have compatible signatures (same parameter names)."""
    original_params = list(inspect.signature(original_fn).parameters.keys())
    vibe_params = list(inspect.signature(vibe_fn).parameters.keys())
    return original_params == vibe_params
