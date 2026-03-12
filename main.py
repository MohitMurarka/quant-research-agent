from dotenv import load_dotenv
from tools.fetch_data import fetch_price_data, fetch_summary

load_dotenv()

# Test 1: raw price data
data = fetch_price_data(["AAPL", "SPY"], "2020-01-01", "2023-01-01")

print("\n--- RAW DATA TEST ---")
for ticker, df in data.items():
    print(f"\n{ticker} - first 3 rows:")
    print(df.head(3))
    print(f"{ticker} - columns: {list(df.columns)}")

# Test 2: summary (this is what Code Writer will receive)
print("\n--- SUMMARY TEST ---")
summary = fetch_summary(["AAPL", "SPY"], "2020-01-01", "2023-01-01")
print(summary)