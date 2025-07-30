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

"""Module fp.iterables - Iterator related tools

Library of iterator related functions and enumerations.

- Concatenating and merging iterables
- Dropping and taking values from iterables
- Reducing and accumulating iterables
- Assumptions

  - iterables are not necessarily iterators
  - at all times iterator protocol is assumed to be followed

    - all iterators are assumed to be iterable
    - for all iterators ``foo`` we assume ``iter(foo) is foo``
"""

from __future__ import annotations

__author__ = 'Geoffrey R. Scheller'
__copyright__ = 'Copyright (c) 2023-2025 Geoffrey R. Scheller'
__license__ = 'Apache License 2.0'

from collections.abc import Callable, Iterable, Iterator
from enum import auto, Enum
from typing import cast, Never, TypeVar
from pythonic_fp.containers.box import Box
from pythonic_fp.containers.maybe import MayBe as MB
from pythonic_fp.fptools.function import negate, swap
from pythonic_fp.fptools.singletons import NoValue

__all__ = [
    'FM',
    'concat',
    'merge',
    'exhaust',
    'drop',
    'drop_while',
    'take',
    'take_while',
    'take_split',
    'take_while_split',
    'accumulate',
    'foldl',
    'mb_fold_left',
    'reduce_left',
    'sc_reduce_left',
    'sc_reduce_right',
]

D = TypeVar('D')  # Needed only for pdoc documentation generation.
L = TypeVar('L')  # Otherwise, ignored by both MyPy and Python.

# Iterate over multiple iterables


class FM(Enum):
    """Types of iterable blending,

    - **CONCAT:** Concatenate first to last
    - **MERGE:** Merge until one is exhausted
    - **EXHAUST:** Merge until all are exhausted
    """

    CONCAT = auto()
    MERGE = auto()
    EXHAUST = auto()


def concat[D](*iterables: Iterable[D]) -> Iterator[D]:
    """Sequentially concatenate multiple iterables together.

    - pure Python version of standard library's ``itertools.chain``
    - iterator sequentially yields each iterable until all are exhausted
    - an infinite iterable will prevent subsequent iterables from yielding any values
    - performant to ``itertools.chain``
    """
    for iterator in map(lambda x: iter(x), iterables):
        while True:
            try:
                value = next(iterator)
                yield value
            except StopIteration:
                break


def exhaust[D](*iterables: Iterable[D]) -> Iterator[D]:
    """Shuffle together multiple iterables until all are exhausted.
    Iterator yields until all iterables are exhausted.
    """
    iter_list = list(map(lambda x: iter(x), iterables))
    if (num_iters := len(iter_list)) > 0:
        ii = 0
        values = []
        while True:
            try:
                while ii < num_iters:
                    values.append(next(iter_list[ii]))
                    ii += 1
                yield from values
                ii = 0
                values.clear()
            except StopIteration:
                num_iters -= 1
                if num_iters < 1:
                    break
                del iter_list[ii]

        yield from values


def merge[D](*iterables: Iterable[D], yield_partials: bool = False) -> Iterator[D]:
    """Shuffle together the ``iterables`` until one is exhausted.

    - iterator yields until one of the iterables is exhausted
    - if ``yield_partials`` is true,

      - yield any unmatched yielded values from other iterables
      - prevents data lose

        - if any of the iterables are iterators with external references
    """
    iter_list = list(map(lambda x: iter(x), iterables))
    values = []
    if (num_iters := len(iter_list)) > 0:
        while True:
            try:
                for ii in range(num_iters):
                    values.append(next(iter_list[ii]))
                yield from values
                values.clear()
            except StopIteration:
                break
        if yield_partials:
            yield from values


## dropping and taking


def drop[D](iterable: Iterable[D], n: int, /) -> Iterator[D]:
    """Drop the next ``n`` values from ``iterable``."""
    it = iter(iterable)
    for _ in range(n):
        try:
            next(it)
        except StopIteration:
            break
    return it


