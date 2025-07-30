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

"""Pythonic FP - Maybe Monad"""

from __future__ import annotations

__all__ = ['MayBe']

from collections.abc import Callable, Iterator, Sequence
from typing import cast, Final, Never, overload, TypeVar
from pythonic_fp.fptools.singletons import Sentinel

D = TypeVar('D', covariant=True)

class MayBe[D]:
    """Maybe monad, data structure wrapping a potentially missing value.

    - where ``MayBe(value)`` contains a possible value of type ``+D``
    - ``MayBe()`` represent a non-existent or missing value of type ``+D``
    - immutable semantics

      - immutable, therefore made covariant

      - can store any item of any type, including ``None``
      - can store any value of any type with one exception

    :: warning:
        hashability invalidated if contained value is not hashable

    :: note:
       MayBe(): MayBe[+D] -> mb: Xor[+D]
       MayBe(value: +D) -> mb: Xor[+D]
    """

    U = TypeVar('U', covariant=True)
    V = TypeVar('V', covariant=True)
    T = TypeVar('T')

    __slots__ = ('_value',)
    __match_args__ = ('_value',)

    @overload
    def __init__(self) -> None: ...
    @overload
    def __init__(self, value: D) -> None: ...

    def __init__(self, value: D | Sentinel = Sentinel('MayBe')) -> None:
        self._value: D | Sentinel = value

    def __hash__(self) -> int:
        return hash((Sentinel('MayBe'), self._value))

    def __bool__(self) -> bool:
        return self._value is not Sentinel('MayBe')

    def __iter__(self) -> Iterator[D]:
        if self:
            yield cast(D, self._value)

    def __repr__(self) -> str:
        if self:
            return 'MayBe(' + repr(self._value) + ')'
        return 'MayBe()'

    def __len__(self) -> int:
        return 1 if self else 0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        if self._value is other._value:
            return True
        if self._value == other._value:
            return True
        return False

    @overload
    def get(self) -> D | Never: ...
    @overload
    def get(self, alt: D) -> D: ...

    def get(self, alt: D | Sentinel = Sentinel('MayBe')) -> D | Never:
        """Return the contained value if it exists, otherwise an alternate value.

        :: warning:
            Unsafe method ``get``. Will raise ``ValueError`` if MayBe empty
            and an alt return value not given. Best practice is to first check
            the MayBe in a boolean context.

        :rtype: +D
        :raises ValueError: when an alternate value is not provided but needed
        """
        _sentinel: Final[Sentinel] = Sentinel('MayBe')
        if self._value is not _sentinel:
            return cast(D, self._value)
        if alt is _sentinel:
            msg = 'MayBe: an alternate return type not provided'
            raise ValueError(msg)
        return cast(D, alt)

    def map[U](self, f: Callable[[D], U]) -> MayBe[U]:
        """Map function `f` over contents."""

        if self:
            return MayBe(f(cast(D, self._value)))
        return cast(MayBe[U], self)

    def bind[U](self, f: Callable[[D], MayBe[U]]) -> MayBe[U]:
        """Flatmap ``MayBe`` with function ``f``."""
        return f(cast(D, self._value)) if self else cast(MayBe[U], self)

    def map_except[U](self, f: Callable[[D], U]) -> MayBe[U]:
        """Map function ``f`` over contents.

        If ``f`` should fail, return a ``MayBe()``.

        :: warning:
            Swallows exceptions
        """
        if not self:
            return cast(MayBe[U], self)
        try:
            return MayBe(f(cast(D, self._value)))
        except (
            LookupError,
            ValueError,
            TypeError,
            BufferError,
            ArithmeticError,
            RecursionError,
            ReferenceError,
            RuntimeError,
        ):
            return MayBe()

    def bind_except[U](self, f: Callable[[D], MayBe[U]]) -> MayBe[U]:
        """Flatmap `MayBe` with function `f`.

        :: warning:
            Swallows exceptions
        """
        try:
            return f(cast(D, self._value)) if self else cast(MayBe[U], self)
        except (
            LookupError,
            ValueError,
            TypeError,
            BufferError,
            ArithmeticError,
            RecursionError,
            ReferenceError,
            RuntimeError,
        ):
            return MayBe()

    @staticmethod
    def sequence[U](sequence_mb_u: Sequence[MayBe[U]]) -> MayBe[Sequence[U]]:
        """Sequence a mutable indexable of type ``MayBe[~U]``

        If the iterated `MayBe` values are not all empty,

        - return a `MayBe` of the Sequence subtype of the contained values
        - otherwise return an empty `MayBe`

        """
        list_items: list[U] = list()

        for mb_u in sequence_mb_u:
            if mb_u:
                list_items.append(mb_u.get())
            else:
                return MayBe()

        sequence_type = cast(Sequence[U], type(sequence_mb_u))

        return MayBe(sequence_type(list_items))  # type: ignore # subclass will be callable

    @staticmethod
    def failable_call[T, V](f: Callable[[T], V], t: T) -> MayBe[V]:
        """Return MayBe wrapped result of a function call that can fail."""
        try:
            mb_return = MayBe(f(t))
        except (
            LookupError,
            ValueError,
            TypeError,
            BufferError,
            ArithmeticError,
            RecursionError,
            ReferenceError,
            RuntimeError,
        ):
            mb_return = MayBe()

        return mb_return

    @staticmethod
    def failable_index[V](vs: Sequence[V], ii: int) -> MayBe[V]:
        """Return a MayBe of an indexed value that can fail."""
        try:
            mb_return = MayBe(vs[ii])
        except (
            LookupError,
            ValueError,
            TypeError,
            BufferError,
            ArithmeticError,
            RecursionError,
            ReferenceError,
            RuntimeError,
        ):
            mb_return = MayBe()

        return mb_return
