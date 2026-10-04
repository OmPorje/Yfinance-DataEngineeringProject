
# 📈 Stock Market ETL Pipeline

An end-to-end **Data Engineering pipeline** that extracts daily stock market data from Yahoo Finance, performs automated cleaning and feature engineering, loads data into a DuckDB warehouse using idempotent upserts, validates data quality, and orchestrates the workflow with Apache Airflow running in Docker.

## 🚀 Key Features

- Incremental data extraction using watermark tracking
- Automated ETL orchestration with Apache Airflow
- Data warehouse loading with DuckDB
- Idempotent upserts for safe reprocessing
- Automated data quality validation
- Dockerized deployment
- Time-series feature engineering for stock analytics
- Production-style pipeline architecture

---

## 🛠️ Tech Stack

| Category | Technology |
|-----------|------------|
| Programming | Python |
| Data Source | Yahoo Finance (yfinance) |
| Storage Layer | Parquet |
| Data Warehouse | DuckDB |
| Processing | Pandas |
| Orchestration | Apache Airflow |
| Containerization | Docker |
| Message Broker | Redis |
| Metadata Database | PostgreSQL |

---

## 🏗️ Pipeline Architecture

```text
                    ┌─────────────────┐
                    │ Yahoo Finance   │
                    │   (yfinance)    │
                    └────────┬────────┘
                             │
                             ▼
                  ┌────────────────────┐
                  │      Extract       │
                  │ Incremental Pull   │
                  │ Watermark Tracking │
                  └────────┬───────────┘
                           │
                           ▼
                  ┌────────────────────┐
                  │    Raw Parquet     │
                  │   Bronze Layer     │
                  └────────┬───────────┘
                           │
                           ▼
                  ┌────────────────────┐
                  │     Transform      │
                  │ Data Cleaning      │
                  │ Feature Engineering│
                  └────────┬───────────┘
                           │
                           ▼
                  ┌────────────────────┐
                  │       DuckDB       │
                  │   Data Warehouse   │
                  └────────┬───────────┘
                           │
                           ▼
                  ┌────────────────────┐
                  │ Quality Validation │
                  │ Nulls, Duplicates  │
                  │ Bad Prices, Stale  │
                  └────────┬───────────┘
                           │
                           ▼
                  ┌────────────────────┐
                  │ Apache Airflow DAG │
                  │ Scheduled Weekdays │
                  └────────────────────┘
```

### Airflow Workflow

```text
extract
   │
   ▼
transform
   │
   ▼
quality_checks
```

**Schedule:** Weekdays at 10:00 PM UTC

---

## 💡 Design Decisions

### Watermark-Based Incremental Extraction

Instead of reprocessing historical data on every run, the pipeline tracks the latest successfully extracted date for each ticker in `watermark.json`.

Benefits:

- Faster execution
- Reduced API calls
- Lower processing costs
- No unnecessary reprocessing

The watermark is updated only after successful writes, ensuring failed runs never skip data.

---

### Idempotent Upserts

Data is loaded into DuckDB using:

```sql
INSERT ... ON CONFLICT (ticker, date)
DO UPDATE
```

Benefits:

- Safe reruns
- No duplicate records
- Easy recovery after failures
- Production-grade loading strategy

---

### Automated Data Quality Checks

Every pipeline run validates:

- Required field null checks
- Duplicate `(ticker, date)` records
- Invalid price relationships (`low > high`)
- Stale ticker detection
- Data freshness checks

Any validation failure causes the Airflow DAG to fail immediately, preventing bad data from reaching downstream consumers.

---

### Dockerized Airflow Deployment

Apache Airflow is deployed using Docker Compose with:

- Scheduler
- Worker
- DAG Processor
- Webserver
- PostgreSQL
- Redis

Project dependencies are baked into a custom Docker image, ensuring consistent execution across environments.

---

## 📂 Project Structure

```text
stock-pipeline/
├── config.py
├── src/
│   ├── extract.py
│   ├── transform.py
│   └── quality_checks.py
├── data/
│   ├── raw/
│   └── watermark.json
├── requirements.txt
└── warehouse.duckdb

airflow-docker/
├── docker-compose.yaml
├── Dockerfile
├── .env
└── dags/
    └── stock_pipeline_dag.py
```

---

## ▶️ Running the Project

### Run ETL Locally

```bash
cd stock-pipeline

pip install -r requirements.txt

python -m src.extract
python -m src.transform
python -m src.quality_checks
```

### Run with Airflow

```bash
cd airflow-docker

docker compose build
docker compose up -d
```

Access Airflow:

```text
http://localhost:8080
```

Default credentials:

```text
Username: airflow
Password: airflow
```

Enable the `stock_pipeline` DAG and either trigger it manually or allow it to run on its scheduled cadence.

---

## 📊 What This Project Demonstrates

### Data Engineering Concepts

- Incremental ETL pipelines
- Watermark processing
- Data warehouse design
- Idempotent loading
- Data quality monitoring
- Workflow orchestration
- Docker containerization
- Batch processing architecture

### Real-World Challenges Solved

- API reliability issues
- TLS connectivity failures
- Schema drift management
- Duplicate prevention
- Data corruption safeguards
- Container dependency isolation

---

## 🔮 Future Enhancements

- Replace DuckDB with PostgreSQL or Snowflake
- Add Streamlit analytics dashboard
- Integrate Slack or email alerts
- Add Great Expectations for advanced data validation
- Implement Kafka-based streaming ingestion
- Deploy using Kubernetes
- Add CI/CD with GitHub Actions

---

## 📌 Key Takeaway

This project demonstrates how to build a production-style ETL pipeline that is reliable, scalable, observable, and capable of handling real-world data engineering challenges such as incremental loading, data quality enforcement, orchestration, and failure recovery.
