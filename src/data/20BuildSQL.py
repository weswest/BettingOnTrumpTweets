#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 08:26:14 2020

@author: jonathanwest
"""

##%%
#import mysql.connector
#
#mydb = mysql.connector.connect(
#  host="localhost",
#  user="root",
#  passwd="password"
#)
#
#print(mydb)
#
#
##%%
#
#mycursor = mydb.cursor()
#mycursor.execute("CREATE DATABASE twitdb")
#
##%%
#mycursor.execute("SHOW DATABASES")
#for x in mycursor:
#  print(x)
#
#%%

import mysql.connector
from datetime import datetime,timedelta


db = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="password",
  database="twitdb"
)
cursor = db.cursor()
#%%


#sql = '''CREATE TABLE tweets (
# id INT AUTO_INCREMENT PRIMARY KEY,
# tweet_id BIGINT UNSIGNED UNIQUE,
# tweet_id_str varchar(255),
# screen_name varchar(255),
# created_at_UTC timestamp,
# created_at_ET timestamp,
# source varchar(255),
# retweet_original_ET timestamp,
# retweet_bool BOOLEAN,
# hashtags varchar(255),
# mentions varchar(255),
# text text
#)'''

#cursor.execute(sql)
#sql = "DROP TABLE IF EXISTS tweets"

#%%


cursor.execute('DROP TABLE IF EXISTS hours_db')
sql = '''
CREATE TABLE hours_db (
  hours DATETIME NOT NULL PRIMARY KEY,
  ct int
  )
'''
cursor.execute(sql)


#%%
startStr =  '2015-01-01 00:00:00'
endStr =    '2035-01-01 00:00:00'

startDate = datetime.strptime(startStr, "%Y-%m-%d %H:%M:%S")
endDate =   datetime.strptime(endStr, "%Y-%m-%d %H:%M:%S")

startTuple = (startDate,0)
endTuple = (endDate,0)
#%%

Dates = []
Dates.append(startTuple)

trackDate = startDate
i = 0
while trackDate < endDate:
    trackDate = trackDate + timedelta(hours=1)
    trackTuple = (trackDate,0)
    Dates.append(trackTuple)
    i = i+1
    if i % 5000 == 0:
        print(i,trackDate)

print(len(Dates))
print(Dates)

#%%
sql = """INSERT IGNORE INTO hours_db (hours, ct)
            VALUES (%s, %s)"""

cursor.executemany(sql,Dates)
db.commit()

cursor.close()
db.close()
