# Stock Market ETL Pipeline

An end-to-end data pipeline that extracts daily stock price data, cleans and
enriches it with financial metrics, loads it into a warehouse with idempotent
upserts, runs automated data quality checks, and is orchestrated on a
schedule with Apache Airflow in Docker.

## Architecture

```
yfinance API
      │
      ▼
 extract.py ──► data/raw/*.parquet        (bronze layer, incremental via watermark)
      │
      ▼
transform.py ──► clean → compute metrics → upsert into DuckDB
      │
      ▼
quality_checks.py ──► nulls / duplicates / bad prices / staleness (fails loudly)

Orchestrated by Airflow (Docker, Celery executor):
  extract >> transform >> quality_checks
  Scheduled: weekdays, 10pm UTC
```

## Why these design choices

**Watermark-based incremental extraction.** Instead of re-pulling a fixed
lookback window every run, `extract.py` tracks the last successfully
extracted date per ticker in `data/watermark.json` and only requests new
days from the API. The watermark only advances *after* a successful write,
so a failed run can't silently skip data on the next run.

**Idempotent upserts, not inserts.** `transform.py` loads into DuckDB using
`INSERT ... ON CONFLICT (ticker, date) DO UPDATE`, keyed on a composite
primary key. This means the pipeline can be re-run any number of times —
on a schedule, after a failure, or manually — without ever creating
duplicate rows or requiring a "wipe and reload."

**Fail-loud data quality gates.** `quality_checks.py` runs after every load
and checks for nulls in required fields, duplicate `(ticker, date)` pairs,
logically impossible prices (e.g. `low > high`), and stale tickers (no new
data in 7+ days). Any failure exits non-zero, so Airflow marks the pipeline
run as failed instead of letting bad data flow downstream unnoticed.

**Containerized orchestration with a custom image.** Airflow runs via
Docker Compose (Celery executor: scheduler, worker, DAG processor,
webserver, Postgres, Redis). Project dependencies (`yfinance`, `duckdb`,
etc.) are baked into a custom image via a `Dockerfile` rather than installed
ad hoc into a running container, so they survive restarts and rebuilds.

## Project structure

```
stock-pipeline/
├── config.py                 # tickers, paths, settings
├── src/
│   ├── extract.py            # incremental pull from yfinance -> raw parquet
│   ├── transform.py          # clean, compute metrics, upsert into DuckDB
│   └── quality_checks.py     # automated data quality gate
├── data/
│   ├── raw/                  # bronze layer: untouched daily pulls (parquet)
│   └── watermark.json        # per-ticker last-extracted-date tracker
├── requirements.txt
└── warehouse.duckdb          # created on first run

airflow-docker/
├── docker-compose.yaml       # Airflow (CeleryExecutor) + Postgres + Redis
├── Dockerfile                # bakes project dependencies into the Airflow image
├── .env                      # AIRFLOW_UID
└── dags/
    └── stock_pipeline_dag.py # extract >> transform >> quality_checks
```

## Running it locally

**1. Run the pipeline directly (no orchestration):**
```bash
cd stock-pipeline
pip install -r requirements.txt
python -m src.extract
python -m src.transform
python -m src.quality_checks
```

**2. Run it on a schedule with Airflow:**
```bash
cd airflow-docker
docker compose build      # builds the custom image with project dependencies
docker compose up -d
```
Open `http://localhost:8080` (default login: `airflow` / `airflow`), unpause
the `stock_pipeline` DAG, and trigger it manually or let it run on its
10pm UTC weekday schedule.

> Note: update the Windows host path in `docker-compose.yaml`'s volume mount
> and `PROJECT_DIR` in the DAG file to match your local `stock-pipeline`
> location before running.

## What this project demonstrates

- Incremental extraction with watermark/checkpoint tracking
- Idempotent loading via SQL upserts (safe re-runs, no duplicate data)
- Automated data quality gates that fail the pipeline rather than pass bad data downstream
- Per-group (per-ticker) time-series feature engineering with pandas (`groupby` + rolling windows)
- Containerized orchestration with Airflow, including a custom Docker image to permanently solve a dependency-isolation issue between the scheduler and worker containers
- Debugging real-world issues: API client TLS failures, schema drift between pipeline versions, column-order data corruption risk, and container filesystem isolation

## Possible extensions

- Swap DuckDB for Postgres or Snowflake
- Add a Streamlit dashboard reading from `warehouse.duckdb`
- Add Slack/email alerting on quality check failure
- Replace daily batch extraction with a Kafka-based intraday stream
