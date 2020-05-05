from flask import Flask
import os, tweepy
from dotenv import load_dotenv
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from google.protobuf.json_format import MessageToJson


# Initialise Flask app
app = Flask(__name__)

# Instantiate Google cloud NL client
client = language.LanguageServiceClient()

# Fetch the service account key JSON file contents
cred = credentials.Certificate('keyfile.json')

# Initialise firebase app
firebase_admin.initialize_app(cred, {'databaseURL': os.getenv("FIREBASE_DB_URL")})
root = db.reference()


def send_to_nl_api(tweet):
    # Text to analyse
    document = types.Document(
        content=tweet.text,
        type=enums.Document.Type.PLAIN_TEXT
    )

    # Detects the sentiment of the text
    sentiment = MessageToJson(client.analyze_sentiment(document=document), preserving_proto_field_name=True)

    # Find entities in the text
    entities = MessageToJson(client.analyze_entities(document=document), preserving_proto_field_name=True)

    # Get tokens in the text
    tokens = MessageToJson(client.analyze_syntax(document=document), preserving_proto_field_name=True)

    id = tweet.id_str
    firebase_data = {
        'text': tweet.text,
        'user': tweet.user.screen_name,
        'user_time_zone': tweet.user.time_zone,
        'user_followers_count': tweet.user.followers_count,
        'hashtags': tweet.entities.get('hashtags'),
        'tokens': tokens,
        'score': sentiment,
        'magnitude': sentiment,
        'entities': entities
    }

    save_to_firebase(id, firebase_data)


def save_to_firebase(id, document):
    root.child('latest/{}'.format(id)).set(document)

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
            #pass
            send_to_nl_api(status)

# Create an object of the above inherited class
tweetStreamListener = TweetStreamListener()
tweetStream = tweepy.Stream(auth=api.auth, listener=tweetStreamListener)

# Add filter for tweets
tweetStream.filter(track=['coronavirus'])

@app.route('/')
def hello_world():
    return "Hello World!"