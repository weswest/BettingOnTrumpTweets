#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 15:59:31 2020

@author: jonathanwest
"""

from datetime import datetime, timedelta
from pytz import timezone

import mysql.connector

import re

import pandas as pd
import statistics
from statistics import mean

import json
import urllib.request




#%%

pi_marketsURL = 'https://www.predictit.org/api/marketdata/all/'
with urllib.request.urlopen(pi_marketsURL) as url:
    pi_markets = json.loads(url.read().decode())

#print(pi_markets)
#print(type(pi_markets))
#print(pi_markets.keys())
#print(pi_markets['markets'])
#print(type(pi_markets['markets']))


#%%

def returnMarketURL(user):
    # Takes as input a twitter user.  Returns the url of the appropriate PredictIt tweet market
    atuser = '@'+user
    match = 0
    for market in pi_markets['markets']:
        url = market['url'].lower()
        if (url.find(atuser) != -1):
            match = url
            break
    return(match)

    
def convertYearMonthDayToNoonET(year,month,day):
    DateStr = str(year) +'-' + str(month) + '-' + str(day) + ' 12:00:00'
    DateNative = datetime.strptime(DateStr, "%Y-%m-%d %H:%M:%S")
    #3a. Convert to Eastern
    mktDate = timezone('America/New_York').localize(DateNative)
    return(mktDate)


def returnMarketDates(user):
    marketURL = returnMarketURL(user)
    
    dateRange = re.search('(?<=post-from-).*',marketURL).group().split('-')
    startMonth = dateRange[1]
    startMonth = datetime.strptime(startMonth, '%b').month
    startDay = int(dateRange[2])
    # The following IF statement aligns whether the url has two months or one
    if len(dateRange[4])==3: #This implies a second month
        endMonth = dateRange[4]
        endMonth = datetime.strptime(endMonth, '%b').month
        endDay = int(dateRange[5])
    else:    
        endMonth = startMonth
        endDay= int(dateRange[4])
    
    startYear = datetime.now().year
    if ((startMonth == 12) and (endMonth == 1)):
        endYear = startYear + 1
    else:
        endYear = startYear
    
    startDate = convertYearMonthDayToNoonET(startYear,startMonth,startDay)
    endDate = convertYearMonthDayToNoonET(endYear,endMonth,endDay)
    
    mktDiff = endDate - startDate
    mktDays, mktSeconds = mktDiff.days, mktDiff.seconds
    mktHours = mktDays * 24 + mktSeconds // 3600

    return(startDate, endDate, mktHours)
       
    
    
#%%

db = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="password",
  database="twitdb")

cursor = db.cursor()

user = 'potus'
#user = 'whitehouse'
#user = 'realdonaldtrump'

mktStartDate, mktEndDate, mktHours = returnMarketDates(user)
#mktStartDate = convertYearMonthDayToNoonET(2020,5,6)
#mktEndDate = convertYearMonthDayToNoonET(2020,5,13)
#mktHours = 168


sql = '''
    SELECT  CONVERT(DATE_FORMAT(created_at_ET,'%Y-%m-%d-%H:00:00'),DATETIME) as hours, 
            COUNT(tweet_id) as tweets
    FROM tweets
    WHERE screen_name = %s
    GROUP BY hours
    ORDER BY hours asc;'''
    
cursor.execute(sql,(user,))
tweets_df = pd.DataFrame(cursor.fetchall())
tweets_df.columns = ['hour','tweets']

tweets_df['hour'] = tweets_df['hour'].dt.tz_localize('America/New_York',ambiguous=True)
tweets_df.set_index('hour',inplace=True)
tweets_df_mktend = pd.DataFrame({'hour':[mktEndDate],'tweets':[0]})
tweets_df_mktend.set_index('hour',inplace=True)
tweets_df = tweets_df.append(tweets_df_mktend)
tweets_df = tweets_df.resample('H').sum()
tweets_df.reset_index(level=0, inplace=True)

#%%

tweets_df['mktHourOrig'] = 0

def convertDateToMktHour(measureDate):
    diff = measureDate - mktStartDate
    diffDays, diffSeconds = diff.days, diff.seconds
    return diffDays * 24 + diffSeconds // 3600 - 1

tweets_df['mktHourOrig'] = tweets_df['hour'].apply(convertDateToMktHour)
tweets_df['mktWeek'] = tweets_df['mktHourOrig'] // mktHours
tweets_df['mktHour'] = tweets_df['mktHourOrig'] % mktHours

#%%

tweets_df_pivot = tweets_df[['mktWeek','mktHour','tweets']].copy()
tweets_df_pivot = tweets_df_pivot[tweets_df_pivot['mktWeek']>-11]
tweets_df_pivot = tweets_df_pivot.pivot(index='mktHour', columns = 'mktWeek', values = 'tweets')

tweets_df_pivotcumu = tweets_df_pivot.cumsum()

#%%
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
#print(tweets_df_graphing [tweets_df_graphing['mktWeek']==-3])
print(tweets_df_pivot)
print(tweets_df_pivotcumu)
tweets_df_pivotcumu.plot.line()
pd.set_option('display.max_rows', 10)
pd.set_option('display.max_columns', 3)


#%%


def returnNowMktHour():
    
    now = datetime.now()
    now = now.replace(minute=0,second=0,microsecond=0)
    now = timezone('America/New_York').localize(now)
    now_mkt = convertDateToMktHour(now)
    return(now_mkt)

#%%
hist_diff = []
hist_pctdiff = []
now_ref = returnNowMktHour()
for column in tweets_df_pivotcumu:
    if column == 0:
        break
    diff = tweets_df_pivotcumu[column].iloc[-1] - tweets_df_pivotcumu[column].iloc[now_ref]
    pctdiff = tweets_df_pivotcumu[column].iloc[-1] / tweets_df_pivotcumu[column].iloc[now_ref]
    hist_diff.append(diff)
    hist_pctdiff.append(pctdiff)

hist_diff_mean = mean(hist_diff)
hist_diff_stdev = statistics.pstdev(hist_diff)

hist_pctdiff_mean = mean(hist_pctdiff)
hist_pctdiff_stdev = statistics.pstdev(hist_pctdiff)

#%%

tweets_current = tweets_df_pivotcumu[0].iloc[now_ref]

tweets_fcst_diff = tweets_current + hist_diff_mean
tweets_fcst_diff_upstdev = tweets_fcst_diff + hist_diff_stdev
tweets_fcst_diff_dnstdev = tweets_fcst_diff - hist_diff_stdev

tweets_fcst_pctdiff = tweets_current * hist_pctdiff_mean
tweets_fcst_pctdiff_upstdev = tweets_current * (hist_pctdiff_mean + hist_pctdiff_stdev)
tweets_fcst_pctdiff_dnstdev = tweets_current * (hist_pctdiff_mean - hist_pctdiff_stdev)

tweets_fcst_diff = int(round(tweets_fcst_diff))
tweets_fcst_diff_upstdev = int(round(tweets_fcst_diff_upstdev))
tweets_fcst_diff_dnstdev = int(round(tweets_fcst_diff_dnstdev))
tweets_fcst_pctdiff = int(round(tweets_fcst_pctdiff))
tweets_fcst_pctdiff_upstdev = int(round(tweets_fcst_pctdiff_upstdev))
tweets_fcst_pctdiff_dnstdev = int(round(tweets_fcst_pctdiff_dnstdev))


summ1 = 'Current tweet count:' + str(tweets_current)
summ2 = 'Forecast, using simple average:' + str(tweets_fcst_diff) + ' Range:' + str(tweets_fcst_diff_dnstdev) + '-' + str(tweets_fcst_diff_upstdev)
summ3 = 'Forecast, using percent growth:' + str(tweets_fcst_pctdiff) + ' Range:' + str(tweets_fcst_pctdiff_dnstdev) + '-' + str(tweets_fcst_pctdiff_upstdev)

print(summ1)
print(summ2)
print(summ3)

#%%
x_axis = tweets_df_pivotcumu.index.tolist()
y_axis1 = tweets_df_pivotcumu[-1].tolist()
y_axis0 = tweets_df_pivotcumu[0].tolist()

#%%

outputGraph_file = 'Dash_Files/cumuTweets_' + user + '.csv'
tweets_df_pivotcumu.to_csv(outputGraph_file)

#%%
outputStatus_dict = {}

outputStatus_dict['tweets_current'] =               tweets_current
outputStatus_dict['tweets_fcst_diff'] =             tweets_fcst_diff
outputStatus_dict['tweets_fcst_diff_dnstdev'] =     tweets_fcst_diff_dnstdev
outputStatus_dict['tweets_fcst_diff_upstdev'] =     tweets_fcst_diff_upstdev
outputStatus_dict['tweets_fcst_pctdiff'] =          tweets_fcst_pctdiff
outputStatus_dict['tweets_fcst_pctdiff_dnstdev'] =  tweets_fcst_pctdiff_dnstdev
outputStatus_dict['tweets_fcst_pctdiff_upstdev'] =  tweets_fcst_pctdiff_upstdev

outputStatus_file = 'Dash_Files/outputStatus_' + user + '.txt'
f = open(outputStatus_file,'w')
f.write(str(outputStatus_dict))
f.close()

#%%
