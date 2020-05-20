from flask import Flask
import os, tweepy, requests
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


# Initialise Flask app
app = Flask(__name__)

# Fetch the service account key JSON file contents
cred = credentials.Certificate('keyfile.json')

# Initialise firebase app
firebase_admin.initialize_app(cred, {'databaseURL': os.getenv("FIREBASE_DB_URL")})
root = db.reference()


def send_to_nl_api(tweet):
    # Construct a request body
    data = {
        'document': {
            'type': 'PLAIN_TEXT',
            'content': tweet.text
        },
        'features': {
            'extractSyntax': True,
            'extractEntities': True,
            'extractDocumentSentiment': True
        }
    }

    response = requests.post(url=os.getenv('GOOGLE_NL_API_ENDPOINT'), json=data)
    if response.status_code == 200:
        response = response.json()
    else:
        print('NL API Error!')
        return

    id = tweet.id_str
    firebase_data = {
        'id': tweet.id_str,
        'text': tweet.text,
        'user': tweet.user.screen_name,
        'user_time_zone': tweet.user.time_zone,
        'user_followers_count': tweet.user.followers_count,
        'hashtags': tweet.entities['hashtags'],
        'tokens': response['tokens'],
        'score': response['documentSentiment']['score'],
        'magnitude': response['documentSentiment']['magnitude'],
        'entities': response['entities']
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