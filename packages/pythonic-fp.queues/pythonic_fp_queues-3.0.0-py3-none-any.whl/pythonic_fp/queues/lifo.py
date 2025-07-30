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
### Last-In-Last-Out (LIFO) Queue

- stateful LIFO queue data structures with amortized O(1) pushes and pops
- obtaining length (number of elements) of a queue is an O(1) operation
- implemented in a "has-a" relationship with a Python list based circular array
- will resize itself larger as needed

"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Sequence
from typing import Never, TypeVar, overload

from pythonic_fp.circulararray import CA
from pythonic_fp.containers.maybe import MayBe as MB
from pythonic_fp.fptools.function import swap

__all__ = ['LIFOQueue', 'lifo_queue']

D = TypeVar('D')


class LIFOQueue[D]:
    """LIFO Queue.

    - stateful Last-In-First-Out (LIFO) data structure
    - initial data pushed on in natural LIFO order

    """

    __slots__ = ('_ca',)

    T = TypeVar('T')
    U = TypeVar('U')

    def __init__(self, *dss: Iterable[D]) -> None:
        if (size := len(dss)) < 2:
            self._ca = CA(dss[0]) if size == 1 else CA()
        else:
            msg = f'LIFOQueue expects at most 1 iterable argument, got {size}'
            raise TypeError(msg)

    def __bool__(self) -> bool:
        return len(self._ca) > 0

    def __len__(self) -> int:
        return len(self._ca)

    def __eq__(self, other: object, /) -> bool:
        if not isinstance(other, LIFOQueue):
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
        return reversed(list(self._ca))

    def __repr__(self) -> str:
        if len(self) == 0:
            return 'LQ()'
        return 'LQ(' + ', '.join(map(repr, self._ca)) + ')'

    def __str__(self) -> str:
        return '|| ' + ' > '.join(map(str, self)) + ' ><'

    def copy(self) -> LIFOQueue[D]:
        """Return a shallow copy of the ``LIFOQueue``."""
        return LIFOQueue(reversed(self._ca))

    def push(self, *ds: D) -> None:
        """Push data onto ``LIFOQueue``, does not return a value."""
        self._ca.pushr(*ds)

    def pop(self) -> MB[D]:
        """Pop data from ``LIFOQueue``.

        - pop item off of queue, return item in a maybe monad
        - returns an empty ``MB()`` if queue is empty

        """
        if self._ca:
            return MB(self._ca.popr())
        return MB()

    def peak(self) -> MB[D]:
        """Peak next data out of ``LIFOQueue``.

        - return a maybe monad of the next item to be popped from the queue
        - does not consume the item
        - returns ``MB()`` if queue is empty

        """
        if self._ca:
            return MB(self._ca[-1])
        return MB()

    def fold[T](self, f: Callable[[T, D], T], initial: T | None = None, /) -> MB[T]:
        """Reduce with ``f`` with an optional initial value.

        - folds in natural LIFO Order (newest to oldest)
        - note that when an initial value is not given then ``~T = ~D``
        - if iterable empty & no initial value given, return ``MB()``

        """
        if initial is None:
            if not self._ca:
                return MB()
        return MB(self._ca.foldr(swap(f), initial))

    def map[U](self, f: Callable[[D], U], /) -> LIFOQueue[U]:
        """Map Over the ``LIFOQueue``.

        - map the function ``f`` over the queue

          - newest to oldest
          - retain original order

        - returns a new instance

        """
        return LIFOQueue(reversed(CA(map(f, reversed(self._ca)))))


def lifo_queue[D](*ds: D) -> LIFOQueue[D]:
    """Create a LIFOQueue from the arguments."""
    return LIFOQueue(ds)
