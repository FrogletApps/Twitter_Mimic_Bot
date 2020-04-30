#!/usr/bin/python3
# -*- coding: utf-8 -*-

from csv import reader
from html import unescape
from itertools import groupby
from os.path import join
from pickle import dump, load
from random import choice, randint, random
from re import sub
from secretKeys import *
from sys import path
from time import time
from twython import Twython

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

#Insert a Twitter username here (leave this blank to randomly pick someone to mimic)
userToMimic = ""

"""
def getTweetsTest(fileName):
    '''
    This will get test information from file and put it into a list (in lower case)
    Parameters:
        filename (string):  Location of the test data file
    Returns:
        wordList (string[]):  List of words in file in lower case.
    '''
    with open(join(path[0], fileName), "r") as inputFile:
        return inputFile.read().lower().split() #Set to lower case and split into list of words

def printDictionary(dictionary):
    '''
    Print a dictionary (from: https://www.codevscolor.com/python-print-key-value-dictionary/)
    Parameters:
        dictionary (dict):  Dictionary to print
    '''
    for item in dictionary:
        print("Key:{}, Value:{}".format(item, dictionary[item]))

def print2dList(listToPrint):
    '''
    Print a 2D list
    Parameters:
        listToPrint ([]):  List to print
    '''
    for x in listToPrint:
        print(x)
"""

def readTweetsByUser(username, limit, maxId=0):
    '''
    This will get tweets from Twitter and put them into an list of tweets
    Parameters:
        username (string):  The user whose tweets you want to receive
        limit (int):  The number of tweets you want to receive (this is a maximum number, and not necessarily the number you will get because this includes retweets which are not shown)
        maxID (int):  Get tweets with an ID less than this (tweets older than this tweet)
    Returns:
        tweetList (string[]):  List of tweets
    '''
    tweetList = []
    atUsername = "@" + username

    #200 is the maximum you can get from one request
    if limit >= 200:
        tweetsNo = 200
    else:
        tweetsNo = limit
    limit = limit - tweetsNo #Calculate the number of extra tweets that you still need to get

    if maxId != 0:
        dataList = twitter.get_user_timeline(screen_name=atUsername, count=tweetsNo, max_id=maxId, include_rts=False, tweet_mode='extended')
    else:
        dataList = twitter.get_user_timeline(screen_name=atUsername, count=tweetsNo, include_rts=False, tweet_mode='extended')

    tweetId = 0
    for tweetData in dataList:
        #print(tweetData)
        #print()
        mediaType = ""
        mediaURL = ""
        if "extended_entities" in tweetData:
            if "media" in tweetData["extended_entities"]:
                if "type" in tweetData["extended_entities"]["media"][0]:
                    mediaType = tweetData["extended_entities"]["media"][0]["type"]
                    mediaURL = tweetData["extended_entities"]["media"][0]["media_url_https"]
        tweetText = tweetData["full_text"] + " <eot>" #Add a marker to show the End Of Tweet
        tweetId = tweetData["id_str"]
        #print(tweetText)
        #Collect Tweet, media type, and the media URL
        tweet = [tweetText, mediaType, mediaURL]
        #print(tweet)
        tweetList.append(tweet)

    if limit > 0:
        extraDataList = readTweetsByUser(username, limit, tweetId)
        for extraTweet in extraDataList:
            tweetList.append(extraTweet)

    return tweetList

def getInputTweetsStats(tweetList):
    '''
    This will calculate statistics about the tweets
    Parameters:
        tweetList (string[]):  List of tweets
    Returns:
        outputStats (dict):  Dictionary of statistics
    '''
    wordList = []
    stats = []
    outputStats = {}
    tweetNo = len(tweetList)

    for miniTweetData in tweetList:
        tweetStats = []
        tweet = miniTweetData[0]
        wordList = tweet.split()
        #print(tweet)

        #Calculate the length of a tweet
        tweetLength = len(wordList)
        tweetStats.append(tweetLength)

        #Amount of end of phrase punctuation in a tweet
        punctCount = 0
        for word in wordList:
            if word[-1:] in ["!", "?" ,"."]:
                punctCount += 1
        tweetStats.append(punctCount)
        #print(punctCount)

        #Number of tweets which start with a capital letter
        upperCount = 0
        if tweet[0].isupper():
            upperCount += 1
        tweetStats.append(upperCount)

        #Check whether an image has been attached to the tweet
        image = 0
        if miniTweetData[1] == "photo":
            image = 1            
        tweetStats.append(image)

        stats.append(tweetStats)

    totalWords = 0
    totalPunct = 0
    totalUpper = 0
    totalImages = 0
    countTweets = 0
    for tweetStats in stats:
        #print(tweetStats)
        totalWords += tweetStats[0]
        totalPunct += tweetStats[1]
        totalUpper += tweetStats[2]
        totalImages += tweetStats[3]
        countTweets += 1

    averageWords = round(totalWords/countTweets)
    averagePunct = totalPunct/countTweets
    averageUpper = totalUpper/countTweets
    averageImages = totalImages/countTweets
    outputStats["avgWords"] = averageWords
    outputStats["avgPunct"] = averagePunct
    outputStats["avgUpper"] = averageUpper
    outputStats["avgImg"] = averageImages
    #print(outputStats)

    return outputStats

