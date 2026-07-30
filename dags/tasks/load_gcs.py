from google.cloud import storage

def get_saved_date(bucket_name, blob_name):
    """
    Get the last saved date from a GCS bucket.

    """

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    if blob.exists():
        return blob.download_as_text()
    else:
        return '2026-04-01'