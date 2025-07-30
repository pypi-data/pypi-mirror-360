"""
Order Sampling
"""

from typing import Callable

import numpy as np
import numpy.typing as npt

from pysps.inclusion_prob import InclusionProb


def _igpd(shape: float) -> Callable[[npt.ArrayLike], np.ndarray]:
    """
    Inverse of the generalized Pareto distribution.
    """
    if shape == 0.0:
        return lambda x: -np.log(1 - x)
    elif shape == 1.0:
        return lambda x: x
    else:
        return lambda x: (1 - (1 - x) ** shape) / shape


def _generate_random_deviates(
    prn: npt.ArrayLike | None, pi: InclusionProb
) -> np.ndarray:
    """
    Generate a vector of random numbers for drawing a sample.
    """
    if prn is None:
        u = np.random.default_rng().uniform(size=len(pi))
    else:
        u = np.asarray(prn, dtype=np.float64).ravel()
        if len(u) != len(pi):
            raise ValueError("pi and prn must be the same length")
        if np.any(u <= 0.0) or np.any(u >= 1.0):
            raise ValueError("all elements of prn must be in (0, 1)")
        if not np.all(np.isfinite(prn)):
            raise ValueError("all elements of prn must be finite")
    return u


class BaseSample:
    """
    Interface for sample classes. Should not be used directly.
    """

    @property
    def units(self) -> np.ndarray:
        """
        Indices for units in the sample.
        """
        return self._units.copy()

    @property
    def weights(self) -> np.ndarray:
        """
        Design weights for units in the sample.
        """
        return 1 / self._pi._values[self._units]

    @property
    def take_all(self) -> np.ndarray:
        """
        Take all units in the sample.
        """
        return self._ta.copy()

    @property
    def take_some(self) -> np.ndarray:
        """
        Take some units in the sample.
        """
        return self._ts.copy()

    @property
    def prn(self) -> np.ndarray:
        """
        Random numbers used for drawing the sample.
        """
        return self._prn.copy()

    def __len__(self) -> int:
        return len(self._units)

    def __str__(self) -> str:
        return str(self._units)


class OrderSample(BaseSample):
    """
    Order sampling scheme with fixed distribution shape.

    Parameters
    ----------
    pi : InclusionProb
        Inclusion probabilities for units in the population.
    prn : ArrayLike, optional
        Permanent random numbers. Should be a flat array of values, the
        same length as `pi`, distributed uniform between 0 and 1. The
        default draws a sample without permanent random numbers.
    shape : float, optional
        Shape parameter for the generalized Pareto distribution that is
        used as the fixed order distribution shape.

        shape=1  => Sequential Poisson sampling (the default)
        shape=0  => Successive sampling
        shape=-1 => Pareto order sampling
    sort_method : {'partial', 'stable'}, optional
        Sorting method to use for drawing the sample. The default
        uses a partial sort. Use 'stable' if ties should resolve in
        order.

    Attributes
    ----------
    units : Array
        Indices for units in the sample.
    weights : Array
        Design weights for units in the sample.
    take_all : Array
        Take-all units in the sample.
    take_some : Array
        Take-some units in the sample.
    prn : Array
        Random numbers used for drawing the sample.

    References
    ----------
    Matei, A., and Tillé, Y. (2007). Computational aspects of order πps
        sampling schemes. _Computational Statistics & Data Analysis_, 51:
        3703-3717.

    Ohlsson, E. (1998). Sequential Poisson Sampling. _Journal of
        Official Statistics_, 14(2): 149-162.

    Rosén, B. (1997). On sampling with probability proportional to
        size. _Journal of Statistical Planning and Inference_, 62(2):
        159-191.

    Examples
    --------
    ```{python}
    import numpy as np
    import pysps

    x = np.arange(10)
    pi = pysps.InclusionProb(x, 6)
    ```

    ```{python}
    # Draw a sequential Poisson sample using permanent random numbers.

    prn = np.random.default_rng(54321).uniform(size=10)
    sample = pysps.OrderSample(pi, prn)
    sample.units
    ```

    ```{python}
    # Get the design weights.
    
    sample.weights
    ```

    ```{python}
    # Units 0 to 2 are take-some units...
    
    sample.take_some
    ```

    ```{python}
    # ... and units 3 to 5 are take-all units.
    
    sample.take_all
    ```

    ```{python}
    # Draw a Pareto order sample using the same permanent random numbers.
    
    pysps.OrderSample(pi, prn, shape=-1).units
    ```
    """

    def __init__(
        self,
        pi: InclusionProb,
        prn: npt.ArrayLike | None = None,
        *,
        shape: float = 1.0,
        sort_method: str = "partial",
    ) -> None:
        u = _generate_random_deviates(prn, pi)
        shape = float(shape)
        n_ts = pi._n - len(pi._ta)
        if n_ts == 0:
            self._units = pi.take_all
        else:
            dist = _igpd(shape)
            xi = dist(u[pi._ts]) / dist(pi._values[pi._ts])
            if sort_method == "partial":
                keep = np.argpartition(xi, n_ts)[:n_ts]
            elif sort_method == "stable":
                keep = np.argsort(xi, kind="stable")[:n_ts]
            else:
                raise ValueError("'sort_method' should be either 'partial' or 'stable'")
            res = np.concatenate((pi._ta, pi._ts[keep]))
            res.sort()
            self._units = res

        ta = np.isin(self._units, pi._ta, assume_unique=True)
        self._ta = np.flatnonzero(ta)
        self._ts = np.flatnonzero(~ta)
        self._pi = pi
        self._prn = u
        self._shape = shape

    def __repr__(self) -> str:
        pi = repr(self._pi)
        prn = repr(self._prn)
        return f"OrderSample({pi}, {prn}, shape={self._shape})"


class PoissonSample(BaseSample):
    """
    Ordinary Poisson sampling.

    Parameters
    ----------
    pi : InclusionProb
        Inclusion probabilities for units in the population.
    prn : ArrayLike, optional
        Permanent random numbers. Should be a flat array of values, the
        same length as `pi`, distributed uniform between 0 and 1. The
        default draws a sample without permanent random numbers.

    Attributes
    ----------
    units : Array
        Indices for units in the sample.
    weights : Array
        Design weights for units in the sample.
    take_all : Array
        Take-all units in the sample.
    take_some : Array
        Take-some units in the sample.
    prn : Array
        Random numbers used for drawing the sample.

    References
    ----------
    Ohlsson, E. (1998). Sequential Poisson Sampling. _Journal of
        Official Statistics_, 14(2): 149-162.

    Examples
    --------
    ```{python}
    import numpy as np
    import pysps

    x = np.arange(10)
    pi = pysps.InclusionProb(x, 6)
    ```

    ```{python}
    # Draw an ordinary Poisson sample using permanent random numbers.

    prn = np.random.default_rng(54321).uniform(size=10)
    sample = pysps.PoissonSample(pi, prn)
    sample.units
    ```
    """

    def __init__(self, pi: InclusionProb, prn: npt.ArrayLike | None = None) -> None:
        u = _generate_random_deviates(prn, pi)
        self._units = np.flatnonzero(u < pi._values)
        ta = np.isin(self._units, pi._ta, assume_unique=True)
        self._ta = np.flatnonzero(ta)
        self._ts = np.flatnonzero(~ta)
        self._pi = pi
        self._prn = u

    def __repr__(self) -> str:
        pi = repr(self._pi)
        prn = repr(self._prn)
        return f"PoissonSample({pi}, {prn})"
