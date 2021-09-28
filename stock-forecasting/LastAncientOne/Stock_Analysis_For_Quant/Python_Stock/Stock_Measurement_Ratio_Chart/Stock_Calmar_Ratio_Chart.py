#!/usr/bin/env python
# coding: utf-8

# # Stock Calmar Ratio Chart

# In[1]:


# Library
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings("ignore")

from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override()


# In[2]:


start = '2019-01-01' #input
end = '2020-07-01' #input
symbol1 = '^GSPC' #input
symbol2 = 'AMD' #input


# In[3]:


market = yf.download(symbol1, start=start, end=end)['Adj Close']
stocks = yf.download(symbol2, start=start, end=end)['Adj Close']


# In[4]:


market_returns = market.pct_change().dropna()
stocks_returns = stocks.pct_change().dropna()


# In[5]:


# risk free
rf = yf.download('BIL', start=start, end=end)['Adj Close'].pct_change()[1:]


# In[6]:


def calmar_ratio(stock_returns, market_returns, rf):
    mrk_rate_ret = (market_returns[-1] - market_returns[0])/ market_returns[0]
    m = np.matrix([stock_returns, market_returns])
    beta = np.cov(m)[0][1] / np.std(market_returns)
    er = rf + beta*(mrk_rate_ret-rf)
    max_dd = 1.0 - (stock_returns / np.maximum.accumulate(stock_returns)).min()
    
    calmar_r = (er - rf) / max_dd
    return calmar_r


# In[7]:


# Compute the running Calmar ratio
running = [calmar_ratio(stocks_returns[i-90:i], market_returns[i-90:i], rf[i-90:i]) for i in range(90, len(stocks_returns))]

# Plot running Calmar ratio up to 100 days before the end of the data set
_, ax1 = plt.subplots(figsize=(12,8))
ax1.plot(range(90, len(stocks_returns)-100), running[:-100])
ticks = ax1.get_xticks()
ax1.set_xticklabels([stocks.index[int(i)].date() for i in ticks[:-1]]) # Label x-axis with dates
plt.title(symbol2 + ' Calmar Ratio')
plt.xlabel('Date')
plt.ylabel('Calmar Ratio')


# In[8]:


calmar_ratio(stocks_returns, market_returns, rf)


# In[9]:


calmar_ratio = calmar_ratio(stocks_returns, market_returns, rf)


# In[10]:


calmar_ratio .plot(figsize=(12,8), title = symbol1 + ' Calmar Ratio')
plt.axhline(y=calmar_ratio.mean(), color='r', linestyle='-')
plt.xlabel('Date')
plt.ylabel('Calmar Ratio')

