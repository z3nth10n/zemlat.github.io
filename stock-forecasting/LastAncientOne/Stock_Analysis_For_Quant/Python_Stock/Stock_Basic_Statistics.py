#!/usr/bin/env python
# coding: utf-8

# # Basic Statistics in Python

# ## Statistical Analysis

# In[1]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import norm
import math

import warnings
warnings.filterwarnings("ignore")

# fix_yahoo_finance is used to fetch data 
import fix_yahoo_finance as yf
yf.pdr_override()


# In[2]:


# input
symbol = 'AAPL'
market = '^GSPC'
start = '2017-01-01'
end = '2019-01-01'

# Read data 
df = yf.download(symbol,start,end)
dfm = yf.download(market,start,end)

# View Columns
df.head()


# In[3]:


df.shape


# In[4]:


new_df = pd.DataFrame({symbol : df['Adj Close'], market : dfm['Adj Close']}, index=df.index)

# compute returns
new_df[['stock_returns','market_returns']] = new_df[[symbol,market]] / new_df[[symbol,market]].shift(1) -1
new_df = new_df.dropna()
covmat = np.cov(new_df["stock_returns"],new_df["market_returns"])

# calculate measures now
beta = covmat[0,1]/covmat[1,1]
alpha= np.mean(new_df["stock_returns"])-beta*np.mean(new_df["market_returns"])


# In[5]:


print('Beta:', beta)
print('Alpha:', alpha)


# In[6]:


close = df['Adj Close']


# ## Mean is the average

# In[7]:


mean = np.mean(close)
mean


# ## Median is the value of middlemost value

# In[8]:


median = np.median(close)
median


# ## Mode is the most frequent value

# In[9]:


mode = stats.mode(close)
print("The modal value is {} with a count of {}".format(mode.mode[0], mode.count[0]))


# ## Range is a measure of how spread apart the values are

# In[10]:


range_of_stock = np.ptp(close)
range_of_stock


# ## Variance is a measure of how variable the data is

# In[11]:


variance = np.var(close)
variance


# ## Standard deviation is the square root of the variance and is measure how the data is spread out

# In[12]:


standard_deviation = np.std(close)
standard_deviation


# ## Standard error is the mean (SE of the mean) estimates the variability between sample means that you would obtain if you took multiple samples from the same population

# In[13]:


standard_error = stats.sem(close)
standard_error


# ## Z-Scores measure how many standard deviations an element is from the mean

# In[14]:


z = np.abs(stats.zscore(close))
print(z)


# ##  Contingency Table shows correlations between two variables

# In[15]:


data_crosstab = pd.crosstab(df['High'], 
                            df['Low'],  
                               margins = False) 
print(data_crosstab) 


# ## Scatter plot shows two variables that plot along two axes and it shows correlation or not

# In[16]:


plt.scatter(df['Adj Close'], df['Open'], alpha=0.5)
plt.title('Adj Close vs Open')
plt.xlabel('Adj Close')
plt.ylabel('Open')
plt.show()


# ## Regression is a measure of the relation between the mean value of one variable (e.g. output) and corresponding values of other variables

# In[17]:


from sklearn.linear_model import LinearRegression

X = np.array(df['Open']).reshape(502,-1)
y = np.array(df['Adj Close'])
LR = LinearRegression().fit(X, y)
LR.score(X, y)


# In[18]:


LR.coef_


# In[19]:


LR.intercept_


# In[20]:


LR.predict(X)


# ## Elementary Probability Theory the outcome that could happen

# ### Monte Carlo method is an experimentals of computational algorithms that rely on repeated random samples. 

# In[21]:


df['Returns'] = df['Adj Close'].pct_change()
df['Returns'] = df['Returns'].dropna()


# In[22]:


values = []
S = df['Returns'][-1] #Starting stock price 
T = 252 #Number of trading days
mu = df['Returns'].mean() #Mean
sigma = df['Returns'].std()*math.sqrt(252) #Volatility


# In[23]:


for i in range(10000):
    # Create list of daily returns using random normal distribution
    daily_returns=np.random.normal(mu/T,sigma/math.sqrt(T),T)+1
    
    # Set starting price and create price series generated by above random daily returns
    price_list = [S]
    
    for x in daily_returns:
        price_list.append(price_list[-1]*x)

    # Plot the data
    plt.plot(price_list)
plt.show()


# ## Random variables and probability distributions

# https://www.investopedia.com/articles/06/probabilitydistribution.asp

# ### Cumulative Distribution 

# In[24]:


data = df['Adj Close']
values, base = np.histogram(data, bins=40)
#evaluate the cumulative
cumulative = np.cumsum(values)
# plot the cumulative function
plt.plot(base[:-1], cumulative, c='blue')
#plot the survival function
plt.plot(base[:-1], len(data)-cumulative, c='green')

plt.show()


# In[25]:


sorted_data = np.sort(data)  # Or data.sort(), if data can be modified

