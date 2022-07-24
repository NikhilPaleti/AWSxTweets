# Importing required libraries
import json
import boto3
import config
import twitter
import requests

# Config.py file structure as used: (It has been gitignored tf)
# twitter_access_token_secret = ''
# twitter_access_token_key = ''
# twitter_consumer_secret = ''
# twitter_consumer_key = ''
# twitter_bearer_token = ''

# aws_access_key_id = ''
# aws_secret_access_key = ''


twt_api = twitter.Api(consumer_key=config.twitter_consumer_key, consumer_secret=config.twitter_consumer_secret, access_token_key=config.twitter_access_token_key, access_token_secret=config.twitter_access_token_secret)

aws_api_comprehend = boto3.client(service_name = 'comprehend', aws_access_key_id = config.aws_access_key_id, aws_secret_access_key = config.aws_secret_access_key, region_name = 'us-east-1')
aws_api_s3 = boto3.client(service_name = 's3', aws_access_key_id = config.aws_access_key_id, aws_secret_access_key = config.aws_secret_access_key, region_name = 'us-east-1')

# Headers/Parameters for the request
headers = {
        'Authorization': 'Bearer {}'.format(config.twitter_bearer_token),
    }

params = (
    ('tweet.fields', 'context_annotations'),
)
payload = {
    'add':[
        {
            'value': 'Google'
        }
    ]
}
response = requests.post('https://api.twitter.com/2/tweets/search/stream/rules', headers=headers, json=payload)

if response.status_code == 201:
    print('Response: {}'.format(response.text))
else:
    print('Filter Creation Error: (HTTP Error {}) {}'.format(response.status_code, response.text))
