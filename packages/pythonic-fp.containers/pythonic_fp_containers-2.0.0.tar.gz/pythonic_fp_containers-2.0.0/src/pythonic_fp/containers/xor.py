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

"""Pythonic FP - Either monad

- *class* Xor: left biased either monad

"""

from __future__ import annotations

__all__ = ['Xor', 'LEFT', 'RIGHT']

from collections.abc import Callable, Iterator, Sequence
from typing import cast, Never, overload, TypeVar
from pythonic_fp.fptools.bool import Bool as Both, Truth as Left, Lie as Right
from pythonic_fp.fptools.singletons import Sentinel as _Sentinel
from .maybe import MayBe

L = TypeVar('L', covariant=True)
R = TypeVar('R', covariant=True)

LEFT = Left('LEFT')
RIGHT = Right('RIGHT')


class Xor[L, R]:
    """Either monad, data structure semantically containing either a left
    or a right value, but not both.

    Implements a left biased Either Monad.

    - `Xor(value: +L, LEFT)` produces a left `Xor`
    - `Xor(value: +L, RIGHT)` produces a right `Xor`

    In a Boolean context

    - `True` if a left `Xor`
    - `False` if a right `Xor`

    Two `Xor` objects compare as equal when

    - both are left values or both are right values whose values

      - are the same object
      - compare as equal

    Immutable, an `Xor` does not change after being created.

    - immutable semantics, map & bind return new instances

      - warning: contained value need not be immutable
      - warning: not hashable if value is mutable

    :: Note:
       Xor(value: +L, side: Left): Xor[+L, +R] -> left: Xor[+L, +R]
       Xor(value: +R, side: Right): Xor[+L, +R] -> right: Xor[+L, +R]
    """

    __slots__ = '_value', '_side'
    __match_args__ = ('_value', '_side')

    U = TypeVar('U', covariant=True)
    V = TypeVar('V', covariant=True)
    T = TypeVar('T')

    @overload
    def __init__(self, value: L, side: Left) -> None: ...
    @overload
    def __init__(self, value: R, side: Right) -> None: ...

    def __init__(self, value: L | R, side: Both = LEFT) -> None:
        self._value = value
        self._side = side

    def __hash__(self) -> int:
        return hash((_Sentinel('XOR'), self._value, self._side))

    def __bool__(self) -> bool:
        return self._side == LEFT

    def __iter__(self) -> Iterator[L]:
        if self:
            yield cast(L, self._value)

    def __repr__(self) -> str:
        if self:
            return 'Xor(' + repr(self._value) + ', LEFT)'
        return 'Xor(' + repr(self._value) + ', RIGHT)'

    def __str__(self) -> str:
        if self:
            return '< ' + str(self._value) + ' | >'
        return '< | ' + str(self._value) + ' >'

    def __len__(self) -> int:
        # An Xor always contains just one value.
        return 1

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False

        if self and other:
            if (self._value is other._value) or (self._value == other._value):
                return True

        if not self and not other:
            if (self._value is other._value) or (self._value == other._value):
                return True

        return False

    def get(self) -> L | Never:
        """Get value if a left.

        :: warning:
            Unsafe method ``get``. Will raise ``ValueError`` if ``Xor``
            is a right. Best practice is to first check the ``Xor`` in
            a boolean context.

        :return: its value if a Left
        :rtype: +L
        :raises ValueError: if not a left
        """
        if self._side == RIGHT:
            msg = 'Xor: get method called on a right valued Xor'
            raise ValueError(msg)
        return cast(L, self._value)

    def get_left(self) -> MayBe[L]:
        """Get value of `Xor` if a left. Safer version of `get` method.

        - if `Xor` contains a left value, return it wrapped in a MayBe
        - if `Xor` contains a right value, return MayBe()
        """
        if self._side == LEFT:
            return MayBe(cast(L, self._value))
        return MayBe()

    def get_right(self) -> MayBe[R]:
        """Get value of `Xor` if a right

        - if `Xor` contains a right value, return it wrapped in a MayBe
        - if `Xor` contains a left value, return MayBe()
        """
        if self._side == RIGHT:
            return MayBe(cast(R, self._value))
        return MayBe()

    def map_right[V](self, f: Callable[[R], V]) -> Xor[L, V]:
        """Construct new Xor with a different right."""
        if self._side == LEFT:
            return cast(Xor[L, V], self)
        return Xor[L, V](f(cast(R, self._value)), RIGHT)

    def map[U](self, f: Callable[[L], U]) -> Xor[U, R]:
        """Map over if a left value. Return new instance."""
        if self._side == RIGHT:
            return cast(Xor[U, R], self)
        return Xor(f(cast(L, self._value)), LEFT)

    def bind[U](self, f: Callable[[L], Xor[U, R]]) -> Xor[U, R]:
        """Flatmap over the left value, propagate right values."""
        if self:
            return f(cast(L, self._value))
        return cast(Xor[U, R], self)

    def map_except[U](self, f: Callable[[L], U], fallback_right: R) -> Xor[U, R]:
        """Map over if a left value - with fallback upon exception.

        - if `Xor` is a left then map `f` over its value

          - if `f` successful return a left `Xor[+U, +R]`
          - if `f` unsuccessful return right `Xor[+U, +R]`

            - swallows many exceptions `f` may throw at run time

        - if `Xor` is a right

          - return new `Xor(right=self._right): Xor[+U, +R]`

        """
        if self._side == RIGHT:
            return cast(Xor[U, R], self)

        applied: MayBe[Xor[U, R]] = MayBe()
        fall_back: MayBe[Xor[U, R]] = MayBe()
        try:
            applied = MayBe(Xor(f(cast(L, self._value)), LEFT))
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
            fall_back = MayBe(cast(Xor[U, R], Xor(fallback_right, RIGHT)))

        if fall_back:
            return fall_back.get()
        return applied.get()

    def bind_except[U](
        self, f: Callable[[L], Xor[U, R]], fallback_right: R
    ) -> Xor[U, R]:
        """Flatmap `Xor` with function `f` with fallback right

        :: warning:
            Swallows exceptions.

        :param fallback_right: fallback value if exception thrown

        """
        if self._side == RIGHT:
            return cast(Xor[U, R], self)

        applied: MayBe[Xor[U, R]] = MayBe()
        fall_back: MayBe[Xor[U, R]] = MayBe()
        try:
            if self:
                applied = MayBe(f(cast(L, self._value)))
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
            fall_back = MayBe(cast(Xor[U, R], Xor(fallback_right, RIGHT)))

        if fall_back:
            return fall_back.get()
        return applied.get()

    @staticmethod
    def sequence[U, V](sequence_xor_uv: Sequence[Xor[U, V]]) -> Xor[Sequence[U], V]:
        """Sequence an indexable of type `Xor[~U, ~V]`

        If the iterated `Xor` values are all lefts, then return an `Xor` of
        an iterable of the left values. Otherwise return a right Xor containing
        the first right encountered.

        """
        list_items: list[U] = []

        for xor_uv in sequence_xor_uv:
            if xor_uv:
                list_items.append(xor_uv.get())
            else:
                return Xor(xor_uv.get_right().get(), RIGHT)

        sequence_type = cast(Sequence[U], type(sequence_xor_uv))

        return Xor(sequence_type(list_items))  # type: ignore # subclass will be callable

    @staticmethod
    def failable_call[T, V](f: Callable[[T], V], left: T) -> Xor[V, Exception]:
        """Return Xor wrapped result of a function call that can fail

        :: warning:
            Swallows exceptions.
        """
        try:
            xor_return = Xor[V, Exception](f(left), LEFT)
        except (
            LookupError,
            ValueError,
            TypeError,
            BufferError,
            ArithmeticError,
            RecursionError,
            ReferenceError,
            RuntimeError,
        ) as exc:
            xor_return = Xor(exc, RIGHT)

        return xor_return

    @staticmethod
    def failable_index[V](v: Sequence[V], ii: int) -> Xor[V, Exception]:
        """Return an Xor of an indexed value that can fail.

        :: warning:
            Swallows exceptions.
        """
        try:
            xor_return = Xor[V, Exception](v[ii], LEFT)
        except (
            IndexError,
            TypeError,
            ArithmeticError,
            RuntimeError,
        ) as exc:
            xor_return = Xor(exc, RIGHT)

        return xor_return
