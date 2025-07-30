import inspect
import ast
from .setup_paths import get_call_position
from .performer_helper import timeit
import types


def get_called_functions(func):
    if not isinstance(func, (types.FunctionType, types.MethodType)):
        print(f"Warning: {func} is not a function or method")
        return set()

    try:
        source = inspect.getsource(func)
    except OSError as e:
        print(f"Warning: Could not get source for {func.__name__}: {e}")
        return set()
    except IndentationError as e:
        print(f"Warning: Indentation error in source of {func.__name__}: {e}")
        return set()

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"Warning: Syntax error in source of {func.__name__}: {e}")
        return set()

    called_functions = set()

    class FunctionCallVisitor(ast.NodeVisitor):
        def visit_Call(self, node):
            if isinstance(node.func, ast.Name):
                if not node.func.id.startswith('_'):
                    called_functions.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    if not node.func.attr.startswith('_'):
                        called_functions.add(f"{node.func.value.id}.{node.func.attr}")
                elif isinstance(node.func.value, ast.Attribute):
                    if not node.func.attr.startswith('_'):
                        called_functions.add(f"{node.func.value.attr}.{node.func.attr}")
            self.generic_visit(node)

    FunctionCallVisitor().visit(tree)
    return called_functions


def find_function_in_modules(func_name, current_module):
    # 如果函数名包含属性（如对象方法）
    if '.' in func_name:
        obj_name, method_name = func_name.split('.')
        try:
            obj = getattr(current_module, obj_name)
            if hasattr(obj, method_name):
                func = getattr(obj, method_name)
                if callable(func):
                    return func
        except AttributeError:
            pass
    else:
        try:
            func = getattr(current_module, func_name)
            if callable(func):
                return func
        except AttributeError:
            pass
    return None


def find_all_called_functions(func, location=False, detect_obj=False):
    all_called_functions = []
    to_process = [(func, None, get_call_position(func))] if location else [(func, None)]

    while to_process:
        res = to_process.pop(0)
        if len(res) == 2:
            current_func, parent_func = res
        else:
            current_func, parent_func, _ = res
        if current_func in [f[0] for f in all_called_functions]:
            continue

        if location:
            all_called_functions.append((current_func, parent_func, get_call_position(current_func)))
        else:
            all_called_functions.append((current_func, parent_func))

        try:
            called_functions = get_called_functions(current_func)
        except (OSError, IndentationError, SyntaxError):
            continue

        current_module = inspect.getmodule(current_func)

        for func_name in called_functions:
            func_obj = find_function_in_modules(func_name, current_module)
            if detect_obj and func_obj is None:
                for obj_name, obj in inspect.getmembers(current_module, inspect.isclass):
                    if hasattr(obj, func_name):
                        func_obj = getattr(obj, func_name)
                        break
            if location and func_obj:
                to_process.append((func_obj, current_func, get_call_position(func_obj)))
            elif func_obj:
                to_process.append((func_obj, current_func))

    return all_called_functions


def auto_timeit(all_called_functions, min_time=1E-4):
    decorated_funcs = {}
    for item in all_called_functions:
        func = item[0]
        module = inspect.getmodule(func)
        if module:
            func_name = func.__name__
            if func_name not in decorated_funcs:
                decorated_funcs[func_name] = timeit(func, min_time=min_time)
            setattr(module, func_name, decorated_funcs[func_name])
