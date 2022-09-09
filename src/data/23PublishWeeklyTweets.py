#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 12 13:59:46 2020

@author: jonathanwest
"""

import plotly.graph_objects as go
from plotly.offline import download_plotlyjs, init_notebook_mode,  plot

import dash
from dash import dcc
from dash import html

import pandas as pd
import os



#%%
# Import the important information

user = 'realdonaldtrump'

inputGraph_file = 'data/processed/Dash_Files/cumuTweets_' + user + '.csv'
userGraphData = pd.read_csv(inputGraph_file)
userGraphData.set_index('mktHour',inplace=True)



inputStatus_file = 'data/processed/Dash_Files/outputStatus_' + user + '.txt'
f = open(inputStatus_file,'r')
data=f.read()
f.close()
userStatus = eval(data)

#%%


#%%

#pd.set_option('display.max_rows', None)
#pd.set_option('display.max_columns', None)
#print(userGraphData)
#userGraphData.plot.line()
#pd.set_option('display.max_rows', 10)
#pd.set_option('display.max_columns', 3)
#
#print(userStatus['tweets_current'])

#%%

# This builds the forecast table of tweets

headerColor = 'grey'
rowEvenColor = 'lightgrey'
rowOddColor = 'white'

forecastTable = go.Figure(data=[go.Table(
  header=dict(
    values=['','<b>Recorded</b>','<b>Deleted</b>','<b>Count</b>','<b>-1 StDev</b>','<b>+1 StDev</b>'],
    line_color='darkslategray',
    fill_color=headerColor,
    align=['left','center'],
    font=dict(color='white', size=12)
  ),
  cells=dict(
    values=[
      ['Engagements So Far', 'Estimated Engagements this Week:', '  - Pace-Based', '  - Additive', '  - Multiplicative'],
      [userStatus['tweets_current'], '', '', '', ''],
      [0, '', '', '', ''],
      [userStatus['tweets_current'], '', 'To Come', userStatus['tweets_fcst_diff'], userStatus['tweets_fcst_pctdiff']],
      ['','','',userStatus['tweets_fcst_diff_dnstdev'],userStatus['tweets_fcst_pctdiff_dnstdev']],
      ['','','',userStatus['tweets_fcst_diff_upstdev'],userStatus['tweets_fcst_pctdiff_upstdev']]],
    line_color='darkslategray',
    # 2-D list of colors for alternating rows
    fill_color = [[rowOddColor,rowEvenColor,rowOddColor, rowEvenColor,rowOddColor]*5],
    align = ['left', 'center'],
    font = dict(color = 'darkslategray', size = 11)
    ))
])

#plot(fig)

#%%
  
# This builds the tweet graph table
x_axis = userGraphData.index.tolist()
y_axis1 = userGraphData['-1'].tolist()
y_axis0 = userGraphData['0'].tolist()


Week0_trace = dict(
    x = x_axis,
    y = userGraphData['0'],
    mode = 'lines',
    type = 'scatter',
    name = 'Current Week',
    line = dict(shape = 'linear', width = 4)
)

tweetWeeks = [Week0_trace]

for col in reversed(userGraphData.columns):
    if col == '0':
        continue
    if col == '-1':
        width_touse = 3
        dash_touse = 'dash'
        name_touse = 'Last Week'
    else:
        width_touse = 2
        dash_touse = 'dot'
        name_touse = str(int(col) * -1) + ' Weeks Ago'
    col_trace = dict(
        x = x_axis,
        y = userGraphData[col],
        mode = 'lines',
        type = 'scatter',
        name = name_touse,
        line = dict(shape = 'linear', width = width_touse, dash = dash_touse)
    )
    tweetWeeks.append(col_trace)

# Setting up the layout settings in the "layout" argument
layout =  dict(
    xaxis = dict(title = 'Hour'),
    yaxis = dict(title = 'Engagements'),
    margin = dict(
        l=70,
        r=10,
        b=10,
        t=10
    )
)

tweetGraph = go.Figure(data = tweetWeeks, layout = layout)
#plot(tweetGraph)

#%%


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Ride the Waves'),

    html.Div(children='''
        A Trump Social Media Engagement Tracker
    '''),
    dcc.Graph(figure = tweetGraph),
    dcc.Graph(figure = forecastTable)
])

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader = False, port=8051)