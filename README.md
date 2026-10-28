# Crypto CSV to Candlestick Chart

A Python mini project that fetches public spot market data for SOL, ETH, and BTC from Binance with CCXT, saves the data to CSV, and creates a candlestick chart from OHLCV candle data.

## Features

- Choose one or more coins in the terminal.
- Fetch OHLCV candles for a selected timeframe and number of days, or fetch ticker snapshots.
- Save fetched market data to `crypto_data.csv`.
- Select a coin from the candle CSV and create a candlestick chart with volume.
- Save the chart as a PNG image.

## Requirements

- Python 3.10 or newer
- Internet access for Binance public market data

No Binance API key is needed.

## Installation

In a terminal, change into this project folder and install the dependencies:

```bash
python -m pip install -r requirements.txt
```

## Fetch market data

Run the fetcher:

```bash
python data_fetcher.py
```

Choose the coins, then choose either historical OHLCV candles or a ticker snapshot. For OHLCV candles, enter a Binance-supported timeframe (such as `1h` or `1d`) and the number of history days. The script saves the results as `crypto_data.csv` in the current working directory.

Ticker snapshots contain current market statistics, not historical candles. Select the OHLCV option to make a candlestick chart.

## Create a candlestick chart

After fetching OHLCV data, run:

```bash
python CSVtocandlestick_converter.py
```

Choose a coin listed from the CSV. The chart is displayed and saved in the current working directory as a file such as `SOL_USDT_candlestick.png`.

## Project files

- `data_fetcher.py` — fetches public Binance data through CCXT.
- `CSVtocandlestick_converter.py` — reads `crypto_data.csv` and plots a selected coin.
- `requirements.txt` — Python package dependencies.
- `pyproject.toml` — project metadata and dependencies.

## Notes

- Run both scripts from this project folder so they find and save files in the expected location.
- The chart converter expects OHLCV columns: `symbol`, `timestamp`, `open`, `high`, `low`, `close`, and `volume`.
- In the current fetcher code, the coin selection is applied to OHLCV mode. Ticker mode fetches all three configured coins.
- The generated CSV and PNG are local outputs and are excluded from version control.
