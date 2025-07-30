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


"""Class `Bool` - Subclassable Boolean

Python does not permit bool to be subclassed, but ``int`` can be subclassed.
Under-the-hood a ``bool`` is just an ``int``. The Bool class inherits from
``int`` and relies on the underlying truthiness and falsiness
of ``1`` and ``0``.

The ``Truth(truth: str)`` and ``Lie(lie: str)`` subclass constructors
produce singletons based on their input parameters. When using type hints,
declare variables of these types as type ``Bool``. Best practices when
used with these subclasses are:

- use `==` or `!=` for pure Boolean comparisons
- use `is` or `not is` if the type of truth matters
- only use Bool() as a type, never as a constructor
- when using Python shortcut logic remember

  - an instance of ``Truth`` is truthy
  - an instance of ``Lie`` is falsy
  - shortcut logic is lazy

    - the last truthy thing evaluated is returned
    - and is not converted to a ``bool``

  - the `not` statement converts a ``Bool`` to an actual ``bool``
"""

from __future__ import annotations

from typing import Final

__all__ = ['Bool', 'Truth', 'Lie', 'TRUTH', 'LIE' ]


class Bool(int):
    """Subclassable Boolean-like class."""

    __slots__ = ()

    def __new__(cls) -> Bool:
        return super(Bool, cls).__new__(cls, 0)

    def __repr__(self) -> str:
        if self:
            return 'Bool(1)'
        return 'Bool(0)'


class Truth(Bool):
    """Truthy singleton Bool subclass.

    :: note:
        When using type hints, declare variables Bool, not Truth.
    """

    _instances: dict[str, Truth] = dict()

    def __new__(cls, truth: str = 'TRUTH') -> Truth:
        if truth not in cls._instances:
            cls._instances[truth] = super(Bool, cls).__new__(cls, 1)
        return cls._instances[truth]

    def __init__(self, truth: str = 'TRUTH') -> None:
        self._truth = truth

    def __repr__(self) -> str:
        return f"Truth('{self._truth}')"


class Lie(Bool):
    """Falsy singleton Bool subclass.

    :: note:
        When using type hints, declare variables Bool, not Lie.
    """

    _instances: dict[str, Lie] = dict()

    def __new__(cls, lie: str = 'LIE') -> Lie:
        if lie not in cls._instances:
            cls._instances[lie] = super(Bool, cls).__new__(cls, 0)
        return cls._instances[lie]

    def __init__(self, lie: str = 'LIE') -> None:
        self._lie = lie

    def __repr__(self) -> str:
        return f"Lie('{self._lie}')"


TRUTH: Final[Truth] = Truth()
LIE: Final[Lie] = Lie()
