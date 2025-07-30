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

"""First-In-Last-Out (FIFO) Queue"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Sequence
from typing import Never, overload, TypeVar

from pythonic_fp.circulararray import CA
from pythonic_fp.containers.maybe import MayBe as MB


__all__ = ['FIFOQueue', 'fifo_queue']

D = TypeVar('D')


class FIFOQueue[D]:
    """FIFO Queue

    - stateful First-In-First-Out (FIFO) data structure
    - initial data pushed on in natural FIFO order
    """

    __slots__ = ('_ca',)

    T = TypeVar('T')
    U = TypeVar('U')

    def __init__(self, *dss: Iterable[D]) -> None:
        if (size := len(dss)) < 2:
            self._ca = CA(dss[0]) if size == 1 else CA()
        else:
            msg = f'FIFOQueue expects at most 1 iterable argument, got {size}'
            raise ValueError(msg)

    def __bool__(self) -> bool:
        return len(self._ca) > 0

    def __len__(self) -> int:
        return len(self._ca)

    def __eq__(self, other: object, /) -> bool:
        if not isinstance(other, FIFOQueue):
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

    def __repr__(self) -> str:
        if len(self) == 0:
            return 'FQ()'
        return 'FQ(' + ', '.join(map(repr, self._ca)) + ')'

    def __str__(self) -> str:
        return '<< ' + ' < '.join(map(str, self)) + ' <<'

    def copy(self) -> FIFOQueue[D]:
        """Return a shallow copy of the ``FIFOQueue``."""
        return FIFOQueue(self._ca)

    def push(self, *ds: D) -> None:
        """Push data onto ``FIFOQueue``, does not return a value."""
        self._ca.pushr(*ds)

    def pop(self) -> MB[D]:
        """Pop data from ``FIFOQueue``.

        - pop item off queue, return item in a maybe monad
        - returns an empty ``MB()`` if queue is empty
        """
        if self._ca:
            return MB(self._ca.popl())
        return MB()

    def peak_last_in(self) -> MB[D]:
        """Peak last data into ``FIFOQueue``.

        - return a maybe monad of the last item pushed to queue
        - does not consume the data
        - if item already popped, return ``MB()``
        """
        if self._ca:
            return MB(self._ca[-1])
        return MB()

    def peak_next_out(self) -> MB[D]:
        """Peak next data out of ``FIFOQueue``.

        - returns a maybe monad of the next item to be popped from the queue.
        - does not consume it the item
        - returns ``MB()`` if queue is empty
        """
        if self._ca:
            return MB(self._ca[0])
        return MB()

    def fold[T](self, f: Callable[[T, D], T], initial: T | None = None, /) -> MB[T]:
        """Reduce with ``f`` with an optional initial value.

        - folds in natural FIFO Order (oldest to newest)
        - note that when an initial value is not given then ``~L = ~D``
        - if iterable empty & no initial value given, return ``MB()``
        """
        if initial is None:
            if not self._ca:
                return MB()
        return MB(self._ca.foldl(f, initial))

    def map[U](self, f: Callable[[D], U], /) -> FIFOQueue[U]:
        """Map over the ``FIFOQueue``.

        - map function ``f`` over the queue

          - oldest to newest
          - retain original order

        - returns a new instance
        """
        return FIFOQueue(map(f, self._ca))


def fifo_queue[D](*ds: D) -> FIFOQueue[D]:
    """Create a FIFOQueue from the arguments."""
    return FIFOQueue(ds)
