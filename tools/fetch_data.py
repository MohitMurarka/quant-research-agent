import yfinance as yf
import pandas as pd
from datetime import datetime


def fetch_price_data(tickers: list[str], start: str, end: str) -> dict:
    """Fetch historical OHLCV data for a list of tickers.
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
