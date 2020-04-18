#!/usr/bin/python3
# -*- coding: utf-8 -*-

from twython import Twython
from secret import *

#This will get test information from file
def getTweetsTest():
    

def outputToTwitter(user, tweet):  
    twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    twitter.update_status(status= user + "\n" + tweet)
