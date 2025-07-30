# Copyright 2023-2024 Geoffrey R. Scheller
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

"""
### Double-Ended (DE) Queue

- stateful DE queue data structures with amortized O(1) pushes and pops each end
- obtaining length (number of elements) of a queue is an O(1) operation
- implemented in a "has-a" relationship with a Python list based circular array
- will resize itself larger as needed

"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Sequence
from typing import Never, overload, TypeVar

from pythonic_fp.circulararray import CA
from pythonic_fp.containers.maybe import MayBe as MB


__all__ = ['DEQueue', 'de_queue']

D = TypeVar('D')


class DEQueue[D]:
    """Double Ended Queue

    - stateful Double-Ended (DEQueue) data structure
    - order of initial data retained, as if pushed on from the right
    """
    L = TypeVar('L')
    R = TypeVar('R')

    __slots__ = ('_ca',)

    U = TypeVar('U')

    def __init__(self, *dss: Iterable[D]) -> None:
        if (size := len(dss)) < 2:
            self._ca = CA(dss[0]) if size == 1 else CA()
        else:
            msg = f'DEQueue expects at most 1 iterable argument, got {size}'
            raise TypeError(msg)

    def __bool__(self) -> bool:
        return len(self._ca) > 0

    def __len__(self) -> int:
        return len(self._ca)

    def __eq__(self, other: object, /) -> bool:
        if not isinstance(other, DEQueue):
            return False
        return self._ca == other._ca

    @overload
    def __getitem__(self, idx: int, /) -> D: ...
    @overload
    def __getitem__(self, idx: slice, /) -> Sequence[D]: ...

    def __getitem__(self, idx: int | slice, /) -> D | Sequence[D] | Never:
        if isinstance(idx, slice):
            msg = 'dtool.restictive queues are not slicable by design'
            raise NotImplementedError(msg)
        return self._ca[idx]

    def __iter__(self) -> Iterator[D]:
        return iter(list(self._ca))

    def __reversed__(self) -> Iterator[D]:
        return reversed(list(self._ca))

    def __repr__(self) -> str:
        if len(self) == 0:
            return 'DQ()'
        return 'DQ(' + ', '.join(map(repr, self._ca)) + ')'

    def __str__(self) -> str:
        return '>< ' + ' | '.join(map(str, self)) + ' ><'

    def copy(self) -> DEQueue[D]:
        """Return a shallow copy of the ``DEQueue``."""
        return DEQueue(self._ca)

    def pushl(self, *ds: D) -> None:
        """Push data onto left side (front) of ``DEQueue``."""
        self._ca.pushl(*ds)

    def pushr(self, *ds: D) -> None:
        """Push data onto right side (rear) of ``DEQueue``.
        Like a Python List, does not return a value.
        """
        self._ca.pushr(*ds)

    def popl(self) -> MB[D]:
        """Pop Data from left side (front) of ``DEQueue``.

        - pop left most item off of queue, return item in a maybe monad
        - returns an empty ``MB()`` if queue is empty
        """
        if self._ca:
            return MB(self._ca.popl())
        return MB()

    def popr(self) -> MB[D]:
        """Pop Data from right side (rear) of ``DEQueue``.

        - pop right most item off of queue, return item in a maybe monad
        - returns an empty ``MB()`` if queue is empty
        """
        if self._ca:
            return MB(self._ca.popr())
        return MB()

    def peakl(self) -> MB[D]:
        """Peak left side of ``DEQueue``.

        - return left most value in a maybe monad
        - does not consume the item
        - returns an empty ``MB()`` if queue is empty
        """
        if self._ca:
            return MB(self._ca[0])
        return MB()

    def peakr(self) -> MB[D]:
        """Peak right side of ``DEQueue``.

        - return right most value in a maybe monad
        - does not consume the item
        - returns an empty ``MB()`` if queue is empty
        """
        if self._ca:
            return MB(self._ca[-1])
        return MB()

    def foldl[L](self, f: Callable[[L, D], L], initial: L | None = None, /) -> MB[L]:
        """Reduce left to right with ``f`` using an optional initial value.

        - note that when an initial value is not given then ``~L = ~D``
        - if iterable empty & no initial value given, return ``MB()``
        - traditional FP type order given for function ``f``
        """
        if initial is None:
            if not self._ca:
                return MB()
        return MB(self._ca.foldl(f, initial))

    def foldr[R](self, f: Callable[[D, R], R], initial: R | None = None, /) -> MB[R]:
        """Reduce right to left with ``f`` using an optional initial value.

        - note that when an initial value is not given then ``~R = ~D``
        - if iterable empty & no initial value given, return ``MB()``
        - traditional FP type order given for function ``f``
        """
        if initial is None:
            if not self._ca:
                return MB()
        return MB(self._ca.foldr(f, initial))

    def map[U](self, f: Callable[[D], U], /) -> DEQueue[U]:
        """Map a function over ``DEQueue``.

        - map the function ``f`` over the ``DEQueue``

          - left to right
          - retain original order

        - returns a new instance
        """
        return DEQueue(map(f, self._ca))


def de_queue[D](*ds: D) -> DEQueue[D]:
    """Create a ``DEQueue`` from the function arguments."""
    return DEQueue(ds)
