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

"""Pythonic FP - Functional Tuple"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import cast, Never, overload
from pythonic_fp.iterables import FM, accumulate, concat, exhaust, merge

__all__ = ['FunctionalTuple', 'functional_tuple']

class FunctionalTuple[D](tuple[D, ...]):
    """Functional Tuple suitable for inheritance

    - Supports both indexing and slicing
    - FunctionalTuple addition and int multiplication supported

      - addition concatenates results, resulting in a Union type
      - both left and right int multiplication supported
      - homogeneous in its data type
      - supports being further inherited from
      - unslotted
    """

    def __reversed__(self) -> Iterator[D]:
        for ii in range(len(self) - 1, -1, -1):
            yield (self[ii])

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(' + ', '.join(map(repr, self)) + ')'

    def __eq__(self, other: object, /) -> bool:
        if not isinstance(other, self.__class__):
            return False
        if (length := len(self)) != len(other):
            return False
        if self is other:
            return True
        for ii in range(length):
            if self[ii] != other[ii]:
                return False
        return True

    @overload    # type:ignore
    def __getitem__(self, x: int) -> D: ...
    @overload
    def __getitem__(self, x: slice) -> tuple[D, ...]: ...

    def __getitem__(self, idx: int | slice, /) -> tuple[D, ...] | D:
        def newtup(tup: tuple[D, ...]) -> tuple[D, ...]:
            return tup[0:-1] + tup[-1:]

        if isinstance(idx, slice):
            return self.__class__(newtup(super().__getitem__(idx)))
        else:
            return super().__getitem__(idx)

    def foldl[L](
        self,
        f: Callable[[L, D], L],
        /,
        start: L | None = None,
        default: L | None = None,
    ) -> L | None:
        """Fold Left

        - fold left with an optional starting value
        - first argument of function f is for the accumulated value

        :raises ValueError: when FunctionalTuple empty and a start value not given
        """
        it = iter(self)
        if start is not None:
            acc = start
        elif self:
            acc = cast(L, next(it))
        else:
            if default is None:
                msg = 'Both start and default cannot be None for an empty FunctionalTuple'
                raise ValueError('FunctionalTuple.foldl - ' + msg)
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
        - second argument of function f is for the accumulated value

        :raises ValueError: when FunctionalTuple empty and a start value not given
        """
        it = reversed(self)
        if start is not None:
            acc = start
        elif self:
            acc = cast(R, next(it))
        else:
            if default is None:
                msg = 'Both start and default cannot be None for an empty FunctionalTuple'
                raise ValueError('FunctionalTuple.foldR - ' + msg)
            acc = default
        for v in it:
            acc = f(v, acc)
        return acc

    def copy(self) -> FunctionalTuple[D]:
        """Return a shallow copy of ``FunctionalTuple`` in O(1) time & space complexity."""
        return self.__class__(self)

    def __add__(self, other: object, /) -> tuple[D, ...]:
        if not isinstance(other, FunctionalTuple):
            msg = 'FunctionalTuple being added to something not an FunctionalTuple'
            raise ValueError(msg)
        return self.__class__(concat(self, other))

    def __mul__(self, num: int, /) -> tuple[D, ...]:
        return self.__class__(super().__mul__(num))

    def __rmul__(self, num: int, /) -> tuple[D]:
        return self.__class__(super().__rmul__(num))

    def accummulate[L](
        self, f: Callable[[L, D], L], s: L | None = None, /
    ) -> FunctionalTuple[L]:
        """Accumulate partial folds

        Accumulate partial fold results in an ``FunctionalTuple`` with an optional
        starting value.
        """
        if s is None:
            return FunctionalTuple(accumulate(self, f))
        return FunctionalTuple(accumulate(self, f, s))

    def map[U](self, f: Callable[[D], U], /) -> FunctionalTuple[U]:
        return FunctionalTuple(map(f, self))

    def bind[U](
        self, f: Callable[[D], FunctionalTuple[U]], type: FM = FM.CONCAT, /
    ) -> FunctionalTuple[U] | Never:
        """Bind function ``f`` to the ``FunctionalTuple``.

        - FM Enum types

          - CONCAT: sequentially concatenate iterables one after the other
          - MERGE: round-robin merge iterables until one is exhausted
          - EXHAUST: round-robin merge iterables until all are exhausted

        :param ds: values to instantiate FunctionalTuple
        :return: resulting FunctionalTuple
        """
        match type:
            case FM.CONCAT:
                return FunctionalTuple(concat(*map(f, self)))
            case FM.MERGE:
                return FunctionalTuple(merge(*map(f, self)))
            case FM.EXHAUST:
                return FunctionalTuple(exhaust(*map(f, self)))

        raise ValueError('Unknown FM type')


def functional_tuple[D](*ds: D):
    """Construct a ``FunctionalTuple`` from arguments.

    :param ds: values to instantiate FunctionalTuple
    :return: resulting FunctionalTuple
    """
    return FunctionalTuple(ds)
