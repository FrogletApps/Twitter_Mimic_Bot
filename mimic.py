#!/usr/bin/python3
# -*- coding: utf-8 -*-

from twython import Twython
from secret import *

def getTweetsTest(fileName):
    '''
    This will get test information from file and put it into an array
    Parameters:
        filename (string):  Location of the test data file
    Returns:
        fileContents (string[]):  Array of words in file in lower case.
    '''
    with open(fileName, "r") as inputFile:
        return inputFile.read().lower().split() #Set to lower case and split into array

def outputToTwitter(user, tweet):  
    '''
    Post data to Twitter
    Parameters:
        user (string):  The username that is being impersonated
        tweet (string):  The tweet that has been generated
    '''
    twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    twitter.update_status(status= user + "\n" + tweet)

print("Original text:")
print(getTweetsTest("testData.txt"))
