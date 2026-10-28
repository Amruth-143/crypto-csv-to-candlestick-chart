import csv
from datetime import datetime, timedelta, timezone

import ccxt

def ask_symbols():
    print("\nWhich coins do you want?")
    print("1. SOL")
    print("2. ETH")
    print("3. BTC")

    choices = {
        "1": "SOL/USDT",
        "2": "ETH/USDT",
        "3": "BTC/USDT",
    }

    while True:
        selected = input("Enter one or more numbers, separated by commas (for example 1,3): ")
        numbers = [number.strip() for number in selected.split(",")]

        if numbers and all(number in choices for number in numbers):
            return list(dict.fromkeys(choices[number] for number in numbers))

        print("Please enter 1, 2, or 3, separated by commas.")

SYMBOLS = ["SOL/USDT", "BTC/USDT", "ETH/USDT"]
OUTPUT_FILE = "crypto_data.csv"


def ask_choice():
    print("What data do you want?")
    print("1. Historical OHLCV candles (open, high, low, close, volume)")
    print("2. Current ticker snapshot")

    while True:
        choice = input("Enter 1 or 2: ").strip()
        if choice in ("1", "2"):
            return choice
        print("Please enter 1 or 2.")


def ask_candle_settings(exchange):
    timeframes = exchange.timeframes
    supported = ", ".join(timeframes.keys())

    print(f"\nAvailable candle intervals: {supported}")
    while True:
        timeframe = input("Candle interval (for example 1h or 1d): ").strip()
        if timeframe in timeframes:
            break
        print("That interval is not supported by this exchange.")

    while True:
        try:
            days = int(input("How many days of history do you want? ").strip())
            if days > 0:
                return timeframe, days
        except ValueError:
            pass
        print("Enter a whole number greater than 0.")


def fetch_candles(exchange, symbol, timeframe, days):
    end_ms = exchange.milliseconds()
    start_ms = end_ms - days * 24 * 60 * 60 * 1000
    timeframe_ms = exchange.parse_timeframe(timeframe) * 1000
    limit = 1000
    rows = []
    since = start_ms

    while since < end_ms:
        batch = exchange.fetch_ohlcv(
            symbol,
            timeframe=timeframe,
            since=since,
            limit=limit,
        )

        if not batch:
            break

        new_rows = [candle for candle in batch if start_ms <= candle[0] < end_ms]
        rows.extend(new_rows)

        last_timestamp = batch[-1][0]
        next_since = last_timestamp + timeframe_ms

        # Stop if the exchange returns no newer data, to avoid looping forever.
        if next_since <= since:
            break

        since = next_since

    # Remove duplicate timestamps and sort chronologically.
    unique_rows = {row[0]: row for row in rows}
    rows = [unique_rows[timestamp] for timestamp in sorted(unique_rows)]

    return [
        {
            "symbol": symbol,
            "timestamp": datetime.fromtimestamp(
                timestamp / 1000, tz=timezone.utc
            ).isoformat(),
            "open": open_price,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
        for timestamp, open_price, high, low, close, volume in rows
    ]


def fetch_ticker(exchange, symbol):
    ticker = exchange.fetch_ticker(symbol)
    timestamp = ticker.get("timestamp")

    return {
        "symbol": symbol,
        "timestamp": (
            datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc).isoformat()
            if timestamp
            else ""
        ),
        "last": ticker.get("last"),
        "bid": ticker.get("bid"),
        "ask": ticker.get("ask"),
        "high": ticker.get("high"),
        "low": ticker.get("low"),
        "baseVolume": ticker.get("baseVolume"),
        "quoteVolume": ticker.get("quoteVolume"),
    }


def main():
    exchange = ccxt.binance({"enableRateLimit": True})
    exchange.load_markets()
    symbols = ask_symbols()

    choice = ask_choice()
    all_rows = []

    if choice == "1":
        timeframe, days = ask_candle_settings(exchange)
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        print(f"\nFetching {timeframe} candles since {start_date.isoformat()}...")

        for symbol in symbols:
            if symbol not in exchange.markets:
                print(f"Skipping {symbol}: market not available.")
                continue

            print(f"Fetching {symbol}...")
            all_rows.extend(fetch_candles(exchange, symbol, timeframe, days))

    else:
        print("\nFetching current ticker snapshots...")
        for symbol in SYMBOLS:
            if symbol not in exchange.markets:
                print(f"Skipping {symbol}: market not available.")
                continue

            print(f"Fetching {symbol}...")
            all_rows.append(fetch_ticker(exchange, symbol))

    if not all_rows:
        print("No data was returned.")
        return

    # Use the combined set of keys so the same CSV can hold either data type.
    fieldnames = sorted({key for row in all_rows for key in row})

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\nSaved {len(all_rows)} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()