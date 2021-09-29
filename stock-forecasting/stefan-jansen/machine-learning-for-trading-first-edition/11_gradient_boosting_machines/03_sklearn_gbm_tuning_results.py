#!/usr/bin/env python
# coding: utf-8

# # Evaluation of the GBM GridSearchCV results

# This file illustrates how to evaluate the [GridSearchCV](http://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html) results for sklearn's [GradientBoostingClassifier](http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.GradientBoostingClassifier.html) obtained after first running `sklearn_gbm_tuning.py` in this directory to test various hyperparameter combinations and store the result.

# ## Imports & Settings

# In[1]:


get_ipython().run_line_magic('matplotlib', 'inline')

import warnings
from pathlib import Path
import os
from datetime import datetime
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns
import graphviz

from statsmodels.api import OLS, add_constant
from sklearn.tree import DecisionTreeRegressor, export_graphviz
from sklearn.metrics import roc_auc_score
from sklearn.externals import joblib


# In[2]:


warnings.filterwarnings('ignore')
sns.set_style("whitegrid")
np.random.seed(42)
pd.options.display.float_format = '{:,.4f}'.format


# In[3]:


with pd.HDFStore('model_tuning.h5') as store:
    test_feature_data = store['holdout/features']
    test_features = test_feature_data.columns
    test_target = store['holdout/target']


# ## GBM GridsearchCV with sklearn

# Need OneStepTimeSeriesSplit because stored GridSearchCV result expects it

# In[4]:


class OneStepTimeSeriesSplit:
    """Generates tuples of train_idx, test_idx pairs
    Assumes the index contains a level labeled 'date'"""

    def __init__(self, n_splits=3, test_period_length=1, shuffle=False):
        self.n_splits = n_splits
        self.test_period_length = test_period_length
        self.shuffle = shuffle
        self.test_end = n_splits * test_period_length

    @staticmethod
    def chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def split(self, X, y=None, groups=None):
        unique_dates = (X.index
                        .get_level_values('date')
                        .unique()
                        .sort_values(ascending=False)
                        [:self.test_end])

        dates = X.reset_index()[['date']]
        for test_date in self.chunks(unique_dates, self.test_period_length):
            train_idx = dates[dates.date < min(test_date)].index
            test_idx = dates[dates.date.isin(test_date)].index
            if self.shuffle:
                np.random.shuffle(list(train_idx))
            yield train_idx, test_idx

    def get_n_splits(self, X, y, groups=None):
        return self.n_splits


# ### Load Result

# Need to first run `sklearn_gbm_tuning.py` to perform gridsearch and store result (not included due to file size).

# In[ ]:


gridsearch_result = joblib.load('gbm_gridsearch.joblib')


# The GridSearchCV object has several additional attributes after completion that we can access after loading the pickled result to learn which hyperparameter combination performed best and its average cross-validation AUC score, which results in a modest improvement over the default values. This is shown in the following code:

# ### Best Parameters & AUC Score

# In[6]:


pd.Series(gridsearch_result.best_params_)


# In[7]:


f'{gridsearch_result.best_score_:.4f}'


# ### Evaluate best model

# #### Test on hold-out set

# In[8]:


best_model = gridsearch_result.best_estimator_


# In[9]:


preds= best_model.predict(test_feature_data)


# In[10]:


roc_auc_score(y_true=test_target, y_score=preds)


# #### Inspect global feature importance

# In[12]:


pd.Series(best_model.feature_importances_, index=test_features).plot.barh(figsize=(8,15));


# ### CV Train-Test Scores

# In[13]:


results = pd.DataFrame(gridsearch_result.cv_results_).drop('params', axis=1)
results.info()


# In[14]:


results.head()


# ### Get parameter values & mean test scores

# In[15]:


test_scores = results.filter(like='param').join(results[['mean_test_score']])
test_scores = test_scores.rename(columns={c: '_'.join(c.split('_')[1:]) for c in test_scores.columns})
test_scores.info()


# In[16]:


params = test_scores.columns[:-1].tolist()


# In[17]:


test_scores = test_scores.set_index('test_score').stack().reset_index()
test_scores.columns= ['test_score', 'parameter', 'value']
test_scores.head()


# In[18]:


test_scores.info()


# In[19]:


def get_test_scores(df):
    """Select parameter values and test scores"""
    data = df.filter(like='param').join(results[['mean_test_score']])
    return data.rename(columns={c: '_'.join(c.split('_')[1:]) for c in data.columns})


# ### Plot Test Scores vs Parameter Settings

