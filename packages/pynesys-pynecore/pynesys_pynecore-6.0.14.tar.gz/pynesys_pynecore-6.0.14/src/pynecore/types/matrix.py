from typing import TypeVar, Generic
from .na import NA

T = TypeVar('T')


class Matrix(Generic[T]):
    """
    A matrix implementation in pure Python
    """

    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.data = [[NA(T) for _ in range(cols)] for _ in range(rows)]