def splitIntoWords(tweetList):
    '''
    This will get the tweets and split them up into individual words (and remove certain unwanted elements like @usernames and hyperlinks)
    Parameters:
        tweetList (string[]):  List of tweets
    Returns:
        wordList (string[]):  List of words from the user's tweets
        firstWordList (string[]):  List of the first word used in a user's tweets
    '''
    wordList = []
    firstWordList = []
    for tweet in tweetList:
        firstWord = True
        #print(tweet)
        #print()
        words = tweet[0].split()
        for word in words:
            #Remove @Users and web links
            if "@" not in word and "http" not in word:
                #Strip out double quotes and brackets
                word = sub("\"|“|”|\(|\)", "", word)
                wordList.append(word)
                if firstWord == True:
                    firstWordList.append(word)
                    firstWord = False

    return [wordList, firstWordList]

def createDictionary(wordList):
    '''
    This will put the data into two dictionaries
    Parameters:
        wordList (string[]):  List of words
    Returns:
        integerToString (dict):  Dictionary arranged by integers and storing strings
        stringToInteger (dict):  Dictionary arranged by strings and storing integers
    '''
    counterITS = 0
    counterSTI = 0
    integerToString = {}
    stringToInteger = {}
    for i in wordList:
        if i not in integerToString.values():
            integerToString[counterITS] = i
            counterITS += 1
        if i not in stringToInteger.keys():
            stringToInteger[i] = counterSTI
            counterSTI += 1

    return [integerToString, stringToInteger]

def count(wordList, stringToInteger):
    '''
    This creates a 2D list counting the number of times a word follows another word
    Parameters:
        wordList (string[]):  List of words
        stringToInteger (dict):  Dictionary arranged by strings and storing integers
    Returns:
        countList (int[][]):  A 2D list counting the number of time a word follows another word
    '''
    dictSize = len(stringToInteger)
    countList = [[0] * dictSize for _ in range(dictSize)] #https://stackoverflow.com/questions/13157961

    for i in range (0, len(wordList) - 1):
        firstWord = wordList[i]
        secondWord = wordList[i+1]
        firstWordInt = stringToInteger[firstWord]
        secondWordInt = stringToInteger[secondWord]
        countList[firstWordInt][secondWordInt] += 1

    return countList

def rowTotals(countList):
    '''
    This creates a list of the sum of each row of given 2D list
    Parameters:
        countList (int[][]):  2D list of numbers
    Returns:
        rowCountList (int[]):  A list of the sum of each row of the given 2D list
    '''
    rowCountList = [0]*len(countList)
    i = 0
    for y in countList:
        for x in y:
            rowCountList[i] += x
        i += 1
    return rowCountList

def calcProbabilities(countList, rowCountList):
    '''
    This creates a list of the probability of a word following another word
    Parameters:
        countList (int[][]):  2D list of numbers
        rowCountList (int[]):  A list of the sum of each row of the given 2D list
    Returns:
        probDict (dict[dict]):  A 2D dictionary of the probabilities that a given word with follow another word
    '''
    listSize = len(countList)
    probDict = {}
    xCount = 0
    yCount = 0

    for y in countList:
        previousProb = 0
        rowList = []
        for x in y:
            if previousProb < 1:
                rowTotal = rowCountList[yCount]
                if (rowTotal != 0):
                    thisProb = round((x/rowTotal) + previousProb, 2)
                    if thisProb != 0 and previousProb != thisProb:
                        #print(str(xCount) + " " + str(yCount) + " " + str(thisProb))
                        rowList.append([xCount, thisProb])
                    previousProb = thisProb
            xCount += 1

        #print(rowList)
        probDict[yCount] = rowList
        #print("")

        xCount = 0
        yCount += 1

    #print(probDict)
    return probDict

