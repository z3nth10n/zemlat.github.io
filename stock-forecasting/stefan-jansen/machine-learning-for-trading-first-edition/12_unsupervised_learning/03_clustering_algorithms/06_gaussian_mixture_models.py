#!/usr/bin/env python
# coding: utf-8

# # Gaussian Mixture Models

# Gaussian mixture models (GMM) are a generative model that assumes the data has been generated by a mix of various multivariate normal distributions. The algorithm aims to estimate the mean & covariance matrices of these distributions.
# 
# It generalizes the k-Means algorithm: it adds covariance among features so that clusters can be ellipsoids rather than spheres, while the centroids are represented by the means of each distribution. The GMM algorithm performs soft assignments because each point has a probability to be a member of any cluster. 

# ## The Expectation-Maximization Algorithm

# Expectation-Maximization Algorithm
# 
# GMM uses the expectation-maximization algorithm to identify the components of the mixture of Gaussian distributions. The goal is to learn the probability distribution parameters from unlabeled data.
# 
# The algorithm proceeds iteratively as follows:
# 1. Initialization: Assume random centroids (e.g. from K-Means)
# 2. Repeat until convergence (changes in assignments drop below threshold):
#     1. Expectation Step: Soft assignment - compute probabilities for each point from each distribution
#     2. Maximization Step: Adjust normal-distribution parameters to make data points most likely

# ## Imports & Settings

# In[1]:


get_ipython().run_line_magic('matplotlib', 'inline')
import warnings
import matplotlib.pyplot as plt
from matplotlib import cm
import pandas as pd
import numpy as np
from numpy import atleast_2d
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture
from sklearn.metrics import adjusted_mutual_info_score
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import load_iris
from mpl_toolkits.mplot3d import Axes3D


# In[2]:


cmap = cm.get_cmap('viridis')
pd.options.display.float_format = '{:,.2f}'.format
warnings.filterwarnings('ignore')


# ## Load Iris Data

# In[3]:


iris = load_iris()
iris.keys()


# ## Create DataFrame

# In[4]:


features = iris.feature_names
data = pd.DataFrame(data=np.column_stack([iris.data, iris.target]), 
                    columns=features + ['label'])
data.label = data.label.astype(int)
data.info()


# ### Standardize Data

# In[5]:


scaler = StandardScaler()
features_standardized = scaler.fit_transform(data[features])
n = len(data)


# ### Reduce Dimensionality to visualize clusters

# In[6]:


pca = PCA(n_components=2)
features_2D = pca.fit_transform(features_standardized)


# In[7]:


ev1, ev2 = pca.explained_variance_ratio_
ax = plt.figure().gca(title='2D Projection', 
                      xlabel='Explained Variance: {:.2%}'.format(ev1), 
                      ylabel='Explained Variance: {:.2%}'.format(ev2))
ax.scatter(*features_2D.T, c=data.label, s=10);


# ## Perform GMM clustering

# In[8]:


n_components = 3
gmm = GaussianMixture(n_components=n_components)
gmm.fit(features_standardized)
data['clusters'] = gmm.predict(features_standardized)
fig, axes = plt.subplots(ncols=2)
labels, clusters = data.label, data.clusters
mi = adjusted_mutual_info_score(labels, clusters)
axes[0].scatter(*features_2D.T, c=data.label, s=10)
axes[0].set_title('Original Data')
axes[1].scatter(*features_2D.T, c=data.clusters, s=10)
axes[1].set_title('Clusters | MI={:.2f}'.format(mi))


# ### Visualize Gaussian Distributions

# The following figures show the GMM cluster membership probabilities for the iris dataset as contour lines:

# In[9]:


xmin, ymin = features_2D.min(axis=0)
xmax, ymax = features_2D.max(axis=0)

x = np.linspace(xmin, xmax, 500)
y = np.linspace(ymin, ymax, 500)
X, Y = np.meshgrid(x, y)

simulated_2D = np.column_stack([np.ravel(X), np.ravel(Y)])
simulated_4D = pca.inverse_transform(simulated_2D)
Z = atleast_2d(np.clip(np.exp(gmm.score_samples(simulated_4D)), a_min=0, a_max=1)).reshape(X.shape)


# In[10]:


fig, ax = plt.subplots()
ax.set_aspect('equal')
CS = ax.contour(X, Y, Z, cmap='Greens', alpha=.5)
CB = plt.colorbar(CS, shrink=0.8)
ax.scatter(*features_2D.T, c=data.label, s=15)
fig.tight_layout();


# In[11]:


fig = plt.figure()
ax = fig.gca(projection='3d')
ax.set_aspect('equal')
CS = ax.contourf3D(X, Y, Z, cmap='RdBu_r', alpha=.5)
CB = plt.colorbar(CS, shrink=0.8)
ax.scatter(*features_2D.T, c=data.label, s=15)
fig.tight_layout()
fig.savefig('gaussian3d', dpi=300)


# ### Bayesian Information Criterion 

# In[12]:


bic = {}
for n_components in range(2, 8):
    gmm = GaussianMixture(n_components=n_components)
    gmm.fit(features_standardized)
    bic[n_components] = gmm.bic(features_standardized)
pd.Series(bic)

