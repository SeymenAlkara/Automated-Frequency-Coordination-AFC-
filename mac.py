"""MAC utilities based on the Bianchi saturated DCF model.

Current scope: fixed-point solver for (tau, p) given number of contenders,
CWmin, and backoff stages. Extensions for Wi‑Fi 6/6E OFDMA can be layered on top.
"""

import math


def bianchi_fixed_point(n_stations: int, cwmin: int, m_max_backoff: int, tol: float = 1e-10, max_iter: int = 1000) -> tuple[float, float]:
    """Solve Bianchi saturated DCF fixed point for (tau, p).

    p = 1 - (1 - tau)^{N-1}
    tau = [2 (1 - 2p)] / [ (1 - 2p)(W + 1) + p W (1 - (2p)^m) ]
    """
    if n_stations < 1 or cwmin < 1 or m_max_backoff < 0:
        raise ValueError("Invalid inputs")

    p = 0.1
    for _ in range(max_iter):
        numerator = 2.0 * (1.0 - 2.0 * p)
        denom = (1.0 - 2.0 * p) * (cwmin + 1.0) + p * cwmin * (1.0 - (2.0 * p) ** m_max_backoff)
        if denom <= 0:
            denom = 1e-12
        tau = numerator / denom
        p_new = 1.0 - (1.0 - tau) ** (n_stations - 1)
        if abs(p_new - p) < tol:
            p = p_new
            break
        p = p_new
    return tau, p

