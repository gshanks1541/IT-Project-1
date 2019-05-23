import os
import sys
from tweepy import API
from tweepy import OAuthHandler

def get_twitter_auth():
    try:
        consumer_key = os.environ[nX7aJP4OUszK1dFgfm6BTZrXQ]
        consumer_secret = os.environ[s1C56X7kGeSrum8M6VXs8IdfTMOfKDmpQnJTDodLcCr6kbv938]
        access_token = os.environ[1128419970960936961-ocBanOhQYajRPcXQ3c1alFBf3BlanX]
        access_secret = os.environ[elHOFXT79tht3RmP1V90lW6bKJhHxNjHHHDolFVyfadTO]
    except KeyError:
        sys.stderr.write("TWITTER_* environment variables not set\n")
        sys.exit(1)
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)

def get_twitter_client():
    auth = get_twitter_auth()
    client = API(auth)
    return client
