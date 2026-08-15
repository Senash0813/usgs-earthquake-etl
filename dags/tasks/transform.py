from datetime import datetime,timezone
from google.cloud import storage
import json
import logging

logger = logging.getLogger(__name__)

def transform_data(ti):
    """
    Transform the extracted data.

    """
    passed_bucket = ti.xcom_pull(task_ids="load_data_to_gcs")
    passed_blob = passed_bucket["blob_name"]
    passed_bucket_name = passed_bucket["bucket_name"]

    client = storage.Client()
    bucket = client.bucket(passed_bucket_name)
    blob = bucket.blob(passed_blob)

    data = blob.download_as_text()

    earthquakes = json.loads(data)

    flattened_data = flatten_earthquake_data(earthquakes)
    transformed_path = "/opt/airflow/data/flattened_data.ndjson"
    with open(transformed_path, "w") as f:
        for row in flattened_data:
            f.write(json.dumps(row) + "\n")
    logger.info(f"Transformed data saved to {transformed_path}")
    logger.info(f"Number of records transformed: {len(flattened_data)}")

    return {"transformed_path": transformed_path}




def epoch_ms_to_iso(epoch_ms):
    """
    Convert an epoch-millisecond timestamp to an ISO 8601 UTC string.

    """
    if epoch_ms is None:
        return None
    return datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc).isoformat()


def flatten_earthquake_data(earthquakes):
    """
    Flatten the earthquake data into a list of dictionaries.

    """
    rows = []
    for event in earthquakes["features"]:
        properties = event["properties"]
        geometry = event["geometry"]
        coordinates = geometry["coordinates"] if geometry else [None, None, None]
        rows.append({
            "id": event["id"],
            "magnitude": properties.get("mag"),
            "mag_type": properties.get("magType"),
            "place": properties.get("place"),
            "event_time": epoch_ms_to_iso(properties.get("time")),
            "updated_time": epoch_ms_to_iso(properties.get("updated")),
            "longitude": coordinates[0],
            "latitude": coordinates[1],
            "depth_km": coordinates[2],
            "event_type": properties.get("type"),
            "alert": properties.get("alert"),
            "status": properties.get("status"),
            "tsunami": properties.get("tsunami"),
            "significance": properties.get("sig"),
            "network": properties.get("net"),
            "felt_reports": properties.get("felt"),
            "community_determined_intensity": properties.get("cdi"),
            "modified_mercalli_intensity": properties.get("mmi"),
            "url": properties.get("url"),
        })

    return rows