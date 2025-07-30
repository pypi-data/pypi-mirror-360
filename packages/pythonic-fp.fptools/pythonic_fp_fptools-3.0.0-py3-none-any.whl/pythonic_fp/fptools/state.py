# Copyright 2024-2025 Geoffrey R. Scheller
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

"""Pythonic FP - State Monad

Handling state functionally.

##### *class* State - Classic FP State Monad

A pure FP immutable implementation for the State Monad.

- translated to Python from the book "Functional Programming in Scala"

  - authors Chiusana & Bjarnason
  - run "action" returns a tuple ``(a, s)`` reversed to the type ``State[S, A]``

    - the standard convention seen in the FP community
    - another "factoid" to remember

- choose the name ``bind`` instead of ``flatmap``

  - the ``flatmap`` name is misleading for non-container-like monads
  - ``flatmap`` name too long, ``bind`` shorter to type

    - without "do-notation", code tends to march to the right

- typing for the ``modify`` class method may be a bit suspect

"""

from __future__ import annotations

__all__ = ['State']

from collections.abc import Callable
from typing import TypeVar
from pythonic_fp.circulararray import CA

S = TypeVar('S')
A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')
ST = TypeVar('ST')
AA = TypeVar('AA')


class State[S, A]:
    """Data structure generating values while propagating changes of state.

    - class ``State`` represents neither a state nor (value, state) pair

      - it wraps a transformation old_state -> (value, new_state)
      - the ``run`` method is this wrapped transformation
      - ``bind`` is just state propagating function composition

    """

    __slots__ = ('run',)

    def __init__(self, run: Callable[[S], tuple[A, S]]) -> None:
        self.run = run

    def bind[B](self, g: Callable[[A], State[S, B]]) -> State[S, B]:
        """Perform function composition while propagating state."""

        def compose(s: S) -> tuple[B, S]:
            a, s = self.run(s)
            return g(a).run(s)

        return State(compose)

    def eval(self, init: S) -> A:
        """Evaluate the Monad via passing an initial state."""
        a, _ = self.run(init)
        return a

    def map[B](self, f: Callable[[A], B]) -> State[S, B]:
        """Map a function over a run action."""
        return self.bind(lambda a: State.unit(f(a)))

    def map2[B, C](self, sb: State[S, B], f: Callable[[A, B], C]) -> State[S, C]:
        """Map a function of two variables over two state actions."""
        return self.bind(lambda a: sb.map(lambda b: f(a, b)))

    def both[B](self, rb: State[S, B]) -> State[S, tuple[A, B]]:
        """Return a tuple of two state actions."""
        return self.map2(rb, lambda a, b: (a, b))

    @staticmethod
    def unit[ST, B](b: B) -> State[ST, B]:
        """Create a State action returning the given value."""
        return State(lambda s: (b, s))

    @staticmethod
    def get[ST]() -> State[ST, ST]:
        """Set run action to return the current state

        - the current state is propagated unchanged
        - current value now set to current state
        - will need type annotation

        """
        return State[ST, ST](lambda s: (s, s))

    @staticmethod
    def put[ST](s: ST) -> State[ST, tuple[()]]:
        """Manually insert a state.

        THe run action.

        - ignores previous state and swaps in a new state
        - assigns a canonically meaningless value to current value
        """
        return State(lambda _: ((), s))

    @staticmethod
    def modify[ST](f: Callable[[ST], ST]) -> State[ST, tuple[()]]:
        """Modify previous state.

        - like put, but modify previous state via ``f``
        - will need type annotation

          - mypy has no "a priori" way to know what ST is
        """
        return State.get().bind(lambda a: State.put(f(a)))  # type: ignore

    @staticmethod
    def sequence[ST, AA](sas: list[State[ST, AA]]) -> State[ST, list[AA]]:
        """Combine a list of state actions into a state action of a list.

        - all state actions must be of the same type
        - run method evaluates list front to back
        """

        def append_ret(ls: list[AA], a: AA) -> list[AA]:
            ls.append(a)
            return ls

        return CA(sas).foldl(
            lambda s1, sa: s1.map2(sa, append_ret),
            State.unit(list[AA]([]))
        )
