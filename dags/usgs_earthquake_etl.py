from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from tasks.extract import extract_data

with DAG(
    dag_id="usgs_earthquake_etl",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:

    extract_usgs_data = PythonOperator(
        task_id="extract_api_data",
        python_callable=extract_data,
        op_kwargs={
            "startdate":"{{data_interval_start}}",
            "enddate": "{{data_interval_end}}"
        }
    )