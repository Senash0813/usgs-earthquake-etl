from google.cloud import storage
import os
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

def get_saved_date(bucket_name, blob_name):
    """
    Get the last saved date from a GCS bucket.

    """

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    if blob.exists():
        logger.info(f"Found existing blob: {blob_name}")
        return blob.download_as_text()
    else:
        return '2026-08-12'



def save_data_to_gcs(ti):
    """
    Save data to a GCS bucket.

    """
    passed_data = ti.xcom_pull(task_ids="extract_api_data")
    local_file_path = passed_data["local_file_path"]
    max_date = passed_data["max_date"]

    bucket_name = "earthquake-etl-extracted-data"
    date_time = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    blob_name = f"extracted_data_{date_time}.json"

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    logger.info(f"Uploading data to GCS bucket: {bucket_name}, blob: {blob_name}")
    try:
        blob.upload_from_filename(local_file_path)
    except Exception as e:
        logger.error(f"Error occurred while uploading data to GCS: {e}")
        raise
    logger.info(f"Data uploaded to GCS bucket!")

    os.remove(local_file_path)
    logger.info("Local file removed after upload.")

    save_max_date(max_date) #function call to save the max date to GCS

    return{"blob_name": blob_name, "bucket_name": bucket_name}


def save_max_date(max_date):
    """
    Save the max date to a GCS bucket.

    """
    bucket_name = "earthquake-etl-bookmark-1"
    blob_name = "last_saved_date.txt"

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # incase max_date is None, we should not attempt to save it to GCS 
    if max_date is None:
        logger.warning("Max date is None, skipping save to GCS.")
        return
    else:
        logger.info(f"Saving max date to GCS bucket: {bucket_name}, blob: {blob_name}")
        blob.upload_from_string(max_date)
        logger.info(f"Max date saved to GCS bucket!")

