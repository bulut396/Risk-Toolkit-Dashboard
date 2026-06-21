"""Interactive chart builders for the risk-toolkit-dashboard app.

Each function returns a Plotly ``Figure`` ready to hand to
``st.plotly_chart``.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.graph_objects as go


def plot_price_history(prices: pd.Series, ticker: str) -> go.Figure:
    """Build an interactive line chart of the price series over time.

    Parameters
    ----------
    prices : pandas.Series
        Closing prices indexed by date.
    ticker : str
        Ticker symbol, used in the chart title.

    Returns
    -------
    plotly.graph_objects.Figure
        Line chart of price vs. date.
    """
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=prices.index,
            y=prices.values,
            mode="lines",
            name=f"{ticker} price",
            line=dict(color="#2E86DE", width=2),
        )
    )
    fig.update_layout(
        title=f"{ticker} — Price History",
        xaxis_title="Date",
        yaxis_title="Price",
        hovermode="x unified",
        template="plotly_white",
    )
    return fig


def plot_drawdown(
    prices: pd.Series,
    peak_index: Any,
    trough_index: Any,
) -> go.Figure:
    """Build a price chart with the maximum-drawdown peak and trough marked.

    The peak (start of the biggest decline) and trough (bottom) are highlighted
    with markers and vertical guide lines so the worst drop is obvious at a
    glance, even to a non-finance reader.

    Parameters
    ----------
    prices : pandas.Series
        Closing prices indexed by date.
    peak_index : hashable
        Index label of the peak before the worst drawdown (from
        ``risk_toolkit.max_drawdown``).
    trough_index : hashable
        Index label of the worst point (from ``risk_toolkit.max_drawdown``).

    Returns
    -------
    plotly.graph_objects.Figure
        Price line with peak/trough annotations.
    """
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=prices.index,
            y=prices.values,
            mode="lines",
            name="Price",
            line=dict(color="#2E86DE", width=2),
        )
    )

    # Look up the prices at the peak and trough dates, if available.
    peak_price = prices.get(peak_index)
    trough_price = prices.get(trough_index)

    if peak_price is not None:
        fig.add_vline(x=peak_index, line=dict(color="#27AE60", dash="dash"))
        fig.add_trace(
            go.Scatter(
                x=[peak_index],
                y=[peak_price],
                mode="markers+text",
                name="Peak",
                text=["Peak"],
                textposition="top center",
                marker=dict(color="#27AE60", size=12, symbol="triangle-up"),
            )
        )

    if trough_price is not None:
        fig.add_vline(x=trough_index, line=dict(color="#E74C3C", dash="dash"))
        fig.add_trace(
            go.Scatter(
                x=[trough_index],
                y=[trough_price],
                mode="markers+text",
                name="Trough",
                text=["Trough"],
                textposition="bottom center",
                marker=dict(color="#E74C3C", size=12, symbol="triangle-down"),
            )
        )

    fig.update_layout(
        title="Maximum Drawdown — Biggest Peak-to-Trough Decline",
        xaxis_title="Date",
        yaxis_title="Price",
        hovermode="x unified",
        template="plotly_white",
    )
    return fig


def plot_returns_distribution(returns: pd.Series) -> go.Figure:
    """Build a histogram of daily returns.

    Parameters
    ----------
    returns : pandas.Series
        Daily simple returns.

    Returns
    -------
    plotly.graph_objects.Figure
        Histogram showing the spread of daily returns.
    """
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=returns.values,
            nbinsx=30,
            marker=dict(color="#2E86DE"),
            name="Daily returns",
        )
    )
    fig.update_layout(
        title="Distribution of Daily Returns",
        xaxis_title="Daily return",
        yaxis_title="Number of days",
        template="plotly_white",
        bargap=0.05,
    )
    return fig
