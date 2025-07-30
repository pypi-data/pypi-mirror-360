import functools
import time
from typing import Optional, Callable, Union
import line_profiler


def timeit(func, min_time=0):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        if elapsed_time >= min_time:
            print(f"Function '{func.__name__}' took {end_time - start_time} seconds to execute.")
        return result

    return wrapper


class TimeIt:
    start_time: float
    end_time: float
    execution_time: float
    round: Optional[int]

    def __init__(self, round: Optional[int] = None, by_line: bool = False, output_unit='auto'):
        self.round = round
        self.logger = []
        self.by_line = by_line
        self.profiler = line_profiler.LineProfiler() if by_line else None
        self.output_unit = output_unit

    def _init(self, round: Optional[int] = None, by_line: bool = None, output_unit=None):
        if round is not None:
            self.round = round
        if by_line is not None:
            self.by_line = by_line
        if output_unit is not None:
            self.output_unit = output_unit

    def add(self, func):
        if self.by_line and self.profiler:
            self.profiler.add_function(func)

    def __enter__(self):
        self.start_time = time.time()
        if self.by_line:
            self.profiler.enable_by_count()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.by_line and self.profiler:
            self.profiler.disable_by_count()
        self.execution_time = time.time() - self.start_time
        if self.output_unit == 'auto':
            if self.execution_time >= 1:
                unit = 1
            elif self.execution_time >= 1e-3:
                unit = 1e-3
            else:
                unit = 1e-6
        else:
            unit = self.convert_output_unit(self.output_unit)
        if self.round is not None:
            formatted_time = round(self.execution_time, self.round)
        else:
            formatted_time = self.execution_time
        print(
            f"Execution time: {formatted_time:.{self.round}f} seconds" if self.round is not None else f"Execution time: {formatted_time} seconds")
        self.logger.append(self.execution_time)
        if self.by_line and self.profiler:
            self.profiler.print_stats(output_unit=unit)
            self.profiler = line_profiler.LineProfiler()

    @staticmethod
    def convert_output_unit(unit: Union[str, float]) -> float:
        if unit == 's':
            return 1
        elif unit == 'ms':
            return 1e-3
        elif unit == 'us':
            return 1e-6
        else:
            return unit

    def clear(self):
        self.logger.clear()
        self.profiler = line_profiler.LineProfiler()

    def clear_profiler(self):
        self.profiler = line_profiler.LineProfiler()

    def list_comprehension(self):
        numbers = self.logger
        return [current - previous for previous, current in zip(numbers[:-1], numbers[1:])]

    def profile_function(self, enable_timing: bool = False) -> Callable:
        """Decorator to profile a function with line_profiler if by_line is True."""

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if enable_timing:
                    with self:
                        result = func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                return result

            if self.by_line and self.profiler:
                self.profiler.add_function(func)

            return wrapper

        return decorator

    def __call__(self, round: Optional[int] = None, by_line: bool = None, output_unit=None):
        self._init(round, by_line, output_unit)
        return self