# Cumulative counts:
plt.step(sorted_data, np.arange(sorted_data.size))  # From 0 to the number of data points-1
plt.step(sorted_data[::-1], np.arange(sorted_data.size))  # From the number of data points-1 to 0

plt.show()


# ### Probability Density Function

# Probability Density Function (PDF) is continuous random variable and have value that is given sample in the sample space can be interpreted as providing a relative likelihood that the value of the random variable would equal that sample. (Wikipedia)

# In[26]:


values = df['Returns'][1:]
x = np.linspace(values.min(), values.max(), len(values))
loc, scale = stats.norm.fit(values)
param_density = stats.norm.pdf(x, loc=loc, scale=scale)
label = 'mean=%.4f, std=%.4f' % (loc, scale)

fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(values, bins=30, normed=True)
ax.plot(x, param_density, 'r-', label=label)
ax.legend(loc='best')
ax.set_title("Probability Density Function")


# In[27]:


sns.distplot(df['Returns'].dropna(),bins=100,color='red')


# ## Cumulative Probability Distribution

# In[28]:


values = df['Returns'][1:]
x = np.linspace(values.min(), values.max(), len(values))
loc, scale = stats.norm.fit(values)
param_density = stats.norm.cdf(x, loc=loc, scale=scale)
label = 'mean=%.4f, std=%.4f' % (loc, scale)

fig, ax = plt.subplots(figsize=(10, 6))
#ax.hist(values, bins=30, normed=True)
ax.plot(x, param_density, 'r-', label=label)
ax.legend(loc='best')
ax.set_title("Cumulative Probability Distribution")


# ## Binomial Distribution

# In[29]:


from scipy.stats import binom

n = len(df['Returns'])
p = df['Returns'].mean()
k = np.arange(0,21)
binomial = binom.pmf(k,n,p)

plt.plot(k, binomial, 'o-')
plt.title("Binomial: n=%i, p=%.2f" % (n,p), fontsize=15)
plt.xlabel("Number of successes", fontsize=15)
plt.ylabel("Probability of successes", fontsize=15)
plt.show()


# In[30]:


s = np.random.uniform(values.min(), values.max(), len(values))

import matplotlib.pyplot as plt
count, bins, ignored = plt.hist(s, 15, density=True)
plt.plot(bins, np.ones_like(bins), linewidth=2, color='r')
plt.show()


# In[31]:


binom_sim = binom.rvs(n = n, p = p, size=10000)
print("Mean: %f" % np.mean(binom_sim))
print("SD: %f" % np.std(binom_sim, ddof=1))
plt.hist(binom_sim, bins = 10, normed = True)
plt.xlabel("x")
plt.ylabel("Density")
plt.show()


# ## Poisson Distribution

# In[32]:


rate = 3 # Error Rate
n = np.arange(0,10) # Number of Trials
y = stats.poisson.pmf(n, rate)
y


# In[33]:


plt.plot(n, y, 'o-')
plt.title('Poisson: $\lambda$ =%i' % rate)
plt.ylabel('Probability Error')
plt.xlabel('Number of Errors (out of 100 trials)')
plt.show()


# In[34]:


data = stats.poisson.rvs(mu=3, loc=0, size=100)
print("Mean: %f" % np.mean(data))
print("Standard Deviation: %f" % np.std(data, ddof=1))

plt.hist(data, bins = 9, normed = True)
plt.xlim(0,10)
plt.xlabel('Number of Errors (out of 100 trials)')
plt.title('Simulating Poisson Random Variables')
plt.show()


# ## Beta Distribution

# In[35]:


alpha = alpha
beta = beta
x = np.arange(0, 1, 0.01)
y = stats.beta.pdf(x, alpha, beta)
plt.plot(x, y)
plt.title('Beta Distribution: alpha=%.1f, beta=%.1f' % (alpha,beta))
plt.xlabel('Range')
plt.ylabel('Probability density')
plt.show()


# ## Exponential Distribution

# In[36]:


lambd = 0.5 # lambda
x = np.arange(0, 1, 0.01)
y = lambd * np.exp(-lambd * x)
plt.plot(x, y)
plt.title('Exponential: $lambda\$ = %.2f' % lambd)
plt.xlabel("Range")
plt.ylabel("Probability density")
plt.show()


# ## Lognormal Distribution 

# In[37]:


from scipy.stats import lognorm

s = np.random.lognormal(mu, sigma, 1000)

count, bins, ignored = plt.hist(s, 100, normed=True, align='mid')
x = np.linspace(min(bins), max(bins), 10000)
pdf = (np.exp(-(np.log(x) - mu)**2 / (2 * sigma**2)) / (x * sigma * np.sqrt(2 * np.pi)))

plt.plot(x, pdf, linewidth=2, color='r')
plt.xlabel('Range')
plt.ylabel('Probability')
plt.axis('tight')
plt.show()

