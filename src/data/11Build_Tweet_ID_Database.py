#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 19:24:45 2020

@author: jonathanwest
"""

# %% Initialize the workspace

# Set up the install packages we are going to need
import datetime
import tweepy
import json
from time import sleep
import random

#Initialize tweepy user/password details

with open('api_keys.json') as f:
    keys = json.load(f)

auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
auth.set_access_token(keys['access_token'], keys['access_token_secret'])
api = tweepy.API(auth)

#%%
# Initialize the list of usernames to track

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


# %% Grab all of the tweet IDs in the user's timeline.  This will pull somewhere between 500 - 3500 tweets

for user in users:
    atUser = '@' + user
    print("Downloading tweets now from ", user)
    tweets = tweepy.Cursor(api.user_timeline, screen_name=atUser, tweet_mode="extended").items()
    
#%% Figure out what is the latest tweet ID in the existing user's scraped tweet database
    
    id_maxScraped = 0
    twitter_dbs_filename = '/data/interim/Tweet_DBs/all_tweets_' + user + '.json'
    try:
        with open(twitter_dbs_filename) as f:
            tweets_scraped = json.load(f)
            counter = 0
            for tweet in tweets_scraped:
                if tweet['id'] > id_maxScraped:
                    id_maxScraped = tweet['id']
        #        if counter % 500 == 0:
        #            print('This is index #', counter, ' and tweet #',tweet['id'])
        #            print('Max ID is: ',id_maxScraped)
                counter = counter + 1
            print('Final scraped Max ID for ',user,' is: ',id_maxScraped)
    except:
        print('No Tweet DB found for user:',user)

#%%
# 4/12: Noticed a bug with RDT's twitter downloads: wasn't pulling all of them in
# To address RDT, need to pull the tweets in a little differently

    ids=[]
    id_number = 0
    if user == 'realdonaldtrump':
        while len(ids) < 3000: #Note: the generic cursor pull gets ~3,200 items
            if id_number == id_maxScraped:
                break
            i=0
            for tweet in tweets:
                id_number = tweet.id
                i = i+1
                if id_number == id_maxScraped:
                    break
                if i % 100 == 0:
                    print('This is tweet #', i, ' for this go-around for ',user)
                ids.append(id_number)
            print('Cumu ',user,' tweets: ',len(ids))
    else:
        i=0
        for tweet in tweets:
            id_number = tweet.id
            i = i+1
            if id_number == id_maxScraped:
                break
            if i % 100 ==0:
                print('This is tweet #', i, ' for user ',user)
            ids.append(id_number)
        print("# New Tweets Found by ",user,": ",len(ids))
    
    #%%
    
    twitter_ids_filename = '/data/interim/ID_DBs/all_ids_' + user + '.json'
    try:
        with open(twitter_ids_filename) as f:
            all_ids = ids + json.load(f)
            data_to_write = list(set(all_ids))
            print('tweets found on this scrape: ', len(ids))
            print('total tweet count: ', len(data_to_write))
    except FileNotFoundError:
        with open(twitter_ids_filename, 'w') as f:
            all_ids = ids
            data_to_write = list(set(all_ids))
            print('tweets found on this scrape: ', len(ids))
            print('total tweet count: ', len(data_to_write))
    
    with open(twitter_ids_filename, 'w') as outfile:
        json.dump(data_to_write, outfile)
        
        
#%%
#        
##rdttweets = tweepy.Cursor(api.user_timeline, screen_name='@realdonaldtrump', tweet_mode="extended").pages(300)
#rdttweets = tweepy.Cursor(api.user_timeline, screen_name='@realdonaldtrump', tweet_mode="compat").items()
#rdtids=[]
#
#
##%%
#
#user='rdt'
#i=0
#for tweet in rdttweets:
#    id_number = tweet.id
#    print(tweet.id)
#    i = i+1
#    if i % 50 ==0:
#        print('This is tweet #', i, ' for user ',user)
#        sleep(1)
##    if i % 1 ==0:
##        break
#    rdtids.append(id_number)
#rdtids = list(dict.fromkeys(rdtids))
#print(len(rdtids))
#
#        
##%%
#        
##rdttweets = tweepy.Cursor(api.user_timeline, screen_name='@realdonaldtrump', tweet_mode="extended").pages(300)
#satweets = tweepy.Cursor(api.user_timeline, screen_name='@potus', tweet_mode="compat").items(3000)
#saids=[]
#
##%%
#
#user='sabrams'
#i=0
#for tweet in satweets:
#    id_number = tweet.id
#    print(tweet.id)
#    i = i+1
#    if i % 50 ==0:
#        print('This is tweet #', i, ' for user ',user)
#        sleep(1)
##    if i % 1 ==0:
##        break
#    saids.append(id_number)
#
#saids = list(dict.fromkeys(saids))
#print(len(saids))


#%%
#user = api.get_user('@realdonaldtrump')
#print(user.screen_name)
#print(user.description)
#print(user.followers_count)
#print(user.statuses_count)
#print(user.url)
#


