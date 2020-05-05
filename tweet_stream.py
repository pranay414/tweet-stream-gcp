import os, tweepy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

# Authentication with Twitter API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Inherit a class from StreamListener
class TweetStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        if(status.text[:2] != 'RT'):
            print(status.text)

# Create an object of the above inherited class
tweetStreamListener = TweetStreamListener()
tweetStream = tweepy.Stream(auth=api.auth, listener=tweetStreamListener)
tweetStream.filter(track=['coronavirus'])

