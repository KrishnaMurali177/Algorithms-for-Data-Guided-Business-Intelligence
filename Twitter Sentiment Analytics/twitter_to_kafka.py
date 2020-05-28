import json
import time
from kafka import SimpleProducer, KafkaClient
import configparser
import tweepy

# Note: Some of the imports are external python libraries. They are installed on the current machine.
# If you are running multinode cluster, you have to make sure that these libraries
# and currect version of Python is installed on all the worker nodes.

class TweeterStreamProducer(tweepy.StreamListener):
    """ A class to read the tweet stream and push it to Kafka"""

    def __init__(self,api):
        self.api = api
        super(tweepy.StreamListener, self).__init__()
        client = KafkaClient("localhost:9092")
        self.producer = SimpleProducer(client, async = True,
                          batch_send_every_n = 1000,
                          batch_send_every_t = 10)

    def on_status(self, status):
        """ This method is called whenever new data arrives from live stream.
        We asynchronously push this data to kafka queue"""
        msg =  status.text.encode('utf-8')
        #print(msg)
        try:
            self.producer.send_messages('twitterstream', msg)
        except Exception as e:
            print(e)
            return False
        return True

    def on_error(self, status_code):
        print("Error received in kafka producer")
        return True # Don't kill the stream

    def on_timeout(self):
        return True # Don't kill the stream


if __name__ == '__main__':
    # To simulate twitter stream, we will load tweets from a file in a streaming fashion
    config = configparser.ConfigParser()
    config.read('twitter.txt')
    consumer_key = config['DEFAULT']['ConsumerKey']
    consumer_secret = config['DEFAULT']['ConsumerSecretKey']
    access_key = config['DEFAULT']['AccessToken']
    access_secret = config['DEFAULT']['AccessTokenSecret']

    # Create OAuth
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    # Create stream and bind the listener to it
    stream = tweepy.Stream(auth, listener = TweeterStreamProducer(api))

    #Custom Filter rules pull all traffic for those filters in real time.
    stream.filter(track = ['love', 'hate'], languages = ['en'])
    #stream.filter(locations=[-180,-90,180,90], languages = ['en'])
