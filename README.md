# Risk-Toolkit-Dashboard

A Streamlit web dashboard that fetches live stock prices and shows a clear, beginner-friendly risk profile for any ticker.

<!-- TODO: add screenshot here after first run -->

## Features

- 🔎 Type any stock ticker and analyze it instantly — no setup or API key needed
- 📈 Live daily price data via `yfinance`
- 📊 Risk metrics: annualized volatility, Sharpe ratio, Sortino ratio, beta (vs. S&P 500), max drawdown, and Value at Risk (historical & parametric)
- 🖼️ Interactive charts: price history, drawdown (peak/trough highlighted), and a returns distribution histogram
- 🗣️ A plain-language summary that explains the numbers for non-finance readers
- 🛡️ Friendly error handling — invalid tickers never crash the app

## Installation

```bash
git clone https://github.com/bulut396/Risk-Toolkit-Dashboard-.git risk-toolkit-dashboard
cd risk-toolkit-dashboard
pip install -r requirements.txt
streamlit run app.py
```

> The app installs the [`risk-toolkit`](https://github.com/bulut396/Python-Risk-Management-Library) library automatically (listed in `requirements.txt`).

## How It Works

The dashboard is a thin **consumer** of the [`risk-toolkit`](https://github.com/bulut396/Python-Risk-Management-Library) library — it does not reimplement any financial math. When you click **Run Analysis**, it fetches live closing prices for your ticker (and the S&P 500 benchmark) from `yfinance`, converts them to returns, and calls `risk-toolkit`'s functions (`annualized_volatility`, `sharpe_ratio`, `sortino_ratio`, `beta`, `max_drawdown`, `historical_var`, `parametric_var`) to compute the metrics. The results are rendered as metric cards, interactive Plotly charts, and a plain-language summary.

## License

Released under the [MIT License](LICENSE).
