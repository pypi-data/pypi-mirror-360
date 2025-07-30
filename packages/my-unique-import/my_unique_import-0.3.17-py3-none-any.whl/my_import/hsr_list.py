from typing import List, Union, TypeVar, Callable

T = TypeVar('T')


def flatten(arr: List[Union[T, List[T]]]) -> List[T]:
    """
        Flattens a nested list into a single-level list.

        Args:
        arr (List[Union[T, List[T]]]): The nested list to be flattened.

        Returns:
        List[T]: The flattened list.
    """
    flat_list = []
    for item in arr:
        if isinstance(item, list):
            flat_list.extend(flatten(item))
        else:
            flat_list.append(item)
    return flat_list


def merge_into(arr1: List[T], arr2: List[T], arr3: List[T]) -> List[T]:
    for i in arr2:
        if i not in arr1 and i not in arr3:
            arr1.append(i)
    return arr1


def not_equal(arr1: List[T], arr2: List[T]) -> bool:
    if len(arr1) != len(arr2):
        return True
    for i, j in zip(arr1, arr2):
        if i != j:
            return True
    return False


def transfer_to_tuple(*args: List[T]) -> List[tuple]:
    if not all(isinstance(arg, (list, tuple)) for arg in args):
        raise ValueError("All arguments must be lists or tuples.")
    return [tuple(elements) for elements in zip(*args)]


if __name__ == '__main__':
    print(transfer_to_tuple([1, 2, 3], [4, 5, 6]))