def generateTweet(integerToString, stringToInteger, firstWordList, probDict, wordCount, punctCount, upperCount):
    '''
    This creates a list of the probability of a word following another word
    Parameters:
        integerToString (dict):  Dictionary arranged by integers and storing strings
        stringToInteger (dict):  Dictionary arranged by strings and storing integers
        firstWordList (string[]):  List of the first word used in a user's tweets
        probDict (dict[dict]):  A 2D dictionary of the probabilities that a given word with follow another word
        wordCount (int):  The average number of words in tweet, this function aims to generate something around this length
        punctCount (float):  The average punctuation in a tweet
        upperCount (float):  The average amount that a tweet starts with an uppercase
    Returns:
        tweet (string):  A tweet which should mimic a Twitter user
    '''
    twitterMaxCharCount = 280 - 38 #38 is overhead from extra info in tweet (23 char + 15 max username length)

    wordInt = stringToInteger[choice(firstWordList)]

    capitalize = True
    charCount = 0
    randomProb = 0
    tweet = []
    tweetPunctCount = 0

    for i in range(0, wordCount*2):
        #If too many characters are generated then stop
        if charCount >= twitterMaxCharCount:
            tweet.pop()
            break
        newWord = integerToString[wordInt]
        #print(newWord)
        charCount += len(newWord) + 1 #Add one for spaces
        if capitalize and not newWord[0].isupper() and upperCount > random():
            #Capitalize the first letter of the word
            newWord = newWord[0].capitalize()
        tweet.append(newWord)
        capitalize = False

        #Look for end of sentence punctuation marks
        if newWord[-1:] in ["!", "?" ,"."]:
            tweetPunctCount += 1
            capitalize = True
            #Check to see if the tweet is around the right length
            if i > wordCount/2 or tweetPunctCount > punctCount:
                break; #Stop generating text

        #Look for end of tweet marker <eot>
        if newWord == "<eot>":
            tweet.pop()
            #Check to see if the tweet is around the right length
            if i > wordCount/2 or tweetPunctCount > punctCount:
                break; #Stop generating text

        randomProb = random()

        nextWordProbs = probDict[wordInt]
        #print(nextWordProbs)

        for j in nextWordProbs:
            if j[1] > randomProb:
                #print(j[1])
                #print(randomProb)
                wordInt = j[0]
                break
        
        #print(str(wordInt) + " " + integerToString[wordInt])

    #Remove duplicate words (From https://stackoverflow.com/a/5738933/13360215)
    tweet = [x[0] for x in groupby(tweet)]
    #Puts the tweet together with spaces between
    tweet = ' '.join(tweet)
    #Convert escaped HTML back into actual characters (eg &amp; to &)
    tweet = unescape(tweet)

    return tweet

def outputToTwitter(user, tweet):  
    '''
    Post data to Twitter
    Parameters:
        user (string):  The username that is being impersonated
        tweet (string):  The tweet that has been generated
    '''
    twitter.update_status(status= "User: " + user + "\nGenerated Tweet: " + tweet)

def storeData(integerToStringDict, stringToIntegerDict, firstWordList, probDict, averageWords, averagePunct, averageUpper, twitterUser):
    '''
    Store all the information locally to save time by not calling the Twitter API and recalculating everything
    Parameters:
        integerToString (dict):  Dictionary arranged by integers and storing strings
        stringToInteger (dict):  Dictionary arranged by strings and storing integers
        firstWordList (string[]):  List of the first word used in a user's tweets
        probDict (dict[dict]):  A 2D dictionary of the probabilities that a given word with follow another word
        averageWords (int):  The average number of words in tweet
        averagePunct (float):  The average punctuation in a tweet
        averageUpper (float):  The average amount that a tweet starts with an uppercase
        twitterUser (string):  Twitter user you want to imitate
    '''
    store = {
        "time": time(), 
        "twitterUser": twitterUser,
        "integerToStringDict": integerToStringDict, 
        "stringToIntegerDict": stringToIntegerDict, 
        "firstWordList": firstWordList, 
        "probDict": probDict, 
        "averageWords": averageWords, 
        "averagePunct": averagePunct,
        "averageUpper": averageUpper
    }
    with open(join(path[0], twitterUser + '.tmbd'), 'wb') as storeFile:
        dump(store, storeFile)

def readData(twitterUser):
    '''
    Store all the information locally to save time by not calling the Twitter API and recalculating everything
    Parameters:
        twitterUser (string):  Twitter user you want to imitate
    Returns:
        outputDictionary (dict):  This contains the information that was read from the file (this will be blank if the data had not been cached or the cache had expired)
    '''
    outputData = {}
    try:
        with open(join(path[0], twitterUser + '.tmbd'), 'rb') as storeFile:
            storedData = load(storeFile)
            #Calculate whether the cache should have expired
            if storedData["time"] > time() - 86400: #86400 is 1 day, 7200 is 2 hours
                outputData = storedData
    except:
        #If the file doesn't exist or there is some error reading it then ignore it
        pass
    return outputData

