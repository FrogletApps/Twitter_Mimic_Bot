#!/usr/bin/python3
# -*- coding: utf-8 -*-

from twython import Twython
from secret import *
from random import randint, random

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

def getTweetsTest(fileName):
    '''
    This will get test information from file and put it into an array (in lower case)
    Parameters:
        filename (string):  Location of the test data file
    Returns:
        wordArray (string[]):  Array of words in file in lower case.
    '''
    with open(fileName, "r") as inputFile:
        return inputFile.read().lower().split() #Set to lower case and split into array

def readTweetsByUser(username, limit=200, retweets=False):
    '''
    This will get tweets from Twitter
    Parameters:
        username (string):  The user whose tweets you want to recieve
        limit (int):  The number of tweets you want to recieve (this is the maximum you can get, there is a limit of 200, and even if you disable retweets they are still counted) (default:200)
        retweets (Boolean):  Enable retweets or not (default:False)
    Returns:
        wordArray (string[]):  Array of words in file in lower case.
    '''
    data = twitter.get_user_timeline(screen_name="@"+username, count=limit, include_rts=retweets, tweet_mode='extended')
    wordArray = []
    for tweet in data:
        #print(tweet)
        #print()
        tweetWords = []
        tweetWords = tweet.get("full_text").lower().split()
        for word in tweetWords:
            wordArray.append(word)

    return wordArray

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
        stringToInteger (dict):  String to integer dictionary
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

def writeTweet(integerToString, probArray, wordCount):
    '''
    This creates an array of the probability of a word following another word
    Parameters:
        integerToString (dict):  Dictionary arranged by integers and storing strings
        probArray (int[][]):  A 2D array of the probabilities that a given word with follow another word
        wordCount (int):  The number of words to put in the tweet
    Returns:
        tweet (string):  A tweet which should mimic a Twitter user
    '''
    tweet = [""]*wordCount
    wordInt = randint(0, len(integerToString) - 1)
    randomProb = 0

    for i in range(0, wordCount):
        #print(integerToString[wordInt])
        tweet[i] = integerToString[wordInt]
        randomProb = random()

        for j in range(0, len(integerToString)):
            #print(str(probArray[wordInt][j]) + " > " + str(randomProb) + " : " + integerToString[j])
            if (probArray[wordInt][j] > randomProb):
                wordInt = j
                break

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

# print("Original text:")
# wordArray = getTweetsTest("testData.txt")
# print(wordArray)

# dicts = createDictionary(wordArray)
# print("\nInteger to string:")
# integerToStringDict = dicts[0]
# print(printDictionary(integerToStringDict))
# print("\nString to integer:")
# stringToIntegerDict = dicts[1]
# print(printDictionary(stringToIntegerDict))

# print("")
# countArray = count(wordArray, stringToIntegerDict)
# print2dArray(countArray)

# print("")
# rowCountArray = rowTotals(countArray)
# print(rowCountArray)

# print("")
# probArray = calcProbabilities(countArray, rowCountArray)
# print2dArray(probArray)

# print("")
# print(writeTweet(integerToStringDict, probArray, 6))

#print(readTweetsByUser("qikipedia", 200, False))

#wordArray = getTweetsTest("testData.txt")
twitterUser = "qikipedia"
wordArray = readTweetsByUser(twitterUser, 200, False)
dicts = createDictionary(wordArray)
integerToStringDict = dicts[0]
stringToIntegerDict = dicts[1]
countArray = count(wordArray, stringToIntegerDict)
rowCountArray = rowTotals(countArray)
probArray = calcProbabilities(countArray, rowCountArray)
tweet = writeTweet(integerToStringDict, probArray, 33)

print(tweet)

#outputToTwitter(twitterUser, tweet)