def drop_while[D](iterable: Iterable[D], pred: Callable[[D], bool], /) -> Iterator[D]:
    """Drop initial values from ``iterable`` while predicate is true."""
    it = iter(iterable)
    while True:
        try:
            value = next(it)
            if not pred(value):
                it = concat((value,), it)
                break
        except StopIteration:
            break
    return it


def take[D](iterable: Iterable[D], n: int, /) -> Iterator[D]:
    """Return an iterator of up to ``n`` initial values of an iterable"""
    it = iter(iterable)
    for _ in range(n):
        try:
            value = next(it)
            yield value
        except StopIteration:
            break


def take_split[D](iterable: Iterable[D], n: int, /) -> tuple[Iterator[D], Iterator[D]]:
    """Same as take except also return an iterator of the remaining values.

    - return a tuple of

      - an iterator of up to ``n`` initial values
      - an iterator of the remaining vales of the ``iterable``

    - Contract: do not access second iterator until first is exhausted
    """
    it = iter(iterable)
    itn = take(it, n)

    return itn, it


def take_while[D](iterable: Iterable[D], pred: Callable[[D], bool], /) -> Iterator[D]:
    """Yield values from ``iterable`` while predicate is true.

    .. warning::
        Risk of value loss if iterable is multiple referenced iterator.
    """
    it = iter(iterable)
    while True:
        try:
            value = next(it)
            if pred(value):
                yield value
            else:
                break
        except StopIteration:
            break


def take_while_split[D](
    iterable: Iterable[D], pred: Callable[[D], bool], /
) -> tuple[Iterator[D], Iterator[D]]:
    """Yield values from ``iterable`` while ``predicate`` is true.

    - return a tuple of two iterators

      - first of initial values where predicate is true, followed by first to fail
      - second of the remaining values of the iterable after first failed value

    - **Contract:** do not access second iterator until first is exhausted
    """

    def _take_while(
        it: Iterator[D], pred: Callable[[D], bool], val: Box[D]
    ) -> Iterator[D]:
        while True:
            try:
                val.put(next(it))
                if pred(val.get()):
                    yield val.pop()
                else:
                    break
            except StopIteration:
                break

    it = iter(iterable)
    value: Box[D] = Box()
    it_pred = _take_while(it, pred, value)

    return (it_pred, concat(value, it))


## reducing and accumulating


def accumulate[D, L](
    iterable: Iterable[D], f: Callable[[L, D], L], initial: L | NoValue = NoValue(), /
) -> Iterator[L]:
    """Returns an iterator of accumulated values.

    - pure Python version of standard library's ``itertools.accumulate``
    - function ``f`` does not default to addition (for typing flexibility)
    - begins accumulation with an optional ``initial`` value
    """
    it = iter(iterable)
    try:
        it0 = next(it)
    except StopIteration:
        if initial is NoValue():
            return
        yield cast(L, initial)
    else:
        if initial is not NoValue():
            init = cast(L, initial)
            yield init
            acc = f(init, it0)
            for ii in it:
                yield acc
                acc = f(acc, ii)
            yield acc
        else:
            acc = cast(L, it0)  # in this case L = D
            for ii in it:
                yield acc
                acc = f(acc, ii)
            yield acc


def reduce_left[D](iterable: Iterable[D], f: Callable[[D, D], D], /) -> D | Never:
    """Fold an iterable left with a function.

    - traditional FP type order given for function ``f``
    - if iterable empty, ``StopIteration`` exception raised
    - does not catch any exceptions ``f`` may raise
    - never returns if ``iterable`` generates an infinite iterator
    """
    it = iter(iterable)
    try:
        acc = next(it)
    except StopIteration as exc:
        msg = 'Attemped to reduce an empty iterable.'
        raise StopIteration(msg) from exc

    for v in it:
        acc = f(acc, v)

    return acc


def foldl[D, L](
    iterable: Iterable[D], f: Callable[[L, D], L], initial: L, /
) -> L | Never:
    """Folds an iterable left with a function and initial value.

    - traditional FP type order given for function ``f``
    - does not catch any exceptions ``f`` may raise
    - like builtin ``sum`` for Python >=3.8 except

      - not restricted to ``__add__`` for the folding function
      - initial value required, does not default to ``0`` for initial value
      - handles non-numeric data just find

    - never returns if ``iterable`` generates an infinite iterator
    """
    acc = initial
    for v in iterable:
        acc = f(acc, v)
    return acc


def mb_fold_left[L, D](
    iterable: Iterable[D], f: Callable[[L, D], L], initial: L | NoValue = NoValue()
) -> MB[L]:
    """Folds an iterable left with optional initial value.

    - traditional FP type order given for function ``f``
    - when an initial value is not given then ``~L = ~D``
    - if iterable empty and no ``initial`` value given, return ``MB()``
    - never returns if iterable generates an infinite iterator
    """
    acc: L
    it = iter(iterable)
    if initial is NoValue():
        try:
            acc = cast(L, next(it))  # in this case L = D
        except StopIteration:
            return MB()
    else:
        acc = cast(L, initial)

    for v in it:
        try:
            acc = f(acc, v)
        except Exception:
            return MB()

    return MB(acc)


def sc_reduce_left[D](
    iterable: Iterable[D],
    f: Callable[[D, D], D],
    /,
    start: Callable[[D], bool] = (lambda d: True),
    stop: Callable[[D], bool] = (lambda d: False),
    include_start: bool = True,
    include_stop: bool = True,
) -> tuple[MB[D], Iterator[D]]:
    """Short circuit version of a left reduce. Useful for infinite or iterables.

    - Behavior for default arguments will

      - left reduce finite iterable
      - start folding immediately
      - continue folding until end (of a possibly infinite iterable)

    - Callable ``start`` delays starting the left reduce
    - Callable ``stop`` prematurely stop the left reduce
    """
    it_start = drop_while(iterable, negate(start))
    if not include_start:
        try:
            next(it_start)
        except StopIteration:
            pass
    it_reduce, it_rest = take_while_split(it_start, negate(stop))
    mb_reduced = mb_fold_left(it_reduce, f)
    if include_stop:
        if mb_reduced:
            try:
                last = next(it_rest)
                mb_reduced = MB(f(mb_reduced.get(), last))
            except StopIteration:
                pass
        else:
            try:
                last = next(it_rest)
                mb_reduced = MB(last)
            except StopIteration:
                pass

    return (mb_reduced, it_rest)


def sc_reduce_right[D](
    iterable: Iterable[D],
    f: Callable[[D, D], D],
    /,
    start: Callable[[D], bool] = (lambda d: False),
    stop: Callable[[D], bool] = (lambda d: False),
    include_start: bool = True,
    include_stop: bool = True,
) -> tuple[MB[D], Iterator[D]]:
    """Short circuit version of a right reduce. Useful for infinite or
    non-reversible iterables.

    - Behavior for default arguments will

      - right reduce finite iterable
      - start reducing at end (of a possibly infinite iterable)
      - continue reducing right until beginning

    - Callable ``start`` prematurely starts the right reduce
    - Callable ``stop`` prematurely stops the right reduce
    """
    it_start, it_rest = take_while_split(iterable, negate(start))
    l1 = list(it_start)
    if include_start:
        try:
            begin = next(it_rest)
        except StopIteration:
            pass
        else:
            l1.append(begin)

    l1.reverse()
    it_reduce, it_stop = take_while_split(l1, negate(stop))

    mb_reduced = mb_fold_left(it_reduce, swap(f))
    if include_stop:
        try:
            end = next(it_stop)
        except StopIteration:
            pass
        else:
            if mb_reduced:
                mb_reduced = MB(f(end, mb_reduced.get()))
            else:
                mb_reduced = MB(end)

    return (mb_reduced, it_rest)
