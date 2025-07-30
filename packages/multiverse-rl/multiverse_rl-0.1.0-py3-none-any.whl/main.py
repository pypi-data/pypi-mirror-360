from __future__ import annotations

"""A minimal, pure‑NumPy implementation of the MAP‑Elites algorithm.

The code is intentionally generic: you only need to supply a function that maps a
`genome -> (fitness, descriptor_vector)` and specify how the behaviour space
(descriptor space) is discretised.  The algorithm will then maintain an archive
(elite map) containing the best‑fitness individual discovered for every niche.

Example
-------
>>> import numpy as np
>>> from map_elites import MAPElites, Solution
>>>
>>> # Toy landscape: fitness = -||x||^2  (we want to minimise distance to 0)
>>> def evaluate(genome: np.ndarray) -> tuple[float, np.ndarray]:
...     fitness = -np.sum(genome ** 2)
...     # behaviour descriptors are the first two coordinates
...     desc = genome[:2]
...     return fitness, desc
>>>
>>> map_elites = MAPElites(
...     genome_length=5,
...     behaviour_bounds=np.array([[-1.0, 1.0],   # x‑axis range
...                                [-1.0, 1.0]]), # y‑axis range
...     bins_per_dim=np.array([10, 10]),          # 10×10 grid
...     evaluate_fn=evaluate,
...     mutation_sigma=0.1,
... )
>>> archive = map_elites.run(num_iterations=2_000, initial_population=100)
>>> print(f"Filled niches: {len([s for s in archive if s is not None])}/100")
"""

from dataclasses import dataclass
from typing import Callable, Sequence, Optional
import numpy as np


@dataclass
class Solution:
    """A generic solution candidate.

    Attributes
    ----------
    genome
        1‑D NumPy array encoding the solution.
    fitness
        The objective value (larger is better).
    descriptors
        Behaviour‑space coordinates produced by the domain‑specific evaluation
        function.
    """

    genome: np.ndarray
    fitness: float
    descriptors: np.ndarray


class MAPElites:
    """Minimal MAP‑Elites implementation (illumination algorithm).

    Parameters
    ----------
    genome_length
        Length of the solution genome vector.
    behaviour_bounds
        Array of shape (B, 2) giving min & max for each of the ``B`` behaviour
        dimensions (descriptors).
    bins_per_dim
        Number of discrete niches along each behaviour dimension (shape: (B,)).
    evaluate_fn
        Callable ``genome -> (fitness, descriptors)`` provided by the user.
    mutation_sigma
        Standard deviation of the Gaussian noise added in mutation.
    rng
        NumPy random Generator (optional).  A fresh default_rng() is used if
        unspecified.
    """

    def __init__(
        self,
        *,
        genome_length: int,
        behaviour_bounds: np.ndarray,
        bins_per_dim: np.ndarray,
        evaluate_fn: Callable[[np.ndarray], tuple[float, np.ndarray]],
        mutation_sigma: float = 0.05,
        rng: Optional[np.random.Generator] = None,
    ) -> None:
        self.genome_length = genome_length
        self.behaviour_bounds = np.asarray(behaviour_bounds, dtype=float)
        self.bins_per_dim = np.asarray(bins_per_dim, dtype=int)
        if self.behaviour_bounds.shape[0] != self.bins_per_dim.shape[0]:
            raise ValueError("bounds and bins_per_dim must have same length")

        self.evaluate_fn = evaluate_fn
        self.mutation_sigma = mutation_sigma
        self.rng = rng or np.random.default_rng()

        # Archive: an n‑dimensional grid (tuple index) of Solution or None.
        self.archive: np.ndarray = np.empty(tuple(self.bins_per_dim), dtype=object)
        self.archive.fill(None)

        # Pre‑compute width of each bin along every axis.
        self.bin_width = (
            self.behaviour_bounds[:, 1] - self.behaviour_bounds[:, 0]
        ) / self.bins_per_dim

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def run(
        self,
        *,
        num_iterations: int,
        initial_population: int = 100,
    ) -> np.ndarray:
        """Run MAP‑Elites and return the filled archive."""
        self._initialise_archive(initial_population)
        for _ in range(num_iterations):
            parent = self._sample_elite()
            if parent is None:
                continue  # archive empty; shouldn't happen after init
            child_genome = self._mutate(parent.genome)
            fitness, desc = self.evaluate_fn(child_genome)
            self._add_to_archive(Solution(child_genome, fitness, desc))
        return self.archive

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _initialise_archive(self, n: int) -> None:
        """Seed the archive with ``n`` random genomes drawn U[-1,1]."""
        genomes = self.rng.uniform(-1.0, 1.0, size=(n, self.genome_length))
        for g in genomes:
            fitness, desc = self.evaluate_fn(g)
            self._add_to_archive(Solution(g, fitness, desc))

    def _mutate(self, genome: np.ndarray) -> np.ndarray:
        """Gaussian mutation with fixed sigma (mirrored at ±1)."""
        child = genome + self.rng.normal(0.0, self.mutation_sigma, size=genome.shape)
        return np.clip(child, -1.0, 1.0)

    def _sample_elite(self) -> Optional[Solution]:
        """Uniformly pick a random filled cell and return its Solution."""
        filled_indices = np.argwhere(self.archive != None)  # noqa: E711
        if filled_indices.size == 0:
            return None
        idx = self.rng.choice(len(filled_indices))
        return self.archive[tuple(filled_indices[idx])]

    # ------------------------------------------------------------------
    # Archive bookkeeping
    # ------------------------------------------------------------------
    def _add_to_archive(self, sol: Solution) -> None:
        idx = self._descriptor_to_index(sol.descriptors)
        if idx is None:
            return  # out‑of‑bounds descriptor → discard (could also rescale)
        current: Optional[Solution] = self.archive[idx]
        if (current is None) or (sol.fitness > current.fitness):
            self.archive[idx] = sol

    def _descriptor_to_index(self, desc: Sequence[float]) -> Optional[tuple]:
        desc = np.asarray(desc, dtype=float)
        # Check bounds
        if np.any(desc < self.behaviour_bounds[:, 0]) or np.any(
            desc > self.behaviour_bounds[:, 1]
        ):
            return None  # out of behaviour space
        # Compute bin indices along each dimension
        rel_pos = (desc - self.behaviour_bounds[:, 0]) / self.bin_width
        idx = np.floor(rel_pos).astype(int)
        # Edge case: descriptors exactly at the max bound
        idx = np.minimum(idx, self.bins_per_dim - 1)
        return tuple(idx)


# ---------------------------------------------------------------------------
# Simple demo when run as a script
# ---------------------------------------------------------------------------
if __name__ == "__main__":

    def sphere(genome: np.ndarray) -> tuple[float, np.ndarray]:
        """Sphere function (maximisation) with 2‑D descriptors."""
        fitness = -np.sum(genome**2)
        return fitness, genome[:2]

    algo = MAPElites(
        genome_length=5,
        behaviour_bounds=np.array([[-1.0, 1.0], [-1.0, 1.0]]),
        bins_per_dim=np.array([20, 20]),
        evaluate_fn=sphere,
        mutation_sigma=0.1,
    )
    archive = algo.run(num_iterations=5_000, initial_population=200)
    filled = np.count_nonzero(archive != None)  # noqa: E711
    print(f"Filled niches: {filled}/{archive.size}")