# The GridSearchCV result stores the average cross-validation scores so that we can analyze how different hyperparameter settings affect the outcome.
# 
# The six seaborn swarm plots below show the distribution of AUC test scores for all parameter values. In this case, the highest AUC  test scores required a low learning_rate and a large value for max_features. Some parameter settings, such as a low learning_rate, produce a wide range of outcomes that depend on the complementary settings of other parameters. Other parameters are compatible with high scores for all settings use in the experiment:

# In[20]:


plot_data = get_test_scores(results).drop('min_impurity_decrease', axis=1)
plot_params = plot_data.columns[:-1].tolist()
plot_data.info()


# In[21]:


fig, axes = plt.subplots(ncols=3, nrows=2, figsize=(14, 6))
axes = axes.flatten()

for i, param in enumerate(plot_params):
    sns.swarmplot(x=param, y='test_score', data=plot_data, ax=axes[i])
    axes[i].set_ylim(.63, .69)
    
fig.suptitle('Mean Test Score Distribution by Hyper Parameter', fontsize=14)
fig.tight_layout()
fig.subplots_adjust(top=.9)
fig.savefig('mean_test_scores_by_param', dpi=300);


# ### Dummy-encode parameters

# In[22]:


data = get_test_scores(results)
params = data.columns[:-1].tolist()
data = pd.get_dummies(data,columns=params, drop_first=False)
data.info()


# ### Build Regression Tree

# We will now explore how hyperparameter settings jointly affect the mean cross-validation score. To gain insight into how parameter settings interact, we can train a DecisionTreeRegressor with the mean test score as the outcome and the parameter settings, encoded as categorical variables in one-hot or dummy format. 
# 
# The tree structure highlights that using all features (max_features_1), a low learning_rate, and a max_depth over three led to the best results, as shown in the following diagram:

# In[23]:


reg_tree = DecisionTreeRegressor(criterion='mse',
                                 splitter='best',
                                 max_depth=4,
                                 min_samples_split=5,
                                 min_samples_leaf=10,
                                 min_weight_fraction_leaf=0.0,
                                 max_features=None,
                                 random_state=42,
                                 max_leaf_nodes=None,
                                 min_impurity_decrease=0.0,
                                 min_impurity_split=None,
                                 presort=False)


# In[24]:


gbm_features = data.drop('test_score', axis=1).columns
reg_tree.fit(X=data[gbm_features], y=data.test_score)


# #### Visualize Tree

# In[25]:


out_file = 'results/gbm_sklearn_tree.dot'
dot_data = export_graphviz(reg_tree,
                          out_file=out_file,
                          feature_names=gbm_features,
                          max_depth=4,
                          filled=True,
                          rounded=True,
                          special_characters=True)
if out_file is not None:
    dot_data = Path(out_file).read_text()

graphviz.Source(dot_data)


# #### Compute Feature Importance

# Overfit regression tree to learn detailed rules that classify all samples

# In[71]:


reg_tree = DecisionTreeRegressor(criterion='mse',
                                 splitter='best',
                                 min_samples_split=2,
                                 min_samples_leaf=1,
                                 min_weight_fraction_leaf=0.0,
                                 max_features=None,
                                 random_state=42,
                                 max_leaf_nodes=None,
                                 min_impurity_decrease=0.0,
                                 min_impurity_split=None,
                                 presort=False)

gbm_features = data.drop('test_score', axis=1).columns
reg_tree.fit(X=data[gbm_features], y=data.test_score)


# The bar chart below displays the influence of the hyperparameter settings in producing different outcomes, measured by their feature importance for a decision tree that is grown to its maximum depth. Naturally, the features that appear near the top of the tree also accumulate the highest importance scores.

# In[85]:


gbm_fi = pd.Series(reg_tree.feature_importances_, index=gbm_features).sort_values(ascending=False)
gbm_fi = gbm_fi[gbm_fi > 0]
idx = [p.split('_') for p in gbm_fi.index]
gbm_fi.index = ['_'.join(p[:-1]) + '=' + p[-1] for p in idx]
gbm_fi.sort_values().plot.barh(figsize=(5,5))
plt.title('Hyperparameter Importance')
plt.tight_layout()
plt.savefig('param_importance', dpi=300);


# ### Run linear regression

# Alternatively, we can use a linear regression to gain insights into the statistical significance of the linear relationship between hyperparameters and test scores.

# In[75]:


data = get_test_scores(results)
params = data.columns[:-1].tolist()
data = pd.get_dummies(data,columns=params, drop_first=True)

model = OLS(endog=data.test_score, exog=add_constant(data.drop('test_score', axis=1))).fit(cov_type='HC3')
print(model.summary())


# In[ ]:




