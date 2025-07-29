import numpy as np
from .rustalib import indicator_atr

def ATR(period: int, high: np.ndarray, low: np.ndarray, close: np.ndarray) -> np.ndarray:
    """
    Average True Range (ATR) using Rust-accelerated backend.

    Parameters
    ----------
    period : int
        Period of the ATR.
    high : np.ndarray
        High prices (float64).
    low : np.ndarray
        Low prices (float64).
    close : np.ndarray
        Close prices (float64).

    Returns
    -------
    np.ndarray
        ATR values (same length as input).
    """
    if not (len(high) == len(low) == len(close)):
        raise ValueError("Input arrays (high, low, close) must have the same length")

    output = np.empty_like(close)
    indicator_atr(period, high, low, close, output)
    return output
