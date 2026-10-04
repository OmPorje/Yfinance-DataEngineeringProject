from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id = 'stock_pipeline',
    schedule="0 22 * * 1-5",
    start_date=datetime(2026,1,1),
    catchup=False,
        
) as dag:
    extract = BashOperator(
        task_id="extract",
        bash_command = "cd /opt/airflow/projects/stock-pipeline && python -m src.extract",
    )
    transform = BashOperator(
        task_id="transform",
        bash_command = "cd /opt/airflow/projects/stock-pipeline && python -m src.transform",
    )
    quality_checks = BashOperator(
            task_id="quality_checks",
            bash_command = "cd /opt/airflow/projects/stock-pipeline && python -m src.quality_checks",
        )
    extract >> transform >> quality_checks