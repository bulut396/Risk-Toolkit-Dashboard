"""risk-toolkit-dashboard — a Streamlit app for stock risk analysis.

Enter a ticker, fetch live prices via yfinance, and view risk metrics computed
by the ``risk-toolkit`` library along with interactive charts and a plain-language
summary. Run with::

    streamlit run app.py
"""

from __future__ import annotations

from typing import Any, Dict

import pandas as pd
import streamlit as st

from risk_toolkit import (
    annualized_volatility,
    beta,
    historical_var,
    max_drawdown,
    parametric_var,
    prices_to_returns,
    sharpe_ratio,
    sortino_ratio,
)

from charts import (
    plot_drawdown,
    plot_price_history,
    plot_returns_distribution,
)
from data_fetcher import fetch_market_benchmark, fetch_price_history

PERIOD_OPTIONS = ["1mo", "3mo", "6mo", "1y", "2y"]
MIN_MEANINGFUL_POINTS = 10


def generate_summary(metrics: Dict[str, Any]) -> str:
    """Build a plain-language interpretation from the computed metrics.

    Pure template/conditional logic — no AI/LLM call. Buckets each metric into
    qualitative bands and stitches together a short, friendly paragraph.

    Parameters
    ----------
    metrics : dict
        Dictionary with keys ``volatility``, ``sharpe``, ``sortino``, ``beta``,
        ``max_drawdown`` (all floats).

    Returns
    -------
    str
        A short multi-sentence summary in plain English.
    """
    vol = metrics["volatility"]
    sharpe = metrics["sharpe"]
    beta_val = metrics["beta"]
    mdd = metrics["max_drawdown"]

    # Volatility band.
    if vol < 0.15:
        risk_word = "relatively low"
    elif vol < 0.30:
        risk_word = "moderate"
    else:
        risk_word = "high"

    # Sharpe band.
    if sharpe > 1:
        sharpe_word = "strong"
    elif sharpe > 0:
        sharpe_word = "decent"
    else:
        sharpe_word = "poor (it has not rewarded its risk)"

    # Beta band.
    if beta_val > 1.1:
        beta_word = "more volatile than the overall market"
    elif beta_val < 0.9:
        beta_word = "less volatile than the overall market"
    else:
        beta_word = "about as volatile as the overall market"

    return (
        f"This asset has **{risk_word} risk** "
        f"(annualized volatility ~{vol:.0%}). "
        f"Its risk-adjusted return is **{sharpe_word}** "
        f"(Sharpe {sharpe:.2f}). "
        f"It is **{beta_word}** (beta {beta_val:.2f}). "
        f"The worst historical decline (max drawdown) was "
        f"**{mdd:.1%}** from peak to trough."
    )


def _metric_with_caption(col, label: str, value: str, caption: str) -> None:
    """Render an ``st.metric`` with a one-line plain-language caption."""
    col.metric(label, value)
    col.caption(caption)


