# opti-extensions

[![license](https://img.shields.io/pypi/l/opti-extensions)](https://github.com/samarthmistry/opti-extensions/blob/main/LICENSE)
[![pypi](https://img.shields.io/pypi/v/opti-extensions)](https://pypi.python.org/pypi/opti-extensions)
[![pyversions](https://img.shields.io/pypi/pyversions/opti-extensions)](https://pypi.python.org/pypi/opti-extensions)

[![CI](https://github.com/samarthmistry/opti-extensions/actions/workflows/ci.yaml/badge.svg)](https://github.com/samarthmistry/opti-extensions/blob/main/.github/workflows/ci.yaml)
[![Tests](https://github.com/samarthmistry/opti-extensions/actions/workflows/tests.yaml/badge.svg)](https://github.com/samarthmistry/opti-extensions/blob/main/.github/workflows/tests.yaml)
[![Coverage](https://raw.githubusercontent.com/samarthmistry/opti-extensions/main/coverage.svg)](https://github.com/samarthmistry/opti-extensions/tree/main/tests/unit_tests)

A collection of custom data structures and user-friendly functions for mathematical optimization modeling with [DOcplex](https://ibmdecisionoptimization.github.io/docplex-doc), [gurobipy](https://docs.gurobi.com/projects/optimizer/en/current/reference/python.html), and [Xpress](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML).

Features
--------

* **Specialized data structures**: For defining index-sets, parameters, and decision variables enabling concise and high-performance algebraic modeling — compatible across different solver APIs.
* **Easy access to additional CPLEX functionality**: Like [tuning tool](https://www.ibm.com/docs/en/icos/latest?topic=programmingconsiderations-tuning-tool), [runseeds](https://www.ibm.com/docs/en/icos/latest?topic=cplex-evaluating-variability), [displaying problem statistics](https://www.ibm.com/docs/en/icos/latest?topic=problem-displaying-statistics), and [displaying solution quality statistics](https://www.ibm.com/docs/en/icos/latest?topic=cplex-evaluating-solution-quality) — not directly available in DOcplex.
* **Type-complete interface**: Enables static type checking and intelligent auto-completion suggestions with modern IDEs — reducing type errors and improving development speed.
* **Robust codebase**: 100% coverage spanning 2600+ test cases and fully type-checked with mypy under [strict mode](https://mypy.readthedocs.io/en/stable/getting_started.html#strict-mode-and-configuration).

Links
-----

* [Documentation](https://opti-extensions.readthedocs.io/en/stable)
* [Installation](https://opti-extensions.readthedocs.io/en/stable/installation/index.html)
* [Source code](https://github.com/samarthmistry/opti-extensions)
* [Changelog](https://github.com/samarthmistry/opti-extensions/releases)

Development
-----------

Dev dependencies can be installed with the pip [extras](https://packaging.python.org/en/latest/tutorials/installing-packages/#installing-extras) `dev`.

* Create HTML documentation locally with: `docs/make html`.
* Run unit tests and functional tests with: `pytest tests`.
* Run doctests with: `pytest src`.
* Run static typing tests with: `mypy tests/typing_tests`.

License
-------

*opti-extensions* is an open-source project developed by [Samarth Mistry](https://www.linkedin.com/in/samarthmistry) and released under the Apache 2.0 License. See the [LICENSE](https://github.com/samarthmistry/opti-extensions/blob/main/LICENSE) and [NOTICE](https://github.com/samarthmistry/opti-extensions/blob/main/NOTICE) for more details.
