import datetime
import os

from google.cloud import bigquery

from gcp_utils import access_secret_version

twitter_api_bearer_token = access_secret_version(
    "ikea-data", "twitter-api-bearer-token"
)


SCHEMA_TWITTER_DATA = [
    bigquery.SchemaField(name="ID", field_type="INTEGER", mode="NULLABLE"),
    bigquery.SchemaField(name="TEXT", field_type="STRING", mode="NULLABLE"),
    bigquery.SchemaField(name="GENERATED_AT", field_type="TIMESTAMP", mode="NULLABLE"),
]

export_file_date = (datetime.datetime.today() - datetime.timedelta(1)).strftime(
    "%Y-%m-%d"
)

twitter_csv_file_path = "twitter_data"
filename = "twitter_data_{}.csv".format(export_file_date)
if not os.path.exists(twitter_csv_file_path):
    os.makedirs(twitter_csv_file_path)

# cloud storage bucket that will store csv files with twitter data
bucket_name = "dep_twitter_data"
