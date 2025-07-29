import numpy as np
from .rustalib import indicator_macd

def MACD(
    fast_period: int,
    slow_period: int,
    signal_period: int,
    data: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Moving Average Convergence Divergence (MACD) using Rust-accelerated backend.

    Parameters
    ----------
    fast_period : int,
        Fast EMA period.
    slow_period : int,
        Slow EMA period.
    signal_period : int,
        Signal EMA period (applied to MACD line).
    data : np.ndarray
        Input time series (float64).

    Returns
    -------
    tuple of np.ndarray
        (macd_line, signal_line, histogram) - all same length as input.
    """
    if data.dtype != np.float64 or not data.flags['C_CONTIGUOUS']:
        data = np.ascontiguousarray(data, dtype=np.float64)

    macd = np.empty_like(data)
    signal = np.empty_like(data)
    hist = np.empty_like(data)

    indicator_macd(fast_period, slow_period, signal_period, data, macd, signal, hist)
    return macd, signal, hist
