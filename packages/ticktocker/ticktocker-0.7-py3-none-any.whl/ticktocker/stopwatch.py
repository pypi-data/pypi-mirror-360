from functools import wraps
from typing import Callable

from .utils import _millis, TextStyle


def _print_elapsed_time(start: float, end: float, desc: str):
    _elapsed = f'{end - start:.4f}'
    print(f'{TextStyle.green(desc)}: {TextStyle.bold(_elapsed)} ms')


class stopwatch:
    """
    A stopwatch class for measuring the
    elapsed time between two points in code.

    Args:
        desc (str): Description of the stopwatch.
        format (str): Format of the elapsed time.
        pretty (bool): Whether to convert with color.
        stream (Callable[[str], None]): The stream to print the elapsed time.
    """
    _FORMAT_LOOKUP = [
        (
            ['ms', 'milli', 'millis', 'millisecond', 'milliseconds'],
            lambda d: f'{d:.4f} ms'
        ),
        (
            ['s', 'sec', 'secs', 'second', 'seconds'],
            lambda d: f'{d / 1000:.2f} s'
        ),
        (
            ['m', 'min', 'mins', 'minute', 'minutes'],
            lambda d: f'{d / 60000:.2f} m'
        ),
        (
            ['h', 'hr', 'hrs', 'hour', 'hours'],
            lambda d: f'{d / 3600000:.2f} h'
        ),
    ]

    def __init__(
        self,
        desc: str = 'stopwatch',
        format: str = 'ms',
        *,
        pretty: bool = True,
        stream: Callable[[str], None] = print,
    ):
        self.desc = desc
        self.format = format
        self.stream = stream
        self.pretty = pretty
        self.__last = None

    # context manager
    def __enter__(self):
        self.start = _millis()
        return self

    # context manager
    def __exit__(self, *args):
        self.end = _millis()
        self.stream(
            f'{TextStyle.green(self.desc)}:'
            f'{self.to_str(self.end - self.start, self.pretty)}'
        )

    # decorator
    def __call__(
        self,
        func,
        *,
        stream: Callable[[str], None] = print,
        pretty: bool = True,
    ):
        if func is None or not callable(func):
            raise ValueError('This is a decorator')

        @wraps(func)
        def wrapper(*args, **kwargs):
            _start = _millis()
            result = func(*args, **kwargs)
            _end = _millis()
            _func_name = func.__name__
            stream(
                f'{TextStyle.green(_func_name)}:'
                f'{self.to_str(_end - _start, pretty)}'
            )
            return result
        return wrapper

    def to_str(self, elapsed: float, pretty: bool = False) -> str:
        """
        Convert elapsed time (ms) to string

        Args:
            elapsed (float): Elapsed time in milliseconds
            pretty (bool): Whether to convert with color

        Returns:
            str: Elapsed time in string format
        """
        if hasattr(self, 'pretty'):
            pretty = self.pretty
        for formats, formatter in self._FORMAT_LOOKUP:
            if self.format in formats:
                _str = formatter(elapsed)
                if pretty:
                    return TextStyle.bold(_str)
                return _str
        raise ValueError(f'Invalid format: {self.format}')

    def tick(self, return_str: bool = False) -> float | str:
        """
        Measure the elapsed time between two consecutive calls.

        .. code-block:: python
            >>> import time
            >>> sw = stopwatch()
            >>> for _ in range(3):
            ...     if delta := sw.tick(True):
            ...         print(delta)
            ...     time.sleep(1)
            ...
            1000.0000 ms
            1000.0000 ms

        Returns:
            float: Elapsed time in milliseconds.
                   Returns negative value on first call (False)
                   or empty string on first call (True)
        """
        now = _millis()
        if self.__last is None:
            self.__last = now
            return '' if return_str else -1.0

        elapsed = now - self.__last
        self.__last = now

        if return_str:
            return self.to_str(elapsed, self.pretty)
        return elapsed
