import numpy as np
from .rustalib import indicator_ema;

def EMA(period: int, data: np.ndarray) -> np.ndarray:
    """
    Exponential Moving Average (EMA) using Rust-accelerated backend.

    Parameters
    ----------
    period : int
        Period of the EMA.
    data : np.ndarray
        Input time series (float64).

    Returns
    -------
    np.ndarray
        EMA values (same length as input).
    """
    output = np.empty_like(data)
    indicator_ema(period, data, output)
    return output