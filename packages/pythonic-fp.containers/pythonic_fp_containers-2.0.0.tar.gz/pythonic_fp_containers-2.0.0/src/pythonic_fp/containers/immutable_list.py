# Copyright 2023-2025 Geoffrey R. Scheller
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Pythonic FP - Immutable guaranteed hashable lists

- hashable if elements are hashable
- declared covariant in its generic datatype
  - hashability should be enforced by LSP tooling
  - hashability will be enforced at runtime
  - ImmutableList addition supported via concatenation
  - ImmutableList integer multiplication supported

"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Hashable
from typing import cast, Never, overload, TypeVar
from pythonic_fp.iterables import FM, accumulate, concat, exhaust, merge

__all__ = ['ImmutableList', 'immutable_list']

D = TypeVar('D', covariant=True)
T = TypeVar('T')

class ImmutableList[D](Hashable):
    """Immutable List like data structure.

    - its method type parameters are also covariant
    - hashability will be enforced by LSP tooling
    - supports both indexing and slicing
    - addition concatenates results, resulting type a Union type
    - both left and right int multiplication supported
    """

    __slots__ = ('_ds', '_len', '_hash')
    __match_args__ = ('_ds', '_len')

    L = TypeVar('L')
    R = TypeVar('R')
    U = TypeVar('U')

    def __init__(self, *dss: Iterable[D]) -> None:
        if (size := len(dss)) > 1:
            msg = f'ImmutableList expects at most 1 iterable argument, got {size}'
            raise ValueError(msg)
        else:
            self._ds: tuple[D, ...] = tuple(dss[0]) if size == 1 else tuple()
            self._len = len(self._ds)
            try:
                self._hash = hash((self._len, 42) + self._ds)
            except TypeError as exc:
                msg = f'ImmutableList: {exc}'
                raise TypeError(msg)

    def __hash__(self) -> int:
        return self._hash

    def __iter__(self) -> Iterator[D]:
        return iter(self._ds)

    def __reversed__(self) -> Iterator[D]:
        return reversed(self._ds)

    def __bool__(self) -> bool:
        return bool(self._ds)

    def __len__(self) -> int:
        return len(self._ds)

    def __repr__(self) -> str:
        return 'immutable_list(' + ', '.join(map(repr, self)) + ')'

    def __str__(self) -> str:
        return '((' + ', '.join(map(repr, self)) + '))'

    def __eq__(self, other: object, /) -> bool:
        if not isinstance(other, ImmutableList):
            return NotImplemented  # magic object
        if self._len != other._len:
            return False
        if self._ds is other._ds:
            return True
        return self._ds == other._ds

    @overload
    def __getitem__(self, idx: int, /) -> D: ...
    @overload
    def __getitem__(self, idx: slice, /) -> ImmutableList[D]: ...

    def __getitem__(self, idx: slice | int, /) -> ImmutableList[D] | D:
        if isinstance(idx, slice):
            return ImmutableList(self._ds[idx])
        return self._ds[idx]

    def foldl[L](
        self,
        f: Callable[[L, D], L],
        /,
        start: L | None = None,
        default: L | None = None,
    ) -> L | None:
        """Fold Left

        - fold left with an optional starting value
        - first argument of function ``f`` is for the accumulated value
        
        "raises ValueError: when empty and a start value not given
        """
        it = iter(self._ds)
        if start is not None:
            acc = start
        elif self:
            acc = cast(L, next(it))  # L_co = D_co in this case
        else:
            if default is None:
                msg0 = 'ImmutableList: foldl method requires '
                msg1 = 'either start or default to be defined for '
                msg2 = 'an empty ImmutableList'
                raise ValueError(msg0 + msg1 + msg2)
            acc = default
        for v in it:
            acc = f(acc, v)
        return acc

    def foldr[R](
        self,
        f: Callable[[D, R], R],
        /,
        start: R | None = None,
        default: R | None = None,
    ) -> R | None:
        """Fold Right

        - fold right with an optional starting value
        - second argument of function ``f`` is for the accumulated value

        "raises ValueError: when empty and a start value not given
        """
        it = reversed(self._ds)
        if start is not None:
            acc = start
        elif self:
            acc = cast(R, next(it))
        else:
            if default is None:
                msg0 = 'ImmutableList: foldr method requires '
                msg1 = 'either start or default to be defined for '
                msg2 = 'an empty ImmutableList'
                raise ValueError(msg0 + msg1 + msg2)
            acc = default
        for v in it:
            acc = f(v, acc)
        return acc

    def __add__(self, other: ImmutableList[D], /) -> ImmutableList[D]:
        if not isinstance(other, ImmutableList):
            msg = 'ImmutableList being added to something not a ImmutableList'
            raise ValueError(msg)

        return ImmutableList(concat(self, other))

    def __mul__(self, num: int, /) -> ImmutableList[D]:
        return ImmutableList(self._ds.__mul__(num if num > 0 else 0))

    def __rmul__(self, num: int, /) -> ImmutableList[D]:
        return ImmutableList(self._ds.__mul__(num if num > 0 else 0))

    def accummulate[L](
        self, f: Callable[[L, D], L], s: L | None = None, /
    ) -> ImmutableList[L]:
        """Accumulate partial folds

        Accumulate partial fold results in an ImmutableList with
        an optional starting value.
        """
        if s is None:
            return ImmutableList(accumulate(self, f))
        return ImmutableList(accumulate(self, f, s))

    def map[U](self, f: Callable[[D], U], /) -> ImmutableList[U]:
        return ImmutableList(map(f, self))

    def bind[U](
        self, f: Callable[[D], ImmutableList[U]], type: FM = FM.CONCAT, /
    ) -> ImmutableList[U] | Never:
        """Bind function `f` to the `ImmutableList`.

        - FM Enum types

          - CONCAT: sequentially concatenate iterables one after the other
          - MERGE: round-robin merge iterables until one is exhausted
          - EXHAUST: round-robin merge iterables until all are exhausted
        """
        match type:
            case FM.CONCAT:
                return ImmutableList(concat(*map(f, self)))
            case FM.MERGE:
                return ImmutableList(merge(*map(f, self)))
            case FM.EXHAUST:
                return ImmutableList(exhaust(*map(f, self)))

        raise ValueError(f'ImmutableList: Unknown FM type: {type}')


def immutable_list[T](*ts: T) -> ImmutableList[TabError]:
    """Function to produce an ``ImmutableList`` from a variable number of arguments.

    :param ds: initial values to push onto a new ImmutableList from right to left
    """
    return ImmutableList(ts)
