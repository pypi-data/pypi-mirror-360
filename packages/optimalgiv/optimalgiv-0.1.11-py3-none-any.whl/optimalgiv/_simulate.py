"""
High-level wrapper for Julia’s `OptimalGIV.simulate_data`.

Exports
-------
simulate_data  – generate one or many synthetic panel DataFrames
SimParam       – ergonomic dataclass mirroring Julia SimParam

Both are re-exported in bridge.__init__ so users can simply write::

    from bridge import simulate_data, SimParam
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from juliacall import Main as jl  # Julia runtime already initialised in __init__


# ---------------------------------------------------------------------
# 1.  Dataclass for autocompletion / type safety (optional for users)
# ---------------------------------------------------------------------
@dataclass
class SimParam:
    # Panel dimensions
    N: int = 10
    T: int = 100
    K: int = 2

    # Structural model parameters
    M: float = 0.5
    sigma_zeta: float = 1.0          # -> σζ
    sigma_p: float = 2.0             # -> σp
    h: float = 0.2
    ushare: float = 0.2
    sigma_u_curv: float = 0.1        # -> σᵤcurv
    nu: float = float("inf")         # -> ν  (Inf ⇒ Normal)
    missingperc: float = 0.0

    # Rarely used: initial guess for tail exponent; Julia overwrites it
    tailparam: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Return a plain ASCII-only dict version."""
        return asdict(self)


# ---------------------------------------------------------------------
# 2.  ASCII -> Unicode field mapping (users may type sigma_zeta etc.)
# ---------------------------------------------------------------------
_ASCII_TO_JULIA: Dict[str, str] = {
    "sigma_zeta": "σζ",
    "sigma_p": "σp",
    "sigma_u_curv": "σᵤcurv",
    "nu": "ν",
    # other keys keep their spelling
}


def _translate_keys(d: Dict[str, Any]) -> Dict[str, Any]:
    """Replace ASCII aliases with the Julia field names expected by SimParam."""
    return {_ASCII_TO_JULIA.get(k, k): v for k, v in d.items() if v is not None}


# ---------------------------------------------------------------------
# 3.  Dict  ->  Julia NamedTuple
# ---------------------------------------------------------------------
def _to_namedtuple(d: Dict[str, Any]):
    """
    Build a Julia NamedTuple literal via `juliacall`.
    Example: {'N': 5, 'σζ': 1.0} → (; N = 5, σζ = 1.0)
    """
    if not d:
        return jl.seval("NamedTuple()")

    parts = [f"{k} = {repr(v)}" for k, v in d.items()]
    return jl.seval(f"(; {', '.join(parts)})")


# ---------------------------------------------------------------------
# 4.  Public API
# ---------------------------------------------------------------------
def simulate_data(
    simparams: Optional[Union[Dict[str, Any], SimParam]] = None,
    *,
    Nsims: int = 1000,
    seed: int = 1,
    **kwargs,
) -> List[pd.DataFrame]:
    """
    Python wrapper for `OptimalGIV.simulate_data`.

    Parameters
    ----------
    simparams : dict | SimParam | None
        Optional container with simulation parameters.  You can *also*
        supply parameters directly as keyword arguments (e.g. `N=20`).
        Keywords override duplicate entries from `simparams`.

    Nsims : int, default 1000
        Number of independent DataFrames to generate.

    seed : int, default 1
        RNG seed for reproducibility.

    **kwargs
        Convenience way to specify parameters directly::
            simulate_data(N=20, T=50, K=3, Nsims=1)

    Returns
    -------
    list[pandas.DataFrame]
    """
    # --------------------------------------------------
    # Merge all parameter sources
    # --------------------------------------------------
    if simparams is None:
        params: Dict[str, Any] = {}
    elif isinstance(simparams, SimParam):
        params = simparams.to_dict()
    elif isinstance(simparams, dict):
        params = simparams.copy()
    else:
        raise TypeError("simparams must be dict, SimParam, or None")

    # kwargs style overrides
    params.update(kwargs)

    # ASCII → Unicode and build NamedTuple
    params = _translate_keys(params)
    nt = _to_namedtuple(params)

    # --------------------------------------------------
    # Call Julia and convert each DataFrame to pandas
    # --------------------------------------------------
    jdfs = jl.OptimalGIV.simulate_data(nt, Nsims=Nsims, seed=seed)
    return [pd.DataFrame(jdf) for jdf in jdfs]
