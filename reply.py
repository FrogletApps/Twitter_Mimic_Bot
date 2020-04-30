#!/usr/bin/python3
# -*- coding: utf-8 -*-

from mimic import *
from os.path import join
from secretKeys import *
from sys import path
from twython import Twython

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

lastId = 0
with open(join(path[0], 'last_id.txt'), 'r') as storeFile:
    lastId = storeFile.read()
    #print(lastId)

search = twitter.search(q="@twimimicbot", since_id=lastId, count=1, tweet_mode='extended')

username = ""
requestUser = ""
tweetId = 0
ownName = False
for tweetData in search["statuses"]:
    #print(tweetData)
    tweet = tweetData["full_text"]
    tweetId = tweetData["id"]
    requestUser = "@" + tweetData["user"]["screen_name"]
    for word in tweet.split():
        if word[0] == "@":
            #Check that it is not getting its own mention, but it will mimic itself if mentioned twice
            if word == "@twimimicbot" and ownName == False:
                countOwnName = True
            else:
                #We could go through the whole tweet and do multiple, but I don't want to spam anyone
                username = word
                break

if username != "" and tweetId != 0:
    #print(username)
    #print(tweetId)
    tweetNo = 0
    try:
        tweetNo = len(twitter.get_user_timeline(screen_name=username, count=200, include_rts=False))
    except: 
        pass
    if tweetNo > 10:
        #Found some tweets, this means we can mimic it
        calculateMimic(username, requestUser, tweetId)
    else:
        #Could not find enough tweets (not including retweets), cannot mimic this account
        twitter.update_status(status=requestUser + " Could not find enough tweets (not including retweets) to mimic " + username[1:], in_reply_to_status_id=tweetId)

    #Write the ID to file so we know where to search from next time
    with open(join(path[0], 'last_id.txt'), 'w') as storeFile:
        storeFile.write(str(tweetId))
#else:
    #print("No mentions found")