def run_analysis(ticker: str, period: str, rf_rate: float) -> None:
    """Fetch data, compute every metric, and render the full results view.

    Parameters
    ----------
    ticker : str
        Stock ticker entered by the user.
    period : str
        yfinance period string.
    rf_rate : float
        Annual risk-free rate as a decimal (e.g. ``0.04`` for 4%).
    """
    with st.spinner(f"Fetching data for {ticker.upper()}..."):
        asset_prices = fetch_price_history(ticker, period=period)
        market_prices = fetch_market_benchmark(period=period)

    asset_returns = prices_to_returns(asset_prices)
    market_returns = prices_to_returns(market_prices)

    if len(asset_returns) < MIN_MEANINGFUL_POINTS:
        st.warning(
            f"Only {len(asset_returns)} data points were returned for this "
            "period. Results may not be statistically meaningful — try a longer "
            "time period."
        )

    # Align asset and market returns on common dates so beta has equal-length
    # inputs (the two series can differ by a trading day).
    aligned = pd.concat(
        {"asset": asset_returns, "market": market_returns}, axis=1
    ).dropna()
    beta_val = beta(aligned["asset"], aligned["market"])

    vol = annualized_volatility(asset_returns)
    sharpe = sharpe_ratio(asset_returns, risk_free_rate=rf_rate)
    sortino = sortino_ratio(asset_returns, risk_free_rate=rf_rate)
    dd = max_drawdown(asset_returns)
    hist_var = historical_var(asset_returns, confidence_level=0.95)
    param_var = parametric_var(asset_returns, confidence_level=0.95)

    st.subheader(f"Risk metrics for {ticker.upper()} ({period})")

    # --- Row 1 of metric cards ---
    c1, c2, c3 = st.columns(3)
    _metric_with_caption(
        c1, "Annualized Volatility", f"{vol:.1%}",
        "How much the price swings. Higher means riskier.",
    )
    _metric_with_caption(
        c2, "Sharpe Ratio", f"{sharpe:.2f}",
        "Return per unit of risk. Above 1 is considered good.",
    )
    _metric_with_caption(
        c3, "Sortino Ratio", f"{sortino:.2f}",
        "Like Sharpe but only penalizes downside. Higher is better.",
    )

    # --- Row 2 of metric cards ---
    c4, c5, c6 = st.columns(3)
    _metric_with_caption(
        c4, "Beta (vs. S&P 500)", f"{beta_val:.2f}",
        "1.0 = moves with the market. >1 = more volatile.",
    )
    _metric_with_caption(
        c5, "Max Drawdown", f"{dd['max_drawdown']:.1%}",
        "The worst peak-to-trough drop. Closer to 0 is safer.",
    )
    _metric_with_caption(
        c6, "Value at Risk (95%)", f"{hist_var:.1%}",
        f"A typical bad day. Parametric estimate: {param_var:.1%}.",
    )

    # --- Charts ---
    st.plotly_chart(plot_price_history(asset_prices, ticker.upper()),
                    use_container_width=True)
    st.plotly_chart(
        plot_drawdown(asset_prices, dd["peak_index"], dd["trough_index"]),
        use_container_width=True,
    )
    st.plotly_chart(plot_returns_distribution(asset_returns),
                    use_container_width=True)

    # --- Plain-language summary ---
    st.subheader("In plain language")
    summary = generate_summary(
        {
            "volatility": vol,
            "sharpe": sharpe,
            "sortino": sortino,
            "beta": beta_val,
            "max_drawdown": dd["max_drawdown"],
        }
    )
    st.info(summary)


def main() -> None:
    """Render the Streamlit page and wire up the sidebar controls."""
    st.set_page_config(page_title="risk-toolkit-dashboard", page_icon="📊")

    st.title("📊 Stock Risk Dashboard")
    st.write(
        "Enter a stock ticker to see its risk profile — volatility, "
        "risk-adjusted returns, drawdowns and more. Live data is fetched "
        "automatically; no setup or API key required."
    )

    with st.sidebar:
        st.header("Settings")
        ticker = st.text_input("Ticker symbol", value="AAPL")
        period = st.selectbox(
            "Time period", PERIOD_OPTIONS, index=PERIOD_OPTIONS.index("6mo")
        )
        rf_pct = st.number_input(
            "Risk-free rate (%)",
            min_value=0.0,
            max_value=20.0,
            value=4.0,
            step=0.25,
            help="Annual risk-free rate used for Sharpe/Sortino ratios.",
        )
        run = st.button("Run Analysis", type="primary")

    if not run:
        st.caption("👈 Set your options in the sidebar and click **Run Analysis**.")
        return

    if not ticker.strip():
        st.warning("Please enter a ticker symbol to get started (e.g. AAPL).")
        return

    try:
        run_analysis(ticker, period, rf_pct / 100.0)
    except ValueError as exc:
        # Expected, user-facing problems (bad ticker, no data, etc.).
        st.error(str(exc))
    except Exception:  # noqa: BLE001 - last-resort guard so the app never crashes
        st.error(
            "Something went wrong while analyzing this ticker. Please try a "
            "different symbol or time period."
        )


if __name__ == "__main__":
    main()
