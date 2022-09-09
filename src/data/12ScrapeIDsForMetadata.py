#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 19:24:45 2020

@author: jonathanwest
"""


# %% Initialize Script

import tweepy
import json
import math
import glob
import csv
import zipfile
import zlib
import random
from tweepy import TweepError
from time import sleep
import numpy as np

#Initialize tweepy user/password details

with open('api_keys.json') as f:
    keys = json.load(f)

auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
auth.set_access_token(keys['access_token'], keys['access_token_secret'])
api = tweepy.API(auth)

# Initialize the list of usernames to track


#%%

users_always = ['realdonaldtrump','potus','whitehouse']
users_sometimes = ["aoc", "andrewyang", "joebiden", 
             "mike_pence", "berniesanders", "mikebloomberg",
             "donaldjtrumpjr", "ivankatrump",
             'ewarren','staceyabrams',
             'govwhitmer','kamalaharris',
             'amyklobuchar',
             'ambassadorrice', 'Michelle4NM', 
             'GovMLG', 'SenDuckworth', 
             'RepValDemings',
             'SenCortezMasto', 'SenatorBaldwin',
             'trish_regan','justinamash']


# This step builds up a users list for this run that only contains a random 3 "sometimes" users
users = users_always.copy()
users.extend(random.sample(users_sometimes,3))

print(users)    

# %% Read in the files and create the list of IDs that need to be scraped
# This is where Python understands what files to open and write to
#
#There are two types of files we're going to process:
#    1. The input file, which is all of the unique IDs.  Stored at ID_DBs/all_ids_<user>.json
#    2. The output file, which is the master twitter db for that user.  Stored at Tweet_DBs/all_tweets_<user>.json

#The work here will accomplish four objectives:
#    1. Read in the list of all tweet IDs.  This list has no additional tweet detail
#    2. Check whether there is a database of tweets
#    3. If there is a database of tweets, extract the list of tweets that have been scraped
#    4. Do a list diff to identify the IDs that have been captured but not scraped

for user in users:
    input_file = '/data/interim/ID_DBs/all_ids_' + user + '.json'
    output_file = '/data/interim/Tweet_DBs/all_tweets_' + user + '.json'
    
    #Step 1: pull in the full set of IDs
    
    with open(input_file) as f:
        ids_full = json.load(f)
    
    #Steps 2 and 3: test if there's the full db; if there is, extract existing tweet IDs
    ids_scraped = []
    try:
        with open(output_file) as f:
            tweets_scraped = json.load(f)
            for tweet in tweets_scraped:
                ids_scraped.append(str(tweet["id"]))
    except:
        tweets_scraped = []
        ids_scraped = []
        
    #Step 4: Create the diff list of tweets that have been ID'd but not scraped
    
    def setdiff_sorted(array1,array2,assume_unique=False):
        ans = np.setdiff1d(array1,array2,assume_unique).tolist()
        if assume_unique:
            return sorted(ans)
        return ans
    
    ids_toScrape = []
    ids_toScrape = setdiff_sorted(ids_full,ids_scraped)
    
    print('user ID being checked: {}'.format(user))
    print('total ids to date: {}'.format(len(ids_full)))
    print('already scraped ids: {}'.format(len(ids_scraped)))
    print('unique ids to check: {}'.format(len(ids_toScrape)))
    
    #%% The real work of scraping the tweets
    
    if len(ids_toScrape)==0:
        print("Nothing to update")
    else:
    
        start = 0
        end = 100
        limit = len(ids_toScrape)
        i = math.ceil(limit / 100)
        
        for go in range(i):
            print('currently getting {} - {}'.format(start, end))
            sleep(1)  # needed to prevent hitting API rate limit
            id_batch = ids_toScrape[start:end]
            start += 100
            end += 100
            tweets = api.statuses_lookup(id_batch)
            for tweet in tweets:
                tweets_scraped.append(dict(tweet._json))
                
        
        print('metadata collection complete')
        print('creating master json file')
        with open(output_file, 'w') as outfile:
            json.dump(tweets_scraped, outfile)
        results = []

