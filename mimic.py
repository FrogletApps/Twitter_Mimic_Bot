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

def createDictionary(wordArray):
    '''
    This will put the data into two dictionaries
    Parameters:
        wordArray (string[]):  Array of words
    Returns:
        integerToString (dict):  Dictionary arranged by integers and storing strings
        stringToInteger (dict):  Dictionary arranged by strings and storing integers
    '''
    counter = 0
    integerToString = {}
    for i in wordArray:
        if i not in integerToString.values():
            integerToString[counter] = i
            counter += 1
    
    counter = 0
    stringToInteger = {}
    for i in wordArray:
        if i not in stringToInteger.keys():
            stringToInteger[i] = counter
            counter += 1

    return [integerToString, stringToInteger]

def outputToTwitter(user, tweet):  
    '''
    Post data to Twitter
    Parameters:
        user (string):  The username that is being impersonated
        tweet (string):  The tweet that has been generated
    '''
    twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    twitter.update_status(status= user + "\n" + tweet)

def printDictionary(dictionary):
    '''
    Print a dictionary (from: https://www.codevscolor.com/python-print-key-value-dictionary/)
    Parameters:
        dictionary (dict):  Dictionary to print
    '''
    for item in dictionary:
        print("Key : {} , Value : {}".format(item, dictionary[item]))

print("Original text:")
words = getTweetsTest("testData.txt")
print(words)

dicts = createDictionary(words)
print("\nInteger to string:")
print(printDictionary(dicts[0]))
print("\nString to integer:")
print(printDictionary(dicts[1]))
