import yfinance as yf
import pandas as pd
from datetime import datetime


def fetch_price_data(tickers: list[str], start: str, end: str) -> dict:
    """
    Fetch historical OHLCV data for a list of tickers.
    Returns a dict of {ticker: DataFrame}
    """
    print(f"\n[DATA FETCHER] Fetching data for: {tickers}")
    print(f"[DATA FETCHER] Timeframe: {start} to {end}")

    result = {}

    for ticker in tickers:
        try:
            df = yf.download(ticker, start=start, end=end, progress=False)

            if df.empty:
                print(f"[DATA FETCHER] WARNING: No data found for {ticker}")
                continue

            # Flatten MultiIndex columns if present (yfinance quirk)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # Clean up
            df.index = pd.to_datetime(df.index)
            df = df.dropna()

            result[ticker] = df
            print(f"[DATA FETCHER] {ticker}: {len(df)} trading days fetched")

        except Exception as e:
            print(f"[DATA FETCHER] ERROR fetching {ticker}: {e}")

    return result


def fetch_summary(tickers: list[str], start: str, end: str) -> str:
    """
    Returns a plain text summary of the data available.
    This gets passed to the Code Writer so it knows what data exists.
    """
    data = fetch_price_data(tickers, start, end)

    lines = []
    lines.append("Available data summary:")
    lines.append(f"Tickers: {list(data.keys())}")
    lines.append(f"Timeframe: {start} to {end}")
    lines.append("")

    for ticker, df in data.items():
        lines.append(f"{ticker}:")
        lines.append(f"  - Columns: {list(df.columns)}")
        lines.append(f"  - Date range: {df.index[0].date()} to {df.index[-1].date()}")
        lines.append(f"  - Total rows: {len(df)}")
        lines.append(f"  - Sample close prices:")
        lines.append(f"    First: ${df['Close'].iloc[0]:.2f}")
        lines.append(f"    Last:  ${df['Close'].iloc[-1]:.2f}")
        lines.append("")

    return "\n".join(lines)


def generate_fallback_chart(output_text: str, hypothesis: str):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import re
    import os

    os.makedirs("outputs", exist_ok=True)

    metrics = {}

    # Broad patterns — handle "Total Return AAPL", "Sharpe Ratio AAPL", etc.
    patterns = {
        "Total Return (%)": r"Total Return[^:\n]*:\s*([+-]?\d+\.?\d*)",
        "Sharpe Ratio": r"Sharpe Ratio[^:\n]*:\s*([+-]?\d+\.?\d*)",
        "Win Rate (%)": r"Win Rate[^:\n]*:\s*([+-]?\d+\.?\d*)",
        "Max Drawdown (%)": r"Max Drawdown[^:\n]*:\s*([+-]?\d+\.?\d*)",
        "Annualized Return (%)": r"Annualized Return[^:\n]*:\s*([+-]?\d+\.?\d*)",
        "Avg AAPL Return (%)": r"Average AAPL Return[^:\n]*:\s*([+-]?\d+\.?\d*)",
        "Avg SPY Return (%)": r"Average S.P.*?Return[^:\n]*:\s*([+-]?\d+\.?\d*)",
    }

    for label, pattern in patterns.items():
        match = re.search(pattern, output_text, re.IGNORECASE)
        if match:
            val = float(match.group(1))
            # Skip obviously broken values
            if abs(val) < 500:
                metrics[label] = val

    if not metrics:
        print("[CHART] Could not parse any metrics from output")
        return False

    fig, ax = plt.subplots(figsize=(11, 6))
    colors = ["#2ecc71" if v >= 0 else "#e74c3c" for v in metrics.values()]
    bars = ax.bar(
        range(len(metrics)),
        metrics.values(),
        color=colors,
        edgecolor="black",
        linewidth=0.5,
        width=0.6,
    )

    for bar, val in zip(bars, metrics.values()):
        offset = 0.3 if val >= 0 else -0.8
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + offset,
            f"{val:.2f}",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )

    ax.set_xticks(range(len(metrics)))
    ax.set_xticklabels(metrics.keys(), rotation=20, ha="right", fontsize=9)
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--", alpha=0.5)
    ax.set_title(
        f"Backtest Results\n{hypothesis[:90]}{'...' if len(hypothesis) > 90 else ''}",
        fontsize=10,
        fontweight="bold",
        pad=12,
    )
    ax.set_ylabel("Value")
    plt.tight_layout()
    plt.savefig("outputs/backtest_chart.png", dpi=100, bbox_inches="tight")
    plt.close()
    print(
        f"[CHART] Generated chart with {len(metrics)} metrics: {list(metrics.keys())}"
    )
    return True
