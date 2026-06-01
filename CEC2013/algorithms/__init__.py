"""
Optimization algorithms for CEC benchmark evaluation.

Implements Rao-1, Rao-2, Rao-3 (Rao, 2020) and FISA.

References
----------
R.V. Rao, "Rao-1, Rao-2 and Rao-3: Three metaphor-less simple
algorithms for solving optimization problems," Int. J. Ind. Eng.
Comput., vol. 11, no. 1, pp. 107-130, 2020.
"""

from .rao1 import rao1
from .rao2 import rao2
from .rao3 import rao3
from .fisa import fisa

ALGORITHMS = {"rao1": rao1, "rao2": rao2, "rao3": rao3, "fisa": fisa}

__all__ = ["rao1", "rao2", "rao3", "fisa", "ALGORITHMS"]
