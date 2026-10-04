from config import DUCK_DB
import duckdb
import sys

con = duckdb.connect(str(DUCK_DB), read_only=True)

null_count = con.execute('''
    SELECT COUNT(*) from stock_prices
    WHERE ticker IS NULL OR date IS NULL OR Close IS NULL
''').fetchone()[0]

if null_count > 0:
    print(f'FAILED: {null_count} rows with null ticker/date/close')
    sys.exit(1)
else:
    print("Check passed : no nulls in required columns")


dupe_count = con.execute("""
    SELECT COUNT(*) FROM (
    SELECT ticker, date, COUNT(*) c
    from stock_prices
    GROUP BY ticker, date
    HAVING c > 1)
""").fetchone()[0]

if dupe_count > 0:
    print(f"FAILED: {dupe_count} duplicate (ticker, date) pairs")
    sys.exit(1)
else:
    print("Check passed: no duplicate (ticker, date) pairs")

price_check = con.execute("""
    SELECT COUNT(*) FROM stock_prices
    WHERE low > high OR open <= 0 OR close <= 0
""").fetchone()[0]

if price_check > 0:
    print(f"FAILED: {price_check} rows with impossible prices")
    sys.exit(1)
else:
    print("Check passed: no impossible prices")

stale = con.execute("""
    SELECT ticker, MAX(date) AS last_date
    FROM stock_prices
    GROUP BY ticker
    HAVING MAX(date) < CURRENT_DATE - INTERVAL 7 DAY
""").fetchall()

if stale:
    tickers = ", ".join(t for t, _ in stale)
    print(f"FAILED: stale data (>7 days old) for: {tickers}")
    sys.exit(1)
else:
    print("Check passed: no stale tickers")
con.close()