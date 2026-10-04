import pandas as pd
import duckdb

from config import RAW_DIR, DUCK_DB

files = list(RAW_DIR.glob('*.parquet'))

frames = [pd.read_parquet(f) for f in files]
df = pd.concat(frames, ignore_index=True)

print(f"before cleaning: {len(df)}")

print(df['ticker'].value_counts())

def clean(df):
    RENAME_MAP = {
    "Date": "date",
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Close": "close",
    "Volume": "volume",
    "ticker": "ticker",
}
    df = df.rename(columns=RENAME_MAP)

    df = df.dropna(subset = ['ticker', 'date', 'close'])
    df = df.drop_duplicates(subset =['ticker', 'date'], keep='last')

    df = df[(df["low"] <= df["high"]) & (df["open"] > 0) & (df["close"] > 0)]

    return df

df = clean(df)
print(f"after cleaning: {len(df)}")


def add_metrics(df):
    grouped = df.groupby('ticker', group_keys=False)

    df['daily_return'] = grouped['close'].pct_change()
    df['ma_7'] = grouped['close'].transform(lambda s: s.rolling(7, min_periods=1).mean())
    df['ma_30'] = grouped['close'].transform(lambda s: s.rolling(30, min_periods=1).mean())
    df['volatility_30d'] = grouped['daily_return'].transform(lambda s: s.rolling(30, min_periods=5).std())
    return df

df = add_metrics(df)
print(df[df["ticker"] == "AAPL"][["date", "close", "daily_return", "ma_7", "ma_30", "volatility_30d"]].head(10))

def load_to_duckdb(df):
    con = duckdb.connect(str(DUCK_DB))
    con.execute("""
        CREATE TABLE IF NOT EXISTS stock_prices (
            ticker TEXT,
            date DATE,
            close DOUBLE,
            daily_return DOUBLE,
            ma_7 DOUBLE,
            ma_30 DOUBLE,
            volatility_30d DOUBLE,
            open DOUBLE,
            high DOUBLE,
            low DOUBLE,
            volume DOUBLE,
            PRIMARY KEY (ticker, date)
        );
            """) # Create Table
    con.register('staging_df',df)
    con.execute("""
    INSERT INTO stock_prices
        (ticker, date, close, daily_return, ma_7, ma_30, volatility_30d, open, high, low, volume)
    SELECT
        ticker, date, close, daily_return, ma_7, ma_30, volatility_30d, open, high, low, volume
    FROM staging_df
    ON CONFLICT (ticker, date) DO UPDATE SET
        close = excluded.close,
        daily_return = excluded.daily_return,
        ma_7 = excluded.ma_7,
        ma_30 = excluded.ma_30,
        volatility_30d = excluded.volatility_30d,
        open = excluded.open,
        high = excluded.high,
        low = excluded.low,
        volume = excluded.volume;
""") # INSERT .... ON CONFLICT
    con.close()

df = clean(df)
df = add_metrics(df)
load_to_duckdb(df)


