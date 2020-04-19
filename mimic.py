#!/usr/bin/python3
# -*- coding: utf-8 -*-

from twython import Twython
from secret import *

def getTweetsTest(fileName):
    '''
    This will get test information from file and put it into an array (in lower case)
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

def count(integerToStringDict, size):
    '''
    This create an array counting the number of times a word follows another word
    Parameters:
        integerToStringDict (dict):  Integer to string dictionary
        size (int): Size of the output array (size * size)
    Returns:
        countArray (int[]):  An array counting the number of time a word follows another word
    '''
    countArray = [[]]


    return countArray

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
        print("Key:{}, Value:{}".format(item, dictionary[item]))

def print2dArray(arrayToPrint):
    '''
    Print a 2D array
    Parameters:
        arrayToPrint ([]):  Array to print
    '''
    for x in arrayToPrint:
        print(x)

print("Original text:")
words = getTweetsTest("testData.txt")
print(words)

dicts = createDictionary(words)
print("\nInteger to string:")
print(printDictionary(dicts[0]))
print("\nString to integer:")
print(printDictionary(dicts[1]))
