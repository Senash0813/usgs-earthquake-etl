import requests
import logging
from tasks.load_gcs import get_saved_date
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

def extract_data():
    """
    Extract data from the USGS API endpoint.

    """
    bucket_name = "earthquake-etl-bookmark-1"
    blob_name = "last_saved_date.txt"

    target = "/opt/airflow/data/local_copy.json"

    # Get the last saved date from GCS
    startdate = get_saved_date(bucket_name, blob_name)
    enddate = datetime.today().strftime('%Y-%m-%d')

    resp = requests.get(
        "https://earthquake.usgs.gov/fdsnws/event/1/query",
        params={
            "format": "geojson",
            "starttime": startdate,
            "endtime": enddate,
        },
        timeout=30
    )

    # Handle response status codes
    if resp.status_code == 200:
        logger.info(f"Request successful: {resp.status_code}")
    elif resp.status_code == 204:
        logger.info(f"No Content: The request was successful but no data was returned. {resp.status_code}")

    # Handle error status codes
    if resp.status_code == 400:
        logger.error(f"Bad Request: The request was invalid or malformed. {resp.status_code}")
    elif resp.status_code == 404:
        logger.error(f"Not Found: No matching data was found. {resp.status_code}")
    elif resp.status_code == 500:
        logger.error(f"USGS Server Error: {resp.status_code}")
    elif resp.status_code == 503:
        logger.error(f"USGS Service temporarily unavailable: {resp.status_code}")


    resp.raise_for_status()

    earthquakes = resp.json()
    earth_dates = [p["properties"]["time"] for p in earthquakes["features"]]
    if earth_dates:
        max_date = max(earth_dates)/1000  # Convert milliseconds to seconds
        max_date_utc = datetime.fromtimestamp(max_date, tz=timezone.utc).strftime('%Y-%m-%d')
    else:
        max_date_utc = None

    # Save the response to a local file
    with open(target, "w") as f:
        f.write(resp.text)

    return {"max_date": max_date_utc, "local_file_path": target}

    
