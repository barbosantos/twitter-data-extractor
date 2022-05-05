import datetime
import json
import time
import logging
import sys

from google.cloud import pubsub_v1, secretmanager

# Google cloud project ID and pub/sub topic ID
project_id = "ikea-data"
topic_id = "twitter-data-dev"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)


def reformat_tweet(tweet):

    processed_doc = {
        "id": tweet["id"],
        "lang": tweet["lang"],
        "retweeted_id": tweet["retweeted_status"]["id"]
        if "retweeted_status" in tweet
        else None,
        "favorite_count": tweet["favorite_count"] if "favorite_count" in tweet else 0,
        "retweet_count": tweet["retweet_count"] if "retweet_count" in tweet else 0,
        "created_at": tweet["created_at"]
        # "created_at": time.mktime(
        #    time.strptime(tweet["created_at"], "%a %b %d %H:%M:%S +0000 %Y")
        #)
        # if "created_at" in tweet
        # else None,
    }

    if "extended_tweet" in tweet:
        processed_doc["text"] = tweet["extended_tweet"]["full_text"]
    elif "full_text" in tweet:
        processed_doc["text"] = tweet["full_text"]
    else:
        processed_doc["text"] = tweet["text"]

    return processed_doc


# Method to push messages to pubsub
def write_to_pubsub(data):
    logging.info("Publishing message to pub/sub topic {}".format(topic_id))
    try:
        publisher.publish(topic_path, data=json.dumps({
            "text": data["text"],
            "id": data["id"],
            "posted_at": datetime.datetime.fromtimestamp(data["created_at"]).strftime('%Y-%m-%d %H:%M:%S')
        }).encode("utf-8"), tweet_id=str(data["id"]).encode("utf-8"))
    except Exception as e:
        raise e


def access_secret_version(project_id, secret_id, version_id='latest'):
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()
    # Build the resource name of the secret version.
    name = client.secret_version_path(project_id, secret_id, version_id)
    # Access the secret version.
    response = client.access_secret_version(name)
    return response.payload.data.decode('UTF-8')
