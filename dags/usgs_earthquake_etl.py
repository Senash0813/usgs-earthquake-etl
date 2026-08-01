from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from tasks.extract import extract_data
from tasks.load_gcs import save_data_to_gcs

with DAG(
    dag_id="usgs_earthquake_etl",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
) as dag:

    extract_usgs_data = PythonOperator(
        task_id="extract_api_data",
        python_callable=extract_data,
    )

    load_data_to_gcs = PythonOperator(
        task_id="load_data_to_gcs",
        python_callable=save_data_to_gcs,
    )

    extract_usgs_data >> load_data_to_gcs