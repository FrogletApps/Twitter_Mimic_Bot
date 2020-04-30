#!/usr/bin/python3
# -*- coding: utf-8 -*-

from json import dump, load
from os.path import join
from secretKeys import *
from sys import path
from twython import Twython

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

last_id = 0
with open(join(path[0], 'last_id.json'), 'r') as storeFile:
    last_id = load(storeFile)
    print(last_id)

search = twitter.search(q="@twimimicbot", since_id=last_id, count=1, tweet_mode='extended')

username = ""
tweet_id = 0
for tweetData in search["statuses"]:
    tweet = tweetData["full_text"]
    tweet_id = tweetData["id"]
    for word in tweet.split():
        if word[0] == "@" and "@twimimicbot" not in word:
            #We could go through the whole tweet and do multiple, but I don't want to spam anyone
            username = word
            break

if username != "" and tweet_id != 0:
    print(username)
    print(tweet_id)
    tweetNo = 0
    try:
        tweetNo = len(twitter.get_user_timeline(screen_name=username, count=200, include_rts=False))
    except: 
        pass
    if tweetNo > 10:
        #Found some tweets, this means we can mimic it
        print(":)")
    else:
        #No tweets or not enough tweets (not including retweets), cannot mimic this account
        print(":(")

    #Write the ID to file so we know where to search from next time
    try:
        last_id = search["statuses"][0]["id"]
        last_id = 0 
        with open(join(path[0], 'last_id.json'), 'w') as storeFile:
            dump(last_id, storeFile)
    except:
        pass
else:
    print("No mentions found")


