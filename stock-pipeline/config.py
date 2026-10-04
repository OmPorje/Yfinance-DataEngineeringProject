from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
RAW_DIR = BASE_DIR/'data'/'raw'
DUCK_DB = BASE_DIR/'warehouse.duckdb'
RAW_DIR.mkdir(parents=True, exist_ok=True)