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

"""Pythonic FP namespace project - Circular Array data structure"""

from __future__ import annotations

__author__ = 'Geoffrey R. Scheller'
__copyright__ = 'Copyright (c) 2023-2025 Geoffrey R. Scheller'
__license__ = 'Apache License 2.0'

from collections.abc import Callable, Iterable, Iterator
from typing import cast, Never, overload

__all__ = ['CA', 'ca']

class CA[D]:
    """Indexable circular array data structure

    - O(1) pops either end 
    - O(1) amortized pushes either end 
    - O(1) indexing, fully supports slicing
    - Auto-resizing larger when necessary, manually compatible
    - Iterable, can safely mutate while iterators continue iterating over previous state
    - comparisons compare identity before equality, like builtins do
    - in boolean context returns

      - ``True`` when not empty
      - ``False`` when empty
    """

    __slots__ = '_data', '_cnt', '_cap', '_front', '_rear'

    def __init__(self, ds: Iterable[D] | None = None) -> None:
        """Initialize circular array with optional initial values.

        :param ds: Optional iterable to initial populate the circular array.
        :raises TypeError: if ds is not Iterable.
        """
        if ds is None:
            self._data: list[D | None] = [None, None]
        else:
            self._data = [None] + list(ds) + [None]
        self._cap = cap = len(self._data)
        self._cnt = cap - 2
        if cap == 2:
            self._front = 0
            self._rear = 1
        else:
            self._front = 1
            self._rear = cap - 2

    def _double_storage_capacity(self) -> None:
        if self._front <= self._rear:
            (
                    self._data,
                    self._cap,
            ) = (
                    self._data + [None] * self._cap,
                    self._cap * 2,
                )
        else:
            (
                    self._data,
                    self._front,
                    self._cap,
            ) = (
                    self._data[: self._front] + [None]*self._cap + self._data[self._front:],
                    self._front + self._cap,
                    2*self._cap,
                )

    def _compact_storage_capacity(self) -> None:
        match self._cnt:
            case 0:
                (
                        self._cap,
                        self._front,
                        self._rear,
                        self._data,
                ) = (
                        2,
                        0,
                        1,
                        [None, None],
                    )
            case 1:
                (
                        self._cap,
                        self._front,
                        self._rear,
                        self._data,
                ) = (
                        3,
                        1,
                        1,
                        [None, self._data[self._front], None],
                    )
            case _:
                if self._front <= self._rear:
                    ( 
                            self._cap,
                            self._front,
                            self._rear,
                            self._data,
                    ) = (
                            self._cnt + 2,
                            1,
                            self._cnt,
                            [None] + self._data[self._front : self._rear + 1] + [None],
                        )
                else:
                    (
                            self._cap,
                            self._front,
                            self._rear,
                            self._data,
                    ) = (
                            self._cnt + 2,
                            1,
                            self._cnt,
                            [None] + self._data[self._front :] + self._data[: self._rear + 1] + [None],
                        )

    def __iter__(self) -> Iterator[D]:
        if self._cnt > 0:
            (
                    capacity,
                    rear,
                    position,
                    current_state,
            ) = (
                    self._cap,
                    self._rear,
                    self._front,
                    self._data.copy(),
                )

            while position != rear:
                yield cast(D, current_state[position])
                position = (position + 1) % capacity
            yield cast(D, current_state[position])

    def __reversed__(self) -> Iterator[D]:
        if self._cnt > 0:
            (
                    capacity,
                    front,
                    position,
                    current_state,
            ) = (
                    self._cap,
                    self._front,
                    self._rear,
                    self._data.copy(),
                )

            while position != front:
                yield cast(D, current_state[position])
                position = (position - 1) % capacity
            yield cast(D, current_state[position])

    def __repr__(self) -> str:
        return 'ca(' + ', '.join(map(repr, self)) + ')'

    def __str__(self) -> str:
        return '(|' + ', '.join(map(str, self)) + '|)'

    def __bool__(self) -> bool:
        return self._cnt > 0

    def __len__(self) -> int:
        return self._cnt

    @overload
    def __getitem__(self, idx: int, /) -> D: ...
    @overload
    def __getitem__(self, idx: slice, /) -> CA[D]: ...

    def __getitem__(self, idx: int | slice, /) -> D | CA[D]:
        if isinstance(idx, slice):
            return CA(list(self)[idx])

        cnt = self._cnt
        if 0 <= idx < cnt:
            return cast(D, self._data[(self._front + idx) % self._cap])

        if -cnt <= idx < 0:
            return cast(D, self._data[(self._front + cnt + idx) % self._cap])

        if cnt == 0:
            msg0 = 'Trying to get a value from an empty CA.'
            raise IndexError(msg0)

        msg1 = 'Out of bounds: '
        msg2 = f'index = {idx} not between {-cnt} and {cnt - 1} '
        msg3 = 'while getting value from a CA.'
        raise IndexError(msg1 + msg2 + msg3)

    @overload
    def __setitem__(self, idx: int, vals: D, /) -> None: ...
    @overload
    def __setitem__(self, idx: slice, vals: Iterable[D], /) -> None: ...

    def __setitem__(self, idx: int | slice, vals: D | Iterable[D], /) -> None:
        if isinstance(idx, slice):
            if isinstance(vals, Iterable):
                data = list(self)
                data[idx] = vals
                _ca = CA(data)
                (
                        self._data,
                        self._cnt,
                        self._cap,
                        self._front,
                        self._rear,
                ) = (
                        _ca._data,
                        _ca._cnt,
                        _ca._cap,
                        _ca._front,
                        _ca._rear,
                    )
                return

            msg = 'must assign iterable to extended slice'
            raise TypeError(msg)

        cnt = self._cnt
        if 0 <= idx < cnt:
            self._data[(self._front + idx) % self._cap] = cast(D, vals)
        elif -cnt <= idx < 0:
            self._data[(self._front + cnt + idx) % self._cap] = cast(D, vals)
        else:
            if cnt < 1:
                msg0 = 'Trying to index into an empty CA.'
                raise IndexError(msg0)
            msg1 = 'Out of bounds: '
            msg2 = f'index = {idx} not between {-cnt} and {cnt - 1} '
            msg3 = 'while setting value from a CA.'
            raise IndexError(msg1 + msg2 + msg3)

    @overload
    def __delitem__(self, idx: int, /) -> None: ...
    @overload
    def __delitem__(self, idx: slice, /) -> None: ...

    def __delitem__(self, idx: int | slice, /) -> None:
        data = list(self)
        del data[idx]
        _ca = CA(data)
        (
                self._data,
                self._cnt,
                self._cap,
                self._front,
                self._rear,
        ) = (
                _ca._data,
                _ca._cnt,
                _ca._cap,
                _ca._front,
                _ca._rear,
            )

    def __eq__(self, other: object, /) -> bool:
        if self is other:
            return True
        if not isinstance(other, type(self)):
            return False

        (
                front1,
                count1,
                capacity1,
                front2,
                count2,
                capacity2,
        ) = (
                self._front,
                self._cnt,
                self._cap,
                other._front,
                other._cnt,
                other._cap,
            )

        if count1 != count2:
            return False

        for nn in range(count1):
            if self._data[(front1 + nn) % capacity1] is other._data[(front2 + nn) % capacity2]:
                continue
            if self._data[(front1 + nn) % capacity1] != other._data[(front2 + nn) % capacity2]:
                return False
        return True

    def pushl(self, *ds: D) -> None:
        """Push left.

        :param ds: data pushed from left onto circular array

        """
        for d in ds:
            if self._cnt == self._cap:
                self._double_storage_capacity()
            (
                    self._front,
                    self._data[self._front],
                    self._cnt,
            ) = (
                    (self._front - 1) % self._cap,
                    d,
                    self._cnt + 1,
                )

    def pushr(self, *ds: D) -> None:
        """Push right.

        :param ds: data pushed from right onto circular array

        """
        for d in ds:
            if self._cnt == self._cap:
                self._double_storage_capacity()
            (
                    self._rear,
                    self._data[self._rear],
                    self._cnt,
            ) = (
                    (self._rear + 1) % self._cap,
                    d,
                    self._cnt + 1,
                )

    def popl(self) -> D | Never:
        """Pop left.

        :return: value popped from left side of circular array
        :raises ValueError: when called on an empty circular array

        """
        if self._cnt > 1:
            (
                    d,
                    self._data[self._front],
                    self._front,
                    self._cnt,
            ) = (
                    self._data[self._front],
                    None,
                    (self._front + 1) % self._cap,
                    self._cnt - 1,
                )
        elif self._cnt == 1:
            (
                    d,
                    self._data[self._front],
                    self._cnt,
                    self._front,
                    self._rear,
            ) = (
                    self._data[self._front],
                    None,
                    0,
                    0,
                    self._cap - 1,
                )
        else:
            msg = 'Method popl called on an empty CA'
            raise ValueError(msg)
        return cast(D, d)

    def popr(self) -> D | Never:
        """Pop right.

        :return: value popped from right side of circular array
        :raises ValueError: when called on an empty circular array

        """
        if self._cnt > 1:
            (
                    d,
                    self._data[self._rear],
                    self._rear,
                    self._cnt,
            ) = (
                    self._data[self._rear],
                    None,
                    (self._rear - 1) % self._cap,
                    self._cnt - 1,
                )
        elif self._cnt == 1:
            (
                    d,
                    self._data[self._front],
                    self._cnt,
                    self._front,
                    self._rear,
            ) = (
                    self._data[self._front],
                    None,
                    0,
                    0,
                    self._cap - 1,
                )
        else:
            msg = 'Method popr called on an empty CA'
            raise ValueError(msg)
        return cast(D, d)

    def popld(self, default: D, /) -> D:
        """Pop one value from left side of the circular array, provide a
        mandatory default value. "Safe" version of popl.

        :param default: value returned if circular array is empty
        :return: value popped from left side

        """
        try:
            return self.popl()
        except ValueError:
            return default

    def poprd(self, default: D, /) -> D:
        """Pop one value from right side of the circular array, provide a
        mandatory default value. "Safe" version of ``popr``.

        :param default: value returned if circular array is empty
        :return: value popped from right side

        """
        try:
            return self.popr()
        except ValueError:
            return default

    def poplt(self, maximum: int, /) -> tuple[D, ...]:
        """Pop multiple values from left side of the circular array.

        :param maximum: pop no more than ``maximum`` values
        :return: tuple of values popped from left side
        """
        ds: list[D] = []

        while maximum > 0:
            try:
                ds.append(self.popl())
            except ValueError:
                break
            else:
                maximum -= 1

        return tuple(ds)

    def poprt(self, maximum: int, /) -> tuple[D, ...]:
        """Pop multiple values from right side of the circular array.

        :param maximum: pop no more than ``maximum`` values
        :return: tuple of values popped from right side
        """
        ds: list[D] = []
        while maximum > 0:
            try:
                ds.append(self.popr())
            except ValueError:
                break
            else:
                maximum -= 1
        return tuple(ds)

    def rotl(self, n: int = 1, /) -> None:
        """Rotate circular array elements left.

        :param n: number of times to shift elements to the left
        """
        if self._cnt < 2:
            return
        for _ in range(n, 0, -1):
            self.pushr(self.popl())

    def rotr(self, n: int = 1, /) -> None:
        """Rotate circular array elements right.

        :param n: number of times to shift elements to the right
        """
        if self._cnt < 2:
            return
        for _ in range(n, 0, -1):
            self.pushl(self.popr())

    def map[U](self, f: Callable[[D], U], /) -> CA[U]:
        """Apply function ``f`` over the circular array's contents,

        :param f: function from type D to type U
        :return: new circular array instance.

        """
        return CA(map(f, self))

    def foldl[L](self, f: Callable[[L, D], L], initial: L | None = None, /) -> L:
        """Left fold with a function and optional initial value.

        :param f: first argument to ``f`` is for the accumulated value
        :param initial: optional initial value
        :raises ValueError: when circular array empty and no initial value given
        """
        if self._cnt == 0:
            if initial is None:
                msg = 'Method foldl called on an empty CA without an initial value.'
                raise ValueError(msg)
            return initial

        if initial is None:
            acc = cast(L, self[0])  # in this case D = L
            for idx in range(1, self._cnt):
                acc = f(acc, self[idx])
            return acc

        acc = initial
        for d in self:
            acc = f(acc, d)
        return acc

    def foldr[R](self, f: Callable[[D, R], R], initial: R | None = None, /) -> R:
        """Right fold with a function and an optional initial value.

        :param f: second argument to `f` is for the accumulated value
        :param initial: optional initial value
        :raises ValueError: when circular array empty and no initial value given
        """
        if self._cnt == 0:
            if initial is None:
                msg = 'Method foldr called on empty CA without initial value.'
                raise ValueError(msg)
            return initial

        if initial is None:
            acc = cast(R, self[-1])  # in this case D = R
            for idx in range(self._cnt - 2, -1, -1):
                acc = f(self[idx], acc)
            return acc

        acc = initial
        for d in reversed(self):
            acc = f(d, acc)
        return acc

    def capacity(self) -> int:
        """Find current storage capacity of the circular array.

        :return: current capacity of the circular array
        """
        return self._cap

    def empty(self) -> None:
        """Empty the circular array, keep current capacity."""
        (
                self._data,
                self._front,
                self._rear,
        ) = (
                [None] * self._cap,
                0,
                self._cap,
            )

    def fraction_filled(self) -> float:
        """Find fraction of capacity filled.

        :return: the ratio cnt/capacity
        """
        return self._cnt / self._cap

    def resize(self, minimum_capacity: int = 2) -> None:
        """Compact circular array and resize to a minimum capacity if necessary.
        To just compact the circular array, do not provide a minimum capacity.

        :param minimum_capacity: minimum value to compact the circular array

        """
        self._compact_storage_capacity()
        if (min_cap := minimum_capacity) > self._cap:
            (
                    self._cap,
                    self._data,
            ) = (
                    min_cap,
                    self._data + [None] * (min_cap - self._cap),
                )
            if self._cnt == 0:
                self._front, self._rear = 0, self._cap - 1


def ca[D](*ds: D) -> CA[D]:
    """Function to produce a circular array from a variable number of arguments.

    :param ds: initial values to push onto a new circular array from right to left
    """
    return CA(ds)
