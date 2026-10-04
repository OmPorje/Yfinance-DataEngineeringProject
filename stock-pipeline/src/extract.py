import pandas as pd
import yfinance as yf
from config import TICKERS, RAW_DIR
from datetime import date, timedelta
import json

WATERMARK_FILE = RAW_DIR.parent / 'watermark.json' # data/watermark.json

def load_watermark():
    if WATERMARK_FILE.exists():
        return json.loads(WATERMARK_FILE.read_text())
    return {}

def save_watermark(watermark):
    WATERMARK_FILE.write_text(json.dumps(watermark, indent=2))

watermark = load_watermark()

for ticker in TICKERS:
    print(ticker)

    if ticker in watermark:
        start = date.fromisoformat(watermark[ticker]) + timedelta(days=1)
    else:
        start = date.today() - timedelta(days=30)

    df = yf.download(ticker, start = start, end = date.today() + timedelta(days=1))
    df = df.reset_index()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    print(df[["Date"]])
    print(f"start={start}")

    df['ticker'] = ticker
    out_path = RAW_DIR / f"{ticker}_{date.today()}.parquet"
    df.to_parquet(out_path)
    print(f"{ticker}: {len(df)} rows")

    new_max = str(df["Date"].max().date())
    if ticker not in watermark or new_max > watermark[ticker]:
        watermark[ticker] = new_max

    print(df.columns)

save_watermark(watermark)



print(load_watermark())