#!/usr/bin/python3
# -*- coding: utf-8 -*-

import html
from itertools import groupby
from random import choice, random #randint
import re
from secret import *
from twython import Twython

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

#Insert a Twitter username here
userToMimic = "realdonaldtrump"

def getTweetsTest(fileName):
    '''
    This will get test information from file and put it into an array (in lower case)
    Parameters:
        filename (string):  Location of the test data file
    Returns:
        wordArray (string[]):  Array of words in file in lower case.
    '''
    with open(fileName, "r") as inputFile:
        return inputFile.read().lower().split() #Set to lower case and split into array of words

def readTweetsByUser(username, limit=200, retweets=False):
    '''
    This will get tweets from Twitter and put them into an array of tweets
    Parameters:
        username (string):  The user whose tweets you want to recieve
        limit (int):  The number of tweets you want to recieve (this is the maximum you can get, there is a limit of 200, and even if you disable retweets they are still counted) (default:200)
        retweets (Boolean):  Enable retweets or not (default:False)
    Returns:
        tweetArray (string[]):  Array of tweets
    '''
    username = "@" + username
    #dataArray contains a lot of metadata that we don't need
    dataArray = twitter.get_user_timeline(screen_name=username, count=limit, include_rts=retweets, tweet_mode='extended')
    tweetArray = []
    for tweetData in dataArray:
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
        print(tweetText)
        #Collect Tweet, media type, and the media URL
        tweet = [tweetText, mediaType, mediaURL]
        #print(tweet)
        tweetArray.append(tweet)
    return tweetArray

def getInputTweetsStats(tweetArray):
    '''
    This will calculate statistics about the tweets
    Parameters:
        tweetArray (string[]):  Array of tweets
    Returns:
        outputStats (dict):  Dictionary of statistics
    '''
    wordArray = []
    stats = []
    outputStats = {}
    tweetNo = len(tweetArray)

    for miniTweetData in tweetArray:
        tweetStats = []
        tweet = miniTweetData[0]
        #print(tweet)
        wordArray = tweet.split()
        tweetLength = len(wordArray)
        tweetStats.append(tweetLength)

        punctCount = 0
        for word in wordArray:
            if word[-1:] in ["!", "?" ,"."]:
                punctCount += 1
            
        tweetStats.append(punctCount)
        #print(punctCount)

        image = 0
        if miniTweetData[1] == "photo":
            image = 1            
        tweetStats.append(image)

        stats.append(tweetStats)

    totalWords = 0
    totalPunct = 0
    totalImages = 0
    countTweets = 0
    for tweetStats in stats:
        #print(tweetStats)
        totalWords += tweetStats[0]
        totalPunct += tweetStats[1]
        totalImages += tweetStats[2]
        countTweets += 1

    averageWords = round(totalWords/countTweets)
    averagePunct = totalPunct/countTweets
    averageImages = totalImages/countTweets
    outputStats["avgWords"] = averageWords
    outputStats["avgPunct"] = averagePunct
    outputStats["avgImg"] = averageImages
    #print(outputStats)

    return outputStats

def splitIntoWords(tweetArray):
    '''
    This will get the tweets and split them up into individual words (and remove certain unwanted elements like @usernames and hyperlinks)
    Parameters:
        tweetArray (string[]):  Array of tweets
    Returns:
        wordArray (string[]):  Array of words from the user's tweets
        firstWordArray (string[]):  Array of the first word used in a user's tweets
    '''
    wordArray = []
    firstWordArray = []
    for tweet in tweetArray:
        firstWord = True
        #print(tweet)
        #print()
        words = tweet[0].split()
        for word in words:
            #Remove @Users and web links
            if "@" not in word and "http" not in word:
                #Strip out double quotes and brackets
                word = re.sub("\"|“|”|\(|\)", "", word)
                wordArray.append(word)
                if firstWord == True:
                    firstWordArray.append(word)
                    firstWord = False

    #print(wordArray)
    print(firstWordArray)
    return [wordArray, firstWordArray]

