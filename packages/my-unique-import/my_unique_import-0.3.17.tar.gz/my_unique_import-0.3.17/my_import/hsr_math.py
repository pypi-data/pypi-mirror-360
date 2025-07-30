import math
import random
import sys
from typing import List, Union, TypeVar, Callable

T = TypeVar('T')


def truncate_with_floor(number: float, digits: int = 0):
    if digits == 0:
        return math.floor(number)
    stepper = 10 ** digits
    return math.floor(number * stepper) / stepper


def product(arr: List[Union[int, float]]) -> Union[int, float]:
    if sys.version_info >= (3.8, 0):
        return math.prod(arr)
    else:
        from functools import reduce
        return reduce(lambda x, y: x * y, arr)


def choose(best_choice: Callable[[List[T]], T], actions: List[T], epsilon: float = 0.5) -> T:
    return random.choice(actions) if random.random() < epsilon else best_choice(actions)


def random_choice(array: List[T]) -> T:
    return random.choice(array)


def probability(value: float) -> bool:
    rand_number = random.uniform(0, 1)
    return rand_number <= value


def set_minus(set1: List[T], set2: List[T]) -> List[T]:
    return [i for i in set1 if i not in set2]


if __name__ == '__main__':
    from performer_helper import TimeIt

    with TimeIt():
        print(product([1, 2, 3, 4, 5, 6, 7]))
