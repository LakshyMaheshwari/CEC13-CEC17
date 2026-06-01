from typing import Optional
import numpy as np


def initialize_population(
    pop_size: int,
    D: int,
    lb: float,
    ub: float,
    rng: Optional[np.random.Generator] = None,
) -> np.ndarray:
    """Initialize population uniformly in [lb, ub]^D.

    Parameters
    ----------
    pop_size : int
        Number of candidate solutions (N).
    D : int
        Problem dimensionality.
    lb, ub : float
        Lower and upper bounds of the search space.
    rng : np.random.Generator, optional
        Random number generator for reproducibility.
        If None, a new default generator is created.

    Returns
    -------
    np.ndarray, shape (pop_size, D)
        Uniformly distributed initial population.
    """
    if rng is None:
        rng = np.random.default_rng()
    return rng.uniform(lb, ub, size=(pop_size, D))
