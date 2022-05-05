import csv
import datetime
import logging
import os
import sys
import time

import tweepy

from gcp_utils import upload_file_to_cloud_storage, upload_from_cloud_storage_to_bq
from settings import (
    twitter_api_bearer_token,
    bucket_name,
    twitter_csv_file_path,
    filename,
    SCHEMA_TWITTER_DATA,
)

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    # Using Twitter api recent search
    end_time = datetime.datetime.now(datetime.timezone.utc)
    # Will fetch data from previous day
    start_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
        days=1
    )

    logging.info(
        "Starting batch extraction from {} to {}...".format(start_time, end_time)
    )

    twitter_api_bearer_token = twitter_api_bearer_token
    client = tweepy.Client(bearer_token=twitter_api_bearer_token)

    # Search query containing Ikea, language english and is not a retweet
    query = "IKEA lang:en -is:retweet"

    # Using Twitter api recent search:
    # https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-recent
    response = client.search_recent_tweets(
        query=query,
        tweet_fields=["lang", "created_at"],
        start_time=start_time,
        end_time=end_time,
        max_results=100,
    )

    if response.data:
        # Flagging to true to guarantee getting the existing data
        next_token = True

    while next_token is not None:
        # csv file will be created from twitter_data list
        twitter_data = []
        for tweet in response.data:
            # cleaning up text field
            text = tweet.text.replace("\r", " ")
            text = tweet.text.replace("\n", " ")
            twitter_data.append(
                [
                    tweet.id,
                    text,
                    tweet.created_at.strftime("%Y-%m-%d %H:%M:%S").strip(),
                ]
            )

        with open(os.path.join(twitter_csv_file_path, filename), "a") as f:
            # using csv.writer method from CSV package
            write = csv.writer(f)
            write.writerows(twitter_data)

        # sleep for two seconds to avoid going over the API requests limits
        time.sleep(2)

        # getting next token for pagination
        try:
            next_token = response.meta["next_token"]
            response = client.search_recent_tweets(
                query=query,
                tweet_fields=["lang", "created_at"],
                start_time=start_time,
                end_time=end_time,
                max_results=100,
                next_token=next_token,
            )
        except KeyError:
            logger.info("Next token not available anymore for pagination")
            next_token = None

    # upload file to cloud storage and then to bigquery
    upload_file_to_cloud_storage(bucket_name, twitter_csv_file_path, filename)
    upload_from_cloud_storage_to_bq(bucket_name, filename, SCHEMA_TWITTER_DATA)
    # remove file after being uploaded to cloud
    os.remove(os.path.join(twitter_csv_file_path, filename))