def createDictionary(wordArray):
    '''
    This will put the data into two dictionaries
    Parameters:
        wordArray (string[]):  Array of words
    Returns:
        integerToString (dict):  Dictionary arranged by integers and storing strings
        stringToInteger (dict):  Dictionary arranged by strings and storing integers
    '''
    counterITS = 0
    counterSTI = 0
    integerToString = {}
    stringToInteger = {}
    for i in wordArray:
        if i not in integerToString.values():
            integerToString[counterITS] = i
            counterITS += 1
        if i not in stringToInteger.keys():
            stringToInteger[i] = counterSTI
            counterSTI += 1

    return [integerToString, stringToInteger]

def count(wordArray, stringToInteger):
    '''
    This creates 2D array counting the number of times a word follows another word
    Parameters:
        wordArray (string[]):  List of words
        stringToInteger (dict):  Dictionary arranged by strings and storing integers
    Returns:
        countArray (int[][]):  A 2D array counting the number of time a word follows another word
    '''
    dictSize = len(stringToInteger)
    countArray = [[0] * dictSize for _ in range(dictSize)] #https://stackoverflow.com/questions/13157961

    for i in range (0, len(wordArray) - 1):
        firstWord = wordArray[i]
        secondWord = wordArray[i+1]
        firstWordInt = stringToInteger[firstWord]
        secondWordInt = stringToInteger[secondWord]
        countArray[firstWordInt][secondWordInt] += 1

    return countArray

def rowTotals(countArray):
    '''
    This creates an array of the sum of each row of given 2D array
    Parameters:
        countArray (int[][]):  2D array of numbers
    Returns:
        rowCountArray (int[]):  An array of the sum of each row of the given 2D array
    '''
    rowCountArray = [0]*len(countArray)
    i = 0
    for y in countArray:
        for x in y:
            rowCountArray[i] += x
        i += 1
    return rowCountArray

def calcProbabilities(countArray, rowCountArray):
    '''
    This creates an array of the probability of a word following another word
    Parameters:
        countArray (int[][]):  2D array of numbers
        rowCountArray (int[]):  An array of the sum of each row of the given 2D array
    Returns:
        probArray (int[][]):  A 2D array of the probabilities that a given word with follow another word
    '''
    arraySize = len(countArray)
    probArray = [[0] * (arraySize) for _ in range(arraySize)] #https://stackoverflow.com/questions/13157961
    xCount = 0
    yCount = 0

    for y in countArray:
        cumulativeProb = 0
        for x in y:
            if (rowCountArray[yCount] != 0):
                #print(round((x/rowCountArray[yCount]) + cumulativeProb, 2))
                probArray[yCount][xCount] = round((x/rowCountArray[yCount]) + cumulativeProb, 2)
            else:
                probArray[yCount][xCount] = cumulativeProb
            cumulativeProb = probArray[yCount][xCount]
            xCount += 1
        xCount = 0
        yCount += 1
    return probArray

def generateTweet(integerToString, stringToInteger, firstWordArray, probArray, wordCount, punctCount):
    '''
    This creates an array of the probability of a word following another word
    Parameters:
        integerToString (dict):  Dictionary arranged by integers and storing strings
        probArray (int[][]):  A 2D array of the probabilities that a given word with follow another word
        wordCount (int):  The number of words to put in the tweet (this is a limit, it could stop earlier if there is punctuation)
    Returns:
        tweet (string):  A tweet which should mimic a Twitter user
    '''
    twitterMaxCharCount = 280 - 38 #38 is overhead from extra info in tweet (23 char + 15 max username length)

    charCount = 0
    tweet = []
    #wordInt = randint(0, len(integerToString) - 1)
    wordInt = stringToInteger[choice(firstWordArray)]
    randomProb = 0
    tweetPunctCount = 0
    capitalize = True

    for i in range(0, wordCount*2):
        #If too many characters are generated then stop
        if charCount >= twitterMaxCharCount:
            tweet.pop()
            break
        newWord = integerToString[wordInt]
        #print(newWord)
        charCount += len(newWord) + 1 #Add one for spaces
        if capitalize:
            #Capitalize the first letter
            newWord = newWord.capitalize()
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

        for j in range(0, len(integerToString)):
            #print(str(probArray[wordInt][j]) + " > " + str(randomProb) + " : " + integerToString[j])
            if (probArray[wordInt][j] > randomProb):
                wordInt = j
                break

    #Remove duplicate words (From https://stackoverflow.com/a/5738933/13360215)
    tweet = [x[0] for x in groupby(tweet)]
    #Puts the tweet together with spaces between
    tweet = ' '.join(tweet)
    #Convert escaped HTML back into actual characters (eg &amp; to and)
    tweet = html.unescape(tweet)

    return tweet

