import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt


CSV_FILE = "crypto_data.csv"


def main():
    data = pd.read_csv(CSV_FILE)

    required_columns = {
        "symbol", "timestamp", "open", "high", "low", "close", "volume"
    }

    missing_columns = required_columns - set(data.columns)
    if missing_columns:
        print("The CSV does not contain candle data.")
        print("Choose OHLCV candles when fetching data, then run this script again.")
        return

    available_symbols = sorted(data["symbol"].dropna().unique())

    if not available_symbols:
        print("No coins were found in the CSV file.")
        return

    print("Which coin do you want to chart?")
    for number, symbol in enumerate(available_symbols, start=1):
        print(f"{number}. {symbol}")

    while True:
        choice = input("Enter the number: ").strip()

        if choice.isdigit() and 1 <= int(choice) <= len(available_symbols):
            symbol = available_symbols[int(choice) - 1]
            break

        print("Please enter one of the listed numbers.")

    coin_data = data[data["symbol"] == symbol].copy()
    coin_data["timestamp"] = pd.to_datetime(coin_data["timestamp"], utc=True)

    coin_data = coin_data.set_index("timestamp")
    coin_data = coin_data.rename(
        columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume",
        }
    )

    coin_data = coin_data[["Open", "High", "Low", "Close", "Volume"]]
    coin_data = coin_data.apply(pd.to_numeric, errors="coerce")
    coin_data = coin_data.dropna().sort_index()

    if coin_data.empty:
        print(f"No valid candle rows found for {symbol}.")
        return

    figure, axes = mpf.plot(
        coin_data,
        type="candle",
        volume=True,
        style="yahoo",
        title=f"{symbol} Candlestick Chart",
        ylabel="Price (USDT)",
        returnfig=True,
    )

    output_file = symbol.replace("/", "_") + "_candlestick.png"
    figure.savefig(output_file, bbox_inches="tight")
    print(f"Chart saved as {output_file}")

    plt.show()


if __name__ == "__main__":
    main()