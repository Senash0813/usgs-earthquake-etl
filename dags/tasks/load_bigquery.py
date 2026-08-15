from google.cloud import bigquery
import os
import logging

logger = logging.getLogger(__name__)

EARTHQUAKE_SCHEMA = [
    bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("magnitude", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("mag_type", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("place", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("event_time", "TIMESTAMP", mode="NULLABLE"),
    bigquery.SchemaField("updated_time", "TIMESTAMP", mode="NULLABLE"),
    bigquery.SchemaField("longitude", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("latitude", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("depth_km", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("event_type", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("alert", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("status", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("tsunami", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("significance", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("network", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("felt_reports", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("community_determined_intensity", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("modified_mercalli_intensity", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("url", "STRING", mode="NULLABLE"),
]


def load_data_to_bigquery(ti):
    """
    Load transformed data into BigQuery.

    """
    passed_data = ti.xcom_pull(task_ids="transform_raw_data")
    transformed_data_path = passed_data["transformed_path"]

    earthquake_table = "earthquake-etl-502816.usgs_earthquakes.earthquakes"

    client = bigquery.Client()
    logger.info(f"Loading data from {transformed_data_path} to BigQuery table {earthquake_table}")
    load_job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        schema=EARTHQUAKE_SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND
    )

    try:
        with open(transformed_data_path, "rb") as f:
            load_job = client.load_table_from_file(f, earthquake_table, job_config=load_job_config)

        load_job.result()  # Wait for the job to complete.
        logger.info(f"Data loaded into BigQuery table {earthquake_table} successfully.")
    except Exception as e:
        logger.error(f"Error occurred while loading data into BigQuery: {e}")
        raise

    os.remove(transformed_data_path)
    logger.info("Local transformed file removed after loading to BigQuery.")