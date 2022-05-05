# twitter-data-extractor

## Introduction

The goal of this project is to extract data from the Twitter API that talks about IKEA.
To start of, it's necessary to create a Twitter developer account to get credentials to access the API. In this project, the "Essential" level access is being used, and the version of the API is v2.

## Methodology

The programming language used in this project is Python and the cloud platform is Google Cloud (GCP). To extract the data from Twitter API, the Tweepy library has being used. The API credentials are stored and fetched from GCP Secrets Manager service. So far, batch data extraction is being implemented, more especifically, we extract all tweets mentioning IKEA, from each previous day, using the "search recent" endpoint.
The data extracted is saved as a CSV file, and uploaded to a google cloud storage bucket. From there, the data is sent to Bigquery for enabling a better analysis.
The code is executed in a container running in Kubernetes (pod). The code is scheduled to run every day, as a cronjob, so that we can keep fetching data continuously. 

For a simple CI/CD, I have used Cloud build to build and deploy the container. The building process is triggered when the master branch is modified. Below is a diagram summing up the process:


![alt text](https://github.com/barbosantos/twitter-data-extractor/blob/main/diagram.png?raw=true)
