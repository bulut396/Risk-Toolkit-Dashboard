"""Price-data fetching for the risk-toolkit-dashboard app.

Uses yfinance (free, no API key) to pull daily closing prices. All functions
return a clean ``pandas.Series`` of closing prices indexed by date.
"""

from __future__ import annotations

import pandas as pd
import yfinance as yf

# S&P 500 index, used as the default market benchmark for beta.
MARKET_BENCHMARK_TICKER = "^GSPC"


def _extract_close_series(data: pd.DataFrame, ticker: str) -> pd.Series:
    """Pull a 1-D closing-price Series out of a yfinance download frame.

    yfinance may return either flat columns (``Close``) or MultiIndex columns
    (``("Close", ticker)``) depending on version and arguments. This normalizes
    both to a single dated Series.

    Parameters
    ----------
    data : pandas.DataFrame
        The frame returned by :func:`yfinance.download`.
    ticker : str
        The requested ticker, used only to label the resulting Series.

    Returns
    -------
    pandas.Series
        Closing prices indexed by date, with non-trading/NaN rows removed.
    """
    close = data["Close"]
    # MultiIndex case: data["Close"] is itself a DataFrame of ticker columns.
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close = close.dropna()
    close.name = ticker
    return close


def fetch_price_history(ticker: str, period: str = "6mo") -> pd.Series:
    """Fetch daily closing prices for a ticker.

    Parameters
    ----------
    ticker : str
        Stock ticker symbol, e.g. ``"AAPL"``.
    period : str, optional
        A yfinance-compatible period string (``"1mo"``, ``"3mo"``, ``"6mo"``,
        ``"1y"``, ``"2y"``). Defaults to ``"6mo"``.

    Returns
    -------
    pandas.Series
        Closing prices indexed by date, oldest to newest.

    Raises
    ------
    ValueError
        If the ticker is empty/invalid or no data is returned. The message is
        user-facing and intentionally non-technical.
    """
    symbol = (ticker or "").strip().upper()
    if not symbol:
        raise ValueError("Please enter a ticker symbol.")

    try:
        data = yf.download(
            symbol,
            period=period,
            progress=False,
            auto_adjust=True,
        )
    except Exception:
        # Network / yfinance internal errors -> friendly message.
        raise ValueError(
            f"Could not fetch data for ticker '{symbol}'. "
            "Check the symbol and your connection, then try again."
        )

    if data is None or data.empty or "Close" not in data:
        raise ValueError(
            f"No data found for ticker '{symbol}'. "
            "Check the symbol and try again."
        )

    close = _extract_close_series(data, symbol)
    if close.empty:
        raise ValueError(
            f"No data found for ticker '{symbol}'. "
            "Check the symbol and try again."
        )
    return close


def fetch_market_benchmark(period: str = "6mo") -> pd.Series:
    """Fetch closing prices for the market benchmark (S&P 500).

    Reuses :func:`fetch_price_history` with the hardcoded ``^GSPC`` ticker.

    Parameters
    ----------
    period : str, optional
        A yfinance-compatible period string. Defaults to ``"6mo"``.

    Returns
    -------
    pandas.Series
        Benchmark closing prices indexed by date.

    Raises
    ------
    ValueError
        If benchmark data cannot be retrieved.
    """
    return fetch_price_history(MARKET_BENCHMARK_TICKER, period=period)
