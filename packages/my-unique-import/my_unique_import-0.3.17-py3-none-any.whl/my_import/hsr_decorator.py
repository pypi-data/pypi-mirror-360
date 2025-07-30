from typing import List, Union, TypeVar, Callable

from typing import Callable


def restruct_decorator(func_with_old_decorator: Callable, old_decorator: Callable, new_decorator: Callable) -> Callable:
    """
    Restructures a decorator by applying a new decorator to an existing function while maintaining the original function's behavior.

    Args:
    func_with_old_decorator (Callable): The function to which the old decorator is applied.
    old_decorator (Callable): The old decorator to be removed.
    new_decorator (Callable): The new decorator to be applied.

    Returns:
    Callable: The function with the old decorator removed and the new decorator applied.
    """
    original_func = func_with_old_decorator.__closure__[0].cell_contents
    return old_decorator(new_decorator(original_func))


def add_decorator(decorator: Callable, func:Callable) -> Callable:
    return decorator(func)

