"""
Rao-2 optimization algorithm.

Reference
---------
R.V. Rao, "Rao-1, Rao-2 and Rao-3: Three metaphor-less simple
algorithms for solving optimization problems," Int. J. Ind. Eng.
Comput., vol. 11, no. 1, pp. 107-130, 2020.

Update rule (Eq. 3):
    x'(j,i,k) = x(j,i) + r1,j*(x(j,best) - x(j,worst))
                        + r2,j*(x(j,i) - x(j,k))    if f(i) < f(k)
                        + r2,j*(x(j,k) - x(j,i))    if f(i) >= f(k)

    where k != i is a randomly selected candidate.
"""

from typing import Tuple, List, Optional
import numpy as np

from ..utils.population import initialize_population
from ..utils.bounds import apply_bounds
from ..functions.core import evaluate, get_fes


def rao2(
    pop_size: int,
    D: int,
    lb: float,
    ub: float,
    max_fes: int,
    func_id: int,
    early_stop_value: float = None,
    rng: Optional[np.random.Generator] = None,
) -> Tuple[np.ndarray, List[Tuple[int, float]]]:
    """Rao-2: best-worst perturbation + partner interaction (Eq. 3 in Rao, 2020).

    Extends Rao-1 with a second term that biases the search direction based
    on fitness comparison with a randomly selected partner solution.
    Termination is governed by the FES budget. Fitness values are cached
    to maintain a 1:1 FES-to-evaluation ratio.

    Parameters
    ----------
    pop_size : int
        Population size (N).
    D : int
        Problem dimensionality.
    lb, ub : float
        Search space bounds.
    max_fes : int
        Maximum number of function evaluations.
    func_id : int
        CEC2013 function ID (1-28).
    early_stop_value : float, optional
        Terminate early if fitness reaches this value (within 1e-8).
    rng : np.random.Generator, optional
        Random number generator for reproducibility.
        If None, a new default generator is created.

    Returns
    -------
    best_x : np.ndarray, shape (D,)
        Best solution found.
    history : list of (int, float)
        Convergence history as (FES_count, best_fitness) pairs.
    """
    if rng is None:
        rng = np.random.default_rng()

    population = initialize_population(pop_size, D, lb, ub, rng=rng)

    # Evaluate initial population (consumes pop_size FES)
    fitness = np.array([evaluate(population[i], func_id)[0]
                        for i in range(pop_size)])

    best_f = np.min(fitness)
    best_x = population[np.argmin(fitness)].copy()
    history = [(get_fes(), best_f)]

    # ── Raw population data capture ──
    iteration_data = []
    generation = 0
    iteration_data.append({
        'iteration': generation,
        'fes': get_fes(),
        'population': np.copy(population),
        'fitness': np.copy(fitness),
    })

    # Main loop
    while get_fes() < max_fes:

        # Early termination if optimum reached
        if early_stop_value is not None and best_f <= early_stop_value + 1e-8:
            break

        # Identify best and worst in current population
        idx_best = int(np.argmin(fitness))
        idx_worst = int(np.argmax(fitness))
        x_best = population[idx_best]
        x_worst = population[idx_worst]

        for i in range(pop_size):

            # Check FES budget
            if get_fes() >= max_fes:
                break

            # Select random partner k != i
            k = rng.integers(0, pop_size)
            while k == i:
                k = rng.integers(0, pop_size)
            x_k = population[k]

            r1 = rng.random(D)
            r2 = rng.random(D)

            # Interaction term (Eq. 3): sign depends on relative fitness.
            # If x_i is better (lower f) than x_k, move away from x_k;
            # otherwise, move toward x_k.
            if fitness[i] < fitness[k]:
                interaction = r2 * (population[i] - x_k)
            else:
                interaction = r2 * (x_k - population[i])

            # Trial vector (Eq. 3)
            x_new = population[i] + r1 * (x_best - x_worst) + interaction

            # Repair bounds
            x_new = apply_bounds(x_new, lb, ub)

            # Evaluate and apply greedy selection
            f_new, _ = evaluate(x_new, func_id)
            if f_new <= fitness[i]:
                population[i] = x_new
                fitness[i] = f_new

            # Update global best
            if fitness[i] < best_f:
                best_f = fitness[i]
                best_x = population[i].copy()
                history.append((get_fes(), best_f))

        # ── Snapshot population after this generation ──
        generation += 1
        iteration_data.append({
            'iteration': generation,
            'fes': get_fes(),
            'population': np.copy(population),
            'fitness': np.copy(fitness),
        })

    return best_x, history, iteration_data
