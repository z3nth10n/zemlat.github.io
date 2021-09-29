#!/usr/bin/env python
# coding: utf-8

# # Breadth Indicators

# Breadth Indicators include:
# 
# On Balance Volume
# 
# McClellan Summation Index
# Arms Index (TRIN)
# 
# Force Index
# 
# Chaikin Oscillator
# 
# Up/Down Volume Ratio
# 
# Up/Down Volume Spread
# 
# Cumulative Volume Index

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
symbol = 'SPY'
start = '2012-01-01'
end = '2019-01-01'

# Read data 
df = yf.download(symbol,start,end)

# View Columns
df.head()


# In[3]:


df['Adj Close'][1:]


# In[4]:


import talib as ta


# ## On Balance Volume

# In[5]:


OBV = ta.OBV(df['Adj Close'], df['Volume'])


# ## McClellan Summation Index Arms Index (TRIN)

# https://www.investopedia.com/terms/m/mcclellanoscillator.asp

# In[6]:


import quandl as q

# For NASDAQ
#Advances = q.get('URC/NASDAQ_ADV')['Numbers of Stocks']
#Declines = q.get('URC/nASDAQ_DEC')['Numbers of Stocks']   
#n = Advances - Declines


# In[7]:


Advances = q.get('URC/NYSE_ADV', start_date = "2017-07-27")['Numbers of Stocks']
Declines = q.get('URC/NYSE_DEC', start_date = "2017-07-27")['Numbers of Stocks']  


# In[8]:


adv_vol = q.get("URC/NYSE_ADV_VOL", start_date = "2017-07-27")['Numbers of Stocks']
dec_vol = q.get("URC/NYSE_DEC_VOL", start_date = "2017-07-27")['Numbers of Stocks']


# In[9]:


data = pd.DataFrame()
data['Advances'] = Advances
data['Declines'] = Declines
data['adv_vol'] = adv_vol
data['dec_vol'] = dec_vol


# In[10]:


data['Net_Advances'] = data['Advances'] - data['Declines'] 
data['Ratio_Adjusted'] = (data['Net_Advances']/(data['Advances'] + data['Declines'])) * 1000
data['19_EMA'] = ta.EMA(data['Ratio_Adjusted'], timeperiod=19)
data['39_EMA'] = ta.EMA(data['Ratio_Adjusted'], timeperiod=39)
data['RANA'] = (data['Advances'] - data['Declines']) / (data['Advances'] + data['Declines']) * 1000


# In[11]:


# Finding the TRIN Value
data['ad_ratio'] = data['Advances'].divide(data['Declines'] ) # AD Ratio
data['ad_vol'] = data['adv_vol'].divide(data['dec_vol']) # AD Volume Ratio
data['TRIN'] = data['ad_ratio'].divide(data['adv_vol']) # TRIN Value


# In[12]:


data.head()


# ## Force Index

# In[13]:


def ForceIndex(data,n):
    ForceIndex=pd.Series(df['Adj Close'].diff(n)* df['Volume'],name='ForceIndex')
    data = data.join(ForceIndex)
    return data


# In[14]:


n=10
ForceIndex = ForceIndex(data,n)
ForceIndex = ForceIndex['ForceIndex']


# In[15]:


fig=plt.figure(figsize=(7,5))
ax=fig.add_subplot(2,1,1)
ax.set_xticklabels([])
plt.plot(df['Adj Close'],lw=1)
plt.title('Market Price Chart')
plt.ylabel('Close Price')
plt.grid(True)
bx=fig.add_subplot(2,1,2)
plt.plot(ForceIndex,'k',lw=0.75,linestyle='-',label='Force Index')
plt.legend(loc=2,prop={'size':9.5})
plt.ylabel('Force Index')
plt.grid(True)
plt.setp(plt.gca().get_xticklabels(),rotation=30)
plt.show()


# ## Chaikin Oscillator

# In[16]:


def Chaikin(data):
    money_flow_volume = (2 * df['Adj Close'] - df['High'] - df['Low']) / (df['High'] - df['Low']) * df['Volume']  
    ad = money_flow_volume.cumsum()
    Chaikin = pd.Series(ad.ewm(com=(3-1)/2).mean() - ad.ewm(com=(10-1)/2).mean(), name='Chaikin')
    data = data.join(Chaikin)  
    return data


# In[17]:


Chaikin(df)


# ## Up/Down Volume Ratio

# Volume Spread = Up Volume - Down Volume 

# In[18]:


Up = q.get('URC/NYSE_ADV', start_date = "2017-07-27")['Numbers of Stocks']
Down = q.get('URC/NYSE_DEC', start_date = "2017-07-27")['Numbers of Stocks']
Volume_Spread = Up - Down


# In[19]:


Volume_Spread


# ## Up/Down Volume Spread

# Volume Ratio = Up Volume / Down Volume

# In[20]:


Up = q.get('URC/NYSE_ADV', start_date = "2017-07-27")['Numbers of Stocks']
Down = q.get('URC/NYSE_DEC', start_date = "2017-07-27")['Numbers of Stocks']
Volume_Ratio = Up/Down


# In[21]:


Volume_Ratio


# ## Cumulative Volume Index

# https://www.marketinout.com/technical_analysis.php?t=Cumulative_Volume_Index_(CVI)&id=38

# In[22]:


# CVI = Yesterday's CVI + (Advancing Volume - Declining Volume)
data['CVI'] = data['Net_Advances'][1:] + (data['Advances'] - data['Declines']) 


# In[23]:


data.head()
