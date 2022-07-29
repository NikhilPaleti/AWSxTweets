# Importing required libs 
import json
import boto3
import config
import twitter
import requests
import numpy as np
import matplotlib.pyplot as plt

# Config.py file structure as used: (It has been gitignored tf)
# twitter_access_token_secret = ''
# twitter_access_token_key = ''
# twitter_consumer_secret = ''
# twitter_consumer_key = ''
# twitter_bearer_token = ''

# aws_access_key_id = ''
# aws_secret_access_key = ''

# dynamodb_partition_key = ''
# dynamodb_table_name = ''


twt_api = twitter.Api(consumer_key=config.twitter_consumer_key, consumer_secret=config.twitter_consumer_secret, access_token_key=config.twitter_access_token_key, access_token_secret=config.twitter_access_token_secret)

aws_api_comprehend = boto3.client(service_name = 'comprehend', aws_access_key_id = config.aws_access_key_id, aws_secret_access_key = config.aws_secret_access_key, region_name = 'us-east-1')
# aws_api_dynamo = boto3.client(service_name = 'dynamodb', aws_access_key_id = config.aws_access_key_id, aws_secret_access_key = config.aws_secret_access_key, region_name = 'us-east-1')
aws_api_dynamo = boto3.resource('dynamodb', aws_access_key_id = config.aws_access_key_id, aws_secret_access_key = config.aws_secret_access_key, region_name = 'us-east-1')
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

#Some pre-processing for the graphs 
pos_list = []
neg_list = []
neu_list = []
mix_list = []
id_list = []


fig= plt.figure()
# ax1 = fig.add_subplot(1,1,1)
plt.ion()

# def animate():
#     ax1.clear()
#     ax1.plot(pos_list, color = "green")
#     ax1.plot(neg_list, color = "red")
#     ax1.plot(neu_list, color = "blue")
#     ax1.plot(mix_list, color = "black")



def stream_connect(bearer_token):
    
    response = requests.get('https://api.twitter.com/2/tweets/search/stream', headers=headers, stream=True)
    
    for new_line in response.iter_lines():        
        if (new_line):
            tweet = json.loads(new_line)
            tweet_id = tweet['data']['id']
            # id_list.append(tweet_id)
            text = tweet['data']['text']
            tweet_sentiment = aws_api_comprehend.detect_sentiment(Text = text, LanguageCode = 'en')
            sentiment = tweet_sentiment['Sentiment']
            sentiment_score = tweet_sentiment['SentimentScore']
            for score in sentiment_score:
                sentiment_score[score] = round(sentiment_score[score], 3)
            
            global pos_list
            global neg_list
            global neu_list
            global mix_list
            
            
            pos_list.append(sentiment_score['Positive']) 
            neg_list.append(sentiment_score['Negative'])
            neu_list.append(sentiment_score['Neutral'])
            mix_list.append(sentiment_score['Mixed'])    
            
            
            if (len(mix_list)>15):
                no = len(mix_list)-15
                mix_list = mix_list[no:]
                pos_list = pos_list[no:]
                neg_list = neg_list[no:]   
                neu_list = neu_list[no:] 
                plt.pause(0.1) 
                plt.cla()       
            
            # print('Tweet ID: ', tweet_id)
            # print('Tweet: ', text) 
            # print('Major Sentiment: ', sentiment)
            # print('Sentiments: ', sentiment_score)
            
            
            table = aws_api_dynamo.Table(config.dynamodb_table_name)
            cols = ["Tweet", "MainSentiment", "Breakdown"]

            response = table.put_item(
                Item = {
                    config.dynamodb_partition_key: str(tweet_id),
                    cols [0]: str(text),
                    cols [1]: str(sentiment) ,
                    cols [2]: str(sentiment_score) 
                }
            )
            
            
            plt.plot(pos_list, color = "green", label='Positive')
            plt.plot(neg_list, color = "red", label='Negative')
            plt.plot(neu_list, color = "blue", label='Neutral')
            plt.plot(mix_list, color = "green", label='Black')
            
            plt.legend()
            
            # time.sleep(0.2)
            plt.show()
            # print (len(mix_list))

# Final code to kick-off everything
 
BEARER_TOKEN = config.twitter_bearer_token
while True:
    stream_connect(BEARER_TOKEN)


#Experimenting with the upload to s3/Dynamo
# bucket = 'letmepretendbucket'
# filename = 'file.csv'

# aws_api_s3.Object(bucket, filename).delete()
# aws_api_s3.upload_file(Filename = filename, Bucket= bucket, Key = filename)