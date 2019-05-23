import os
import sys
from tweepy import API
from tweepy import OAuthHandler

def get_twitter_auth():
    try:
        consumer_key = os.environ[]
        consumer_secret = os.environ[]
        access_token = os.environ[]
        access_secret = os.environ[]
    except KeyError:
        sys.stderr.write("TWITTER_* environment variables not set\n")
        sys.exit(1)
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)

def get_twitter_client():
    auth = get_twitter_auth()
    client = API(auth)
    return client