def getTwitterUser(twitterUser):
    '''
    Run all the calculations needed to generate an imiation of a Twitter user's tweets
    Parameters:
        twitterUser (string):  Username of a Twitter account you want to imitate (this can be left blank to randomly choose an account to mimic)
    Returns:
        twitterUser (string):  Username of a Twitter account to imitate
    '''
    if twitterUser != "":
        if twitterUser[0] == "@":
            twitterUser = twitterUser[1:]
    else:
        with open(join(path[0], 'twitterUsers.csv'), 'r', encoding='utf-8-sig') as twitterUsersCSV:
            twitterUsers = reader(twitterUsersCSV)
            twitterUsersList = []
            for row in twitterUsers:
                twitterUsersList.append(row[0])
            #print(twitterUsersList)
            twitterUser = choice(twitterUsersList)

    #print(twitterUser)
    return twitterUser

def calculateMimic(userToMimic):
    '''
    Run all the calculations needed to generate an imiation of a Twitter user's tweets
    Parameters:
        userToMimic (string):  Username of a Twitter account you want to imitate
    '''
    twitterUser = getTwitterUser(userToMimic)

    cachedData = readData(twitterUser)
    if cachedData == {}:
        #print("No cached data or cache has expired, now generating data")
        '''Get Tweets'''
        # print("Original text:")
        # tweetList = getTweetsTest("testData.txt")
        tweetList = readTweetsByUser(twitterUser, 10000, False)
        #print(str(len(tweetList)) + " tweets found")
        # print(tweetList)

        stats = getInputTweetsStats(tweetList)
        # print(stats)
        averageWords = stats["avgWords"]
        averagePunct = stats["avgPunct"]
        averageUpper = stats["avgUpper"]
        averageImages = stats["avgImg"] #Currently unused

        splitWordsOutput = splitIntoWords(tweetList)
        wordList = splitWordsOutput[0]
        firstWordList = splitWordsOutput[1]
        #For testing if you're getting data from a file
        # wordList = tweetList
        # firstWordList = ["The", "The", "The", "The"]
        # print(wordList)

        '''Create dictionaries for the tweets'''
        dicts = createDictionary(wordList)
        # print("\nInteger to string:")
        integerToStringDict = dicts[0]
        # printDictionary(integerToStringDict)
        # print("\nString to integer:")
        stringToIntegerDict = dicts[1]
        # printDictionary(stringToIntegerDict)
        # print("")

        '''Count the number of times a word follows another word'''
        countList = count(wordList, stringToIntegerDict)
        # print2dList(countList)
        # print("")

        '''Sum of rows of the count list'''
        rowCountList = rowTotals(countList)
        # print(rowCountList)
        # print("")

        '''Calculate the probability of a word following another word'''
        probDict = calcProbabilities(countList, rowCountList)
        # printDictionary(probDict)
        # print("")

        storeData(integerToStringDict, stringToIntegerDict, firstWordList, probDict, averageWords, averagePunct, averageUpper, twitterUser)

    else:
        # print("Reading data from cache")
        integerToStringDict = cachedData["integerToStringDict"]
        stringToIntegerDict = cachedData["stringToIntegerDict"]
        firstWordList = cachedData["firstWordList"]
        probDict = cachedData["probDict"]
        averageWords = cachedData["averageWords"]
        averagePunct = cachedData["averagePunct"]
        averageUpper = cachedData["averageUpper"]
        #averageImages = cachedData["averageImages"]

    #Once this has all been generated pass it onto outputMimic
    outputMimic(integerToStringDict, stringToIntegerDict, firstWordList, probDict, averageWords, averagePunct, averageUpper, twitterUser)

def outputMimic(integerToStringDict, stringToIntegerDict, firstWordList, probDict, averageWords, averagePunct, averageUpper, twitterUser):
    '''
    Generate a tweet and give the option to output, try again or quit
    Parameters:
        integerToString (dict):  Dictionary arranged by integers and storing strings
        stringToInteger (dict):  Dictionary arranged by strings and storing integers
        firstWordList (string[]):  List of the first word used in a user's tweets
        probDict (dict[dict]):  A 2D dictionary of the probabilities that a given word with follow another word
        averageWords (int):  The average number of words in tweet
        averagePunct (float):  The average punctuation in a tweet
        averageUpper (float):  The average amount that a tweet starts with an uppercase
        twitterUser (string):  Twitter user you want to imitate
    '''
    tweet = generateTweet(integerToStringDict, stringToIntegerDict, firstWordList, probDict, averageWords, averagePunct, averageUpper)
    outputToTwitter(twitterUser, tweet)
   
    # print("\nGenerated tweet:")
    # print(tweet)

    """
    outputCheck = input("Are you sure you want to post? (y=yes, n=no, 2=generate another without posting)  ")
    if outputCheck == "y":
        outputToTwitter(twitterUser, tweet)
        print("The tweet was posted")
    elif outputCheck == "2":
        #Go again
        outputMimic(integerToStringDict, stringToIntegerDict, firstWordList, probDict, averageWords, averagePunct, twitterUser)
    else:
        print("The tweet was not posted")
    """




calculateMimic(userToMimic)