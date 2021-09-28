#!/usr/bin/env python
# coding: utf-8

# # Central Pivot Range (CPR)

# https://www.tradingview.com/script/EGsBWBpe-SD-Developing-Central-Pivot-Range/
# 
# https://pivotboss.com/2010/05/31/a-quick-guide-to-the-pivot-range/

# In[1]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings("ignore")

# fix_yahoo_finance is used to fetch data 
import fix_yahoo_finance as yf
yf.pdr_override()


# In[2]:


# input
symbol = 'AAPL'
start = '2018-08-01'
end = '2019-01-01'

# Read data 
df = yf.download(symbol,start,end)

# View Columns
df.head()


# In[3]:


df['Pivot'] = (df['High'] + df['Low'] + df['Adj Close']) / 3.0
df['BC'] = (df['High'] + df['Low']) / 2.0
df['TC'] = (df['Pivot'] - df['BC']) + df['Pivot']


# In[4]:


df.head()


# In[5]:


df.tail()


# In[7]:


plt.figure(figsize=(14,10))
plt.plot(df['Adj Close'])
plt.plot(df['TC'], label='Central Pivot Range')
plt.plot(df['Pivot'], label='Central Pivot Range')
plt.plot(df['BC'], label='Central Pivot Range')
plt.title('Stock '+ symbol +' Closing Price')
plt.ylabel('Price')
plt.legend(loc='best')


# ## Candlestick with Central Pivot Range (CPR)

# In[8]:


from matplotlib import dates as mdates
import datetime as dt

dfc = df.copy()
dfc['VolumePositive'] = dfc['Open'] < dfc['Adj Close']
#dfc = dfc.dropna()
dfc = dfc.reset_index()
dfc['Date'] = pd.to_datetime(dfc['Date'])
dfc['Date'] = dfc['Date'].apply(mdates.date2num)
dfc.head()


# In[21]:


from mpl_finance import candlestick_ohlc

fig = plt.figure(figsize=(32,25))
ax1 = plt.subplot(2, 1, 1)
ax1.plot(df['Pivot'], label='Pivot')
ax1.plot(df['BC'], label='BC')
ax1.plot(df['TC'], label='TC')
candlestick_ohlc(ax1,dfc.values, width=0.5, colorup='g', colordown='r', alpha=1.0)
ax1.xaxis_date()
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
ax1.grid(True, which='both')
ax1.minorticks_on()
ax1v = ax1.twinx()
colors = dfc.VolumePositive.map({True: 'g', False: 'r'})
ax1v.bar(dfc.Date, dfc['Volume'], color=colors, alpha=0.4)
ax1v.axes.yaxis.set_ticklabels([])
ax1v.set_ylim(0, 3*df.Volume.max())
ax1.set_title('Stock '+ symbol +' Closing Price')
ax1.set_ylabel('Price')
ax1.legend(loc='best')

