from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.standard.operators.empty import EmptyOperator
from datetime import datetime
from tasks.extract import extract_data
from tasks.load_gcs import save_data_to_gcs
from tasks.transform import transform_data
from tasks.load_bigquery import load_data_to_bigquery

with DAG(
    dag_id="usgs_earthquake_etl",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
) as dag:

    start_task = EmptyOperator(
        task_id="start_task"
    )

    extract_usgs_data = PythonOperator(
        task_id="extract_api_data",
        python_callable=extract_data,
    )

    load_data_to_gcs = PythonOperator(
        task_id="load_data_to_gcs",
        python_callable=save_data_to_gcs,
    )

    transform_raw_data = PythonOperator(
        task_id="transform_raw_data",
        python_callable=transform_data,
    ) 

    load_transformed_data_to_bigquery = PythonOperator(
        task_id="load_transformed_data_to_bigquery",
        python_callable=load_data_to_bigquery,
    )

    end_task = EmptyOperator(
        task_id="end_task"
    )



    start_task >> extract_usgs_data >> load_data_to_gcs >> transform_raw_data >> load_transformed_data_to_bigquery >> end_task