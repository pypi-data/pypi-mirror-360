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

"""Pythonic FP - Lazy function evaluation

Delayed function evaluations. FP tools for "non-strict" function evaluations.
Useful to delay a function's evaluation until some inner scope.

Non-strict delayed function evaluation:

  - *class* Lazy: Delay evaluation of functions taking & returning single values
  - *function* lazy: Delay evaluation of functions taking any number of values
  - *function* real_lazy: Version of ``lazy`` which caches its result
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Final, Never, TypeVar, ParamSpec
from pythonic_fp.containers.maybe import MayBe as MB
from pythonic_fp.containers.xor import Xor, LEFT, RIGHT
from .function import sequenced

__all__ = ['Lazy', 'lazy', 'real_lazy']

D = TypeVar('D')
R = TypeVar('R', contravariant=True)
P = ParamSpec('P')


class Lazy[D, R]:
    """Delayed evaluation of a singled valued function.

    Class instance delays the executable of a function where ``Lazy(f, arg)``
    constructs an object that can evaluate the Callable ``f`` with its argument
    at a later time.

    - first argument ``f`` taking values of type ``~D`` to values of type ``~R``
    - second argument ``arg: ~D`` is the argument to be passed to ``f``

      - where the type ``~D`` is the ``tuple`` type of the argument types to ``f``

    - function is evaluated when the ``eval`` method is called
    - result is cached unless ``pure`` is set to ``False``
    - returns True in Boolean context if evaluated

    Usually use case is to make a function "non-strict" by passing some of its
    arguments wrapped in Lazy instances.
    """

    __slots__ = ('_f', '_d', '_result', '_pure', '_evaluated', '_exceptional')

    def __init__(self, f: Callable[[D], R], d: D, pure: bool = True) -> None:
        self._f: Final[Callable[[D], R]] = f
        self._d: Final[D] = d
        self._pure: bool = pure
        self._evaluated: bool = False
        self._exceptional: MB[bool] = MB()
        self._result: Xor[R, Exception]

    def __bool__(self) -> bool:
        return self._evaluated

    def eval(self) -> None:
        """Evaluate function with its argument.

        - evaluate function
        - cache result or exception if ``pure == True``
        - reevaluate if ``pure == False``
        """
        if not (self._pure and self._evaluated):
            try:
                result = self._f(self._d)
            except Exception as exc:
                self._result, self._evaluated, self._exceptional = (
                    Xor(exc, RIGHT),
                    True,
                    MB(True),
                )
            else:
                self._result, self._evaluated, self._exceptional = (
                    Xor(result, LEFT),
                    True,
                    MB(False),
                )

    def got_result(self) -> MB[bool]:
        """Return true if an evaluated Lazy did not raise an exception."""
        return self._exceptional.bind(lambda x: MB(not x))

    def got_exception(self) -> MB[bool]:
        """Return true if Lazy raised exception."""
        return self._exceptional

    def get(self, alt: R | None = None) -> R | Never:
        """Get result only if evaluated and no exceptions occurred, otherwise
        return an alternate value.

        A possible use case would be if the calculation is expensive, but if it
        has already been done, its result is better than the alternate value.
        """
        if self._evaluated and self._result:
            return self._result.get()
        if alt is not None:
            return alt
        msg = 'Lazy: method get needed an alternate value but none given.'
        raise ValueError(msg)

    def get_result(self) -> MB[R]:
        """Get result only if evaluated and not exceptional."""
        if self._evaluated and self._result:
            return self._result.get_left()
        return MB()

    def get_exception(self) -> MB[Exception]:
        """Get result only if evaluate and exceptional."""
        if self._evaluated and not self._result:
            return self._result.get_right()
        return MB()


def lazy[**P, R](
    f: Callable[P, R], *args: P.args, **kwargs: P.kwargs
) -> Lazy[tuple[Any, ...], R]:
    """Delayed evaluation of a function with arbitrary positional arguments.

    Function returning a delayed evaluation of a function of an arbitrary number
    of positional arguments.

    - first positional argument ``f`` takes a function
    - next positional arguments are the arguments to be applied later to ``f``

      - ``f`` is reevaluated whenever ``eval`` method of the returned ``Lazy`` is called

    - any kwargs passed are ignored

      - if ``f`` needs them, then wrap ``f`` in another function
    """
    return Lazy(sequenced(f), args, pure=False)


def real_lazy[**P, R](
    f: Callable[P, R], *args: P.args, **kwargs: P.kwargs
) -> Lazy[tuple[Any, ...], R]:
    """Cached delayed evaluation of a function with arbitrary positional arguments.

    Function returning a delayed evaluation of a function of an arbitrary number
    of positional arguments.

    - first positional argument ``f`` takes a function
    - next positional arguments are the arguments to be applied later to ``f``

      - ``f`` is evaluated when ``eval`` method of the returned ``Lazy`` is called
      - ``f`` is evaluated only once with results cached

    - any kwargs passed are ignored

      - if ``f`` needs them then wrap ``f`` in another function
    """
    return Lazy(sequenced(f), args)
