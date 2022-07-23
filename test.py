# Importing required libraries
import boto3
import twitter


twt_api = twitter.Api(consumer_key='', consumer_secret='', access_token_key='', access_token_secret='')

aws_api = boto3.client(service_name ='comprehend', aws_access_key_id = '', aws_secret_access_key = '', region_name = '')
aws_api = boto3.client(service_name ='s3', aws_access_key_id = '', aws_secret_access_key = '', region_name = '')