#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 10:07:48 2020

@author: jonathanwest
"""
#SQL-related imports
import mysql.connector

#Date manipulation-related imports
from datetime import datetime
from pytz import timezone
import pytz

#Tweet-related imports
import json
import tweepy
import math
from time import sleep


#%%
# Initialize MySQL

db = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="password",
  database="twitdb"
)
cursor = db.cursor()

#Initialize Twitter

with open('api_keys.json') as f:
    keys = json.load(f)

tweepy_auth = tweepy.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
tweepy_auth.set_access_token(keys['access_token'], keys['access_token_secret'])
tweepy_api = tweepy.API(tweepy_auth)

#%%

# THIS BLOCK OF FUNCTIONS RELATES TO EXTRACTION OF TWEET DATA

def returnListOfTwitterEntities(tweet,entity):
    
    #This method reads in a tweet and then extracts the items from the "entities" feature
    #Only coded up to work for hashtags and user mentions
    #Hashtags = any hashtag in the tweet
    #User Mentions = any other twitter user mentioned
    
    if entity == 'hashtags': entityName = 'text'
    if entity == 'user_mentions': entityName = 'screen_name'
    
    if tweet.entities[entity] == []:
        entity_str = ''
    else:
        entity_list = []
        for entity in tweet.entities[entity]:
            entity_list.append(entity[entityName])
        entity_str = str(entity_list).strip('[]')
    return (entity_str)


def returnUTCDateAsETDate(tweet_dateUTC):
    dateUTC = tweet_dateUTC.replace(tzinfo=pytz.UTC)
    dateET = dateUTC.astimezone(timezone('America/New_York'))
    return (dateET)

def returnRetweetDateET(tweet):
    try:
        created_at_utc = tweet.retweeted_status.created_at
        created_at_et = returnUTCDateAsETDate(created_at_utc)
    except AttributeError:
        created_at_et = None
    return created_at_et
    
def returnRetweetBoolean(tweet):
    try:
        created_test = tweet.retweeted_status.created_at
        retweeted_bool = 1
    except AttributeError:
        retweeted_bool = 0
    return retweeted_bool
    
def returnTweetDataforSQL(tweet):
    tweet_data =            []
    tweet_id =              tweet.id
    tweet_id_str =          tweet.id_str
    screen_name =           tweet.user.screen_name
    created_at_UTC =        str(tweet.created_at)
    created_at_ET =         str(returnUTCDateAsETDate(tweet.created_at))
    source =                tweet.source
    retweet_original_ET =   returnRetweetDateET(tweet)
    retweet_bool =          returnRetweetBoolean(tweet)
    hashtags =              returnListOfTwitterEntities(tweet,'hashtags')
    mentions =              returnListOfTwitterEntities(tweet,'user_mentions')
    text =                  tweet.full_text
    tweet_data = [tweet_id, tweet_id_str, screen_name, created_at_UTC, created_at_ET,
                  source, retweet_original_ET, retweet_bool, hashtags, mentions, text]
    return(tweet_data)
    
# END OF BLOCK OF TWEET EXTRACTION FUNCTIONS
    
#%%

# THIS BLOCK OF FUNCTIONS RELATES TO DOWNLOADING NEW TWEETS

def returnUserMaxID(user):
    try:
        max_id = users_maxid[user]
    except:
        max_id = 0
    return(max_id)

def insertTweetsIntoSQL(tweets_data):
    sql = """INSERT IGNORE INTO tweets (tweet_id, tweet_id_str, screen_name, created_at_UTC, 
                created_at_ET, source, retweet_original_ET, retweet_bool, 
                hashtags, mentions, text) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    
    cursor.executemany(sql,tweets_data)
    db.commit()
    print('Committed',len(tweets_data),'rows to SQL')

#%%

sql = 'SELECT LOWER(screen_name) AS screen_name, MAX(tweet_id) FROM tweets GROUP BY screen_name;'
cursor.execute(sql)
users_maxid = dict(cursor.fetchall())
#print(users_maxid)
#print(type(users_maxid))
#print(users_maxid['realdonaldtrump'])

#%%
# This reads in the master list of users
users_json = 'users.json'
with open(users_json) as f:
    users = json.load(f)

#%%

for user in users:
    user = user.lower()
    print('Max ID in db for',user,':',returnUserMaxID(user))
    tweets_data = []
    max_id = returnUserMaxID(user)
    tweet_id = 1
    atUser = '@' + user
    print("Downloading tweets now from ", user)
    tweets = tweepy.Cursor(tweepy_api.user_timeline, screen_name=atUser, tweet_mode="extended").items()

    while len(tweets_data) < 3000:
        if tweet_id == max_id:
            break
        i=0
        for tweet in tweets:
            tweet_id = tweet.id
            if tweet_id == max_id:
                break
            i = i+1
#            print('Tweet #',i,':',tweet_id,tweet.full_text[0:30])
            tweets_data.append(returnTweetDataforSQL(tweet))
            if i % 100 == 0:
                print('This is tweet #', i, ' for this go-around for ',user)                
        print('Cumu',user,'tweets:',len(tweets_data))
    if len(tweets_data) > 0:
        insertTweetsIntoSQL(tweets_data)

#%%
cursor.close()
db.close()
#%%
#
### 
### This block of code was used to import my existing json lists of tweet ids into the sql db
###
#
#users = ['realdonaldtrump','potus','whitehouse',
#         "aoc", "andrewyang", "joebiden", 
#         "mike_pence", "berniesanders", "mikebloomberg",
#         "donaldjtrumpjr", "ivankatrump",
#         'ewarren','staceyabrams',
#         'govwhitmer','kamalaharris',
#         'amyklobuchar',
#         'ambassadorrice', 'Michelle4NM', 
#         'GovMLG', 'SenDuckworth', 
#         'RepValDemings',
#         'SenCortezMasto', 'SenatorBaldwin',
#         'trish_regan','justinamash']
#
## Read in the tweet id file from a given user
#for user in users:
#    twitter_ids_filename = 'ID_DBs/all_ids_' + user + '.json'
#    with open(twitter_ids_filename) as f:
#        tweet_ids = json.load(f)
#
## Initialize for the tweet-gathering process
#    tweets_data = []
#    start = 0
#    end = 100
#    limit = len(tweet_ids)
#    i = math.ceil(limit / 100)
#
## Actually gather the tweets
#    for go in range(i):
#        print('currently getting {} {} - {}'.format(user, start, end))
#        sleep(6)  # needed to prevent hitting API rate limit
#        id_batch = tweet_ids[start:end]
#        start += 100
#        end += 100
#        tweets = tweepy_api.statuses_lookup(id_batch, tweet_mode='extended')
#        for tweet in tweets:
#            tweets_data.append(returnTweetDataforSQL(tweet))
#
## Inject the data into SQL
#    sql = """INSERT IGNORE INTO tweets (tweet_id, tweet_id_str, screen_name, created_at_UTC, 
#                               created_at_ET, source, retweet_original_ET, retweet_bool, 
#                               hashtags, mentions, text) 
#                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
#    
#    cursor.executemany(sql,tweets_data)
#    db.commit()
#    print('Committed ',len(tweets_data),' rows')
#    
#
##%%
##sql = '''CREATE TABLE tweets (
## id INT AUTO_INCREMENT PRIMARY KEY,
## tweet_id BIGINT UNSIGNED UNIQUE,
## tweet_id_str varchar(255),
## screen_name varchar(255),
## created_at_UTC timestamp,
## created_at_ET timestamp,
## source varchar(255),
## retweet_original_ET timestamp,
## retweet_bool BOOLEAN,
## hashtags varchar(255),
## mentions varchar(255),
## text text
##)'''
##
###sql = "DROP TABLE IF EXISTS tweets"
##cursor.execute(sql)
#    
