import numpy as np
from .rustalib import indicator_sma

def SMA(period: int, data: np.ndarray) -> np.ndarray:
    """
    Simple Moving Average (SMA) using Rust-accelerated backend.

    Parameters
    ----------
    period : int
        Period of the SMA.
    data : np.ndarray
        Input time series (float64).

    Returns
    -------
    np.ndarray
        SMA values (same length as input).
    """
    output = np.empty_like(data)
    indicator_sma(period, data, output)
    return output
