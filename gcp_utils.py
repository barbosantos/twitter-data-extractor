import logging
import sys
import os

from google.cloud.exceptions import NotFound
from google.cloud import bigquery, storage, secretmanager

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


dataset_location = "europe-north1"


def dataset_exists(client, dataset_ref):
    try:
        client.get_dataset(dataset_ref)
        return True
    except NotFound:
        return False


def upload_to_bigquery_from_dataframe(df, table_nm, dataset_nm, schema):
    try:
        client = bigquery.Client()

        dataset = bigquery.Dataset("{}.{}".format(client.project, dataset_nm))
        dataset.location = dataset_location
        if not dataset_exists(client, dataset):
            dataset = client.create_dataset(dataset)  # Make an API request.
            logger.info(
                "Created dataset {}.{}".format(client.project, dataset.dataset_id)
            )

        table_id = "{}.{}".format(dataset.dataset_id, table_nm)

        job_config = bigquery.LoadJobConfig(schema=schema)
        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        # Wait for the load job to complete
        job.result()
        logger.info("Uploading %s completed", table_id)
        return "Uploading {} completed".format(table_id)
    except Exception as e:
        logger.exception(e)
        logger.error("Uploading %s failed!", table_id)
        return "Uploading {} failed!".format(table_id)


def access_secret_version(project_id, secret_id, version_id="latest"):
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(request={"name": name})
    # WARNING: Do not print the secret in a production environment - this
    # snippet is showing how to access the secret material.
    payload = response.payload.data.decode("UTF-8")
    return payload


def upload_file_to_cloud_storage(bucket_name, file_path, filename):
    logger.info("Uploading file to cloud storage...")
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(filename)
    blob.upload_from_filename(os.path.join(file_path, filename))


def upload_from_cloud_storage_to_bq(bucket_name, filename, schema_bq):
    logger.info("Uploading file to bigquery...")
    # Construct a BigQuery client object.
    client = bigquery.Client()

    table_id = "ikea-data.twitter.ikea_recent_batch"

    job_config = bigquery.LoadJobConfig(
        schema=schema_bq,
        skip_leading_rows=1,
        # The source format defaults to CSV, so the line below is optional.
        source_format=bigquery.SourceFormat.CSV,
    )
    uri = "gs://{}/{}".format(bucket_name, filename)

    load_job = client.load_table_from_uri(
        uri, table_id, job_config=job_config
    )  # Make an API request.

    load_job.result()  # Waits for the job to complete.
    logger.info("Data uploaded to bigquery")
