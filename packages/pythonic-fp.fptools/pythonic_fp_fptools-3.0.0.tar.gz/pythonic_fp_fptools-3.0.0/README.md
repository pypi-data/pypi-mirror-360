# Pythonic FP - Functional tools


PyPI project
[pythonic-fp.fptools](https://pypi.org/project/pythonic-fp.fptools/)
Functional programming tools which endeavor to be Pythonic.

- Subclassable Boolean datatype (*module* `pythonic_fp.fptools.bool`)
- Functions as first class objects (*module* `pythonic_fp.fptools.function`)
- Lazy (non-strict) function evaluation (*module* `pythonic_fp.fptools.lazy`)
- Singletons (*module* `pythonic_fp.fptools.singletons`)
  - 3 singleton classes representing
    - a missing value (actually missing, not potentially missing)
    - a sentinel values
    - a failed calculation
- State monad implementation (*module* `pythonic_fp.fptools.state`)
  - pure FP handling of state (the state monad)
  - Classic FP implementation
    - the monad encapsulates a state transformation, not a "state"

This PyPI project is part of of the grscheller
[pythonic-fp namespace projects](https://github.com/grscheller/pythonic-fp/blob/main/README.md).

**Warning:** The maintainer intends to break out the first, forth and
fifth modules to their own repos sometime in the near future.

## Documentation

Documentation hosted on
[GitHub Pages](https://grscheller.github.io/pythonic-fp-fptools/html).

## Copyright and License

Copyright (c) 2023-2025 Geoffrey R. Scheller. Licensed under the Apache
License, Version 2.0. See the LICENSE file for details.
