# 📈 Stock Market ETL Pipeline

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Airflow](https://img.shields.io/badge/Apache%20Airflow-Orchestration-red)
![DuckDB](https://img.shields.io/badge/DuckDB-Data%20Warehouse-yellow)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)
![ETL](https://img.shields.io/badge/ETL-End--to--End-success)

An end-to-end **Data Engineering project** that automatically collects stock market data, transforms it into analytics-ready datasets, loads it into a data warehouse using **idempotent upserts**, validates data quality, and orchestrates the entire workflow with **Apache Airflow** running in Docker.

---

## 🚀 Project Highlights

✅ Incremental data extraction using watermark tracking

✅ Automated ETL pipeline with Apache Airflow

✅ Idempotent warehouse loading using DuckDB

✅ Data quality monitoring and validation

✅ Containerized deployment with Docker

✅ Production-style orchestration and scheduling

✅ Built using modern Data Engineering best practices

---

## 🎯 Business Problem

Financial data changes every trading day. Reprocessing historical data repeatedly is inefficient and expensive.

This project solves that challenge by:

- Extracting only new stock data using incremental loads
- Preventing duplicate records through upserts
- Automatically validating data quality
- Scheduling reliable daily executions
- Providing an analytics-ready warehouse for reporting and dashboards

---

## 🏗️ Architecture

```text
                    ┌─────────────────┐
                    │  Yahoo Finance  │
                    │    (yfinance)   │
                    └────────┬────────┘
                             │
                             ▼
                 ┌──────────────────────┐
                 │     Extract Layer    │
                 │ Incremental Pulls    │
                 │ Watermark Tracking   │
                 └────────┬─────────────┘
                          │
                          ▼
                 ┌──────────────────────┐
                 │   Raw Parquet Files  │
                 │    Bronze Layer      │
                 └────────┬─────────────┘
                          │
                          ▼
                 ┌──────────────────────┐
                 │   Transform Layer    │
                 │ Data Cleaning        │
                 │ Feature Engineering  │
                 │ Financial Metrics    │
                 └────────┬─────────────┘
                          │
                          ▼
                 ┌──────────────────────┐
                 │       DuckDB         │
                 │ Analytics Warehouse  │
                 └────────┬─────────────┘
                          │
                          ▼
                 ┌──────────────────────┐
                 │  Data Quality Checks │
                 │ Nulls, Duplicates    │
                 │ Staleness, Pricing   │
                 └────────┬─────────────┘
                          │
                          ▼
                 ┌──────────────────────┐
                 │   Apache Airflow     │
                 │ Daily Orchestration  │
                 └──────────────────────┘
```

### Airflow DAG

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

## 🛠️ Tech Stack

| Category | Tools |
|-----------|--------|
| Language | Python |
| Data Source | Yahoo Finance (yfinance) |
| Storage | Parquet |
| Warehouse | DuckDB |
| Data Processing | Pandas |
| Orchestration | Apache Airflow |
| Containerization | Docker |
| Messaging | Redis |
| Metadata DB | PostgreSQL |
| Scheduling | Airflow DAGs |
```