def outputToTwitter(user, tweet):  
    '''
    Post data to Twitter
    Parameters:
        user (string):  The username that is being impersonated
        tweet (string):  The tweet that has been generated
    '''
    twitter.update_status(status= "User: " + user + "\nGenerated Tweet: " + tweet)

def printDictionary(dictionary):
    '''
    Print a dictionary (from: https://www.codevscolor.com/python-print-key-value-dictionary/)
    Parameters:
        dictionary (dict):  Dictionary to print
    '''
    for item in dictionary:
        print("Key:{}, Value:{}".format(item, dictionary[item]))

def print2dArray(arrayToPrint):
    '''
    Print a 2D array
    Parameters:
        arrayToPrint ([]):  Array to print
    '''
    for x in arrayToPrint:
        print(x)

def calculateMimic(twitterUser):
    '''
    Run all the calculations needed to generate an imiation of a Twitter user's tweets
    Parameters:
        twitterUser (string):  Twitter user you want to imitate
    '''
    if twitterUser[0] == "@":
        twitterUser = twitterUser[1:]
    print(twitterUser)

    '''Get Tweets'''
    # print("Original text:")
    #tweetArray = getTweetsTest("testData.txt")
    tweetArray = readTweetsByUser(twitterUser, 200, False)
    #print(tweetArray)

    stats = getInputTweetsStats(tweetArray)
    #print(stats)
    averageWords = stats["avgWords"]
    averagePunct = stats["avgPunct"]
    averageImages = stats["avgImg"] #Currently unused

    splitWordsOutput = splitIntoWords(tweetArray)
    wordArray = splitWordsOutput[0]
    firstWordArray = splitWordsOutput[1]
    #wordArray = tweetArray #For testing if you're getting data from a file
    #print(wordArray)

    '''Create dictionaries for the tweets'''
    dicts = createDictionary(wordArray)
    # print("\nInteger to string:")
    integerToStringDict = dicts[0]
    # print(printDictionary(integerToStringDict))
    # print("\nString to integer:")
    stringToIntegerDict = dicts[1]
    # print(printDictionary(stringToIntegerDict))
    # print("")

    '''Count the number of times a word follows another word'''
    countArray = count(wordArray, stringToIntegerDict)
    # print2dArray(countArray)
    # print("")

    '''Sum of rows of the count array'''
    rowCountArray = rowTotals(countArray)
    # print(rowCountArray)
    # print("")

    '''Calculate the probability of a word following another word'''
    probArray = calcProbabilities(countArray, rowCountArray)
    # print2dArray(probArray)
    # print("")

    #Once this has all been generated pass it onto outputMimic
    outputMimic(integerToStringDict, stringToIntegerDict, firstWordArray, probArray, averageWords, averagePunct, twitterUser)

def outputMimic(integerToStringDict, stringToIntegerDict, firstWordArray, probArray, averageWords, averagePunct, twitterUser):
    '''
    Generate a tweet and give the option to output, try again or quit
    Parameters:
        integerToString (dict):  Dictionary arranged by integers and storing strings
        stringToInteger (dict):  Dictionary arranged by strings and storing integers
        probArray (int[][]):  A 2D array of the probabilities that a given word with follow another word
        averageWords (int):  The average number of words in tweet
        averagePunct (float):  The average punctuation in a tweet
        twitterUser (string):  Twitter user you want to imitate
    '''
    tweet = generateTweet(integerToStringDict, stringToIntegerDict, firstWordArray, probArray, averageWords, averagePunct)
    # print(tweet)
    # print("")    

    print("\nGenerated tweet:")
    print(tweet)

    outputCheck = input("Are you sure you want to post? (y=yes, n=no, 2=generate another without posting)  ")
    if outputCheck == "y":
        outputToTwitter(twitterUser, tweet)
        print("The tweet was posted")
    elif outputCheck == "2":
        #Go again
        outputMimic(integerToStringDict, stringToIntegerDict, firstWordArray, probArray, averageWords, averagePunct, twitterUser)
    else:
        print("The tweet was not posted")



calculateMimic(userToMimic)