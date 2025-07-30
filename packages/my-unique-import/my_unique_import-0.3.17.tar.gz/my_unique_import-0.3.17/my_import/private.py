import inspect
from typing import Callable, TypeVar, List

_class_source_info_cache = {}
T = TypeVar('T')


def get_class_source_info(cls):
    if cls not in _class_source_info_cache:
        source_lines, starting_line_no = inspect.getsourcelines(cls)
        file_name = inspect.getfile(cls)
        _class_source_info_cache[cls] = (starting_line_no, starting_line_no + len(source_lines) - 1, file_name)
    return _class_source_info_cache[cls]


def get_calling_context(cls=None):
    caller_frame = inspect.currentframe().f_back.f_back
    file_name = caller_frame.f_code.co_filename
    line_no = caller_frame.f_lineno
    if cls is None:
        local_vars = caller_frame.f_locals
        instance = local_vars['self']
        cls = type(instance)
    start_line_no, end_line_no, class_file_name = get_class_source_info(cls)
    if file_name != class_file_name or not (start_line_no <= line_no <= end_line_no):
        return True
    return False


def private(func):
    def wrapper(*args, **kwargs):
        if get_calling_context():
            raise AttributeError(f"The function '{func.__name__}' is private")
        return func(*args, **kwargs)

    return wrapper


class PrivateMeta(type):
    _private_list: List[str] = []
    _constant_list: List[str] = []

    def __new__(cls, name, bases, dct):

        original_setattr = dct.get('__setattr__', None)
        original_getattr = dct.get('__getattribute__', None)

        for key, value in dct.items():
            if key.startswith('private_'):
                cls._private_list.append(key[8:])
            elif key.startswith('const_'):
                cls._constant_list.append(key[6:])

        def __setattr__(self, item, value):

            if item.startswith('private_'):
                item = item[8:]
                cls._private_list.append(item)

            elif item.startswith('const_'):
                item = item[6:]
                cls._constant_list.append(item)

            position = get_calling_context(self.__class__.__bases__[0])

            if position:
                if item in cls._private_list:
                    raise AttributeError(f"The attribute '{item}' is private")
                elif item in cls._constant_list:
                    raise AttributeError(f"The attribute '{item}' is const")

            if original_setattr:
                original_setattr(self, item, value)
            else:
                super(self.__class__, self).__setattr__(item, value)

        def __getattribute__(self, item):

            if item.startswith('private_'):
                item = item[8:]
            elif item.startswith('const_'):
                item = item[6:]

            if item in cls._private_list and get_calling_context(self.__class__.__bases__[0]):
                raise AttributeError(f"The attribute '{item}' is private")

            if original_getattr:
                return original_getattr(self, item)
            else:
                return object.__getattribute__(self, item)

        def get_private(self):
            return cls._private_list

        def get_const(self):
            return cls._constant_list

        dct['__setattr__'] = __setattr__
        dct['__getattribute__'] = __getattribute__
        dct['get_private'] = get_private
        dct['const_private'] = get_const

        return super().__new__(cls, name, bases, dct)


class PrivateClass:

    def __init__(self, cls: T):
        self.cls = cls

    def __call__(self, *args, **kwargs) -> T:
        cls_dict = dict(self.cls.__dict__)
        cls_dict.pop('__dict__', None)
        cls_dict.pop('__weakref__', None)
        cls_dict.pop('__module__', None)
        cls_dict.pop('__doc__', None)

        Wrapped = PrivateMeta(self.cls.__name__, (self.cls,), cls_dict)
        instance = Wrapped(*args, **kwargs)
        return instance


@PrivateClass
class MyClass:
    private_horse: int
    const_pi: float
    say: Callable

    def __init__(self):
        self.private_horse = 10
        self.const_pi = 3.14

    def private_say(self):
        print("Hello, world!")

    def say_normal(self):
        self.horse = 12
        print(self.horse)
        print("Hello, world!")
