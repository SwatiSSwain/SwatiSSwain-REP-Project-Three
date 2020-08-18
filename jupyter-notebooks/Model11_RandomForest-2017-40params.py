#!/usr/bin/env python
# coding: utf-8

# In[1]:


from sklearn import tree
import pandas as pd
import os


# In[2]:


# SQL Alchemy
from sqlalchemy import create_engine


# In[3]:


# Create Engine for employee db
engine = create_engine('postgres://sxwlsbsllohawb:4723d0dab89d2da6bf1aae12930fd6865874a185e4e4dca60e5af580ccd1a185@ec2-52-200-48-116.compute-1.amazonaws.com:5432/d7shhrp5hdjs4d')
#engine = create_engine('postgresql://swain:db@localhost:5432/world_happiness')
connection = engine.connect()


# In[4]:


indicators_df = pd.read_sql("select * from happiness_indicators_final", connection)
                              
indicators_df.head() 


# In[5]:


pivot_df = indicators_df.pivot(index='countryname', columns='indicatorname', values='value')


# In[6]:


pivot_df.head()


# In[7]:


pivot_df=pivot_df.dropna(how='any')


# In[8]:


pivot_df.count()


# In[9]:


target_groups_df = pd.read_sql("SELECT distinct countryname,target_groups  from happiness_indicators_final", connection)
                              
target_groups_df.head() 


# In[10]:


merged_df = pd.merge(pivot_df, target_groups_df 
                   ,left_on="countryname"
                   ,right_on = "countryname"
                   ,how="inner")


# In[11]:


merged_df.head()


# In[12]:


target = merged_df["target_groups"]
target.head()


# In[13]:


target_names = pd.read_sql("SELECT distinct target_groups  from happiness_indicators_final", connection)
target_names


# In[14]:


data = merged_df.drop(["target_groups","countryname"], axis=1)


# In[15]:


feature_names = data.columns
data.head()


# In[16]:


data.count()


# In[17]:


from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(data, target, random_state=42)


# In[18]:


clf = tree.DecisionTreeClassifier()
clf = clf.fit(X_train, y_train)
clf.score(X_test, y_test)


# In[19]:


from sklearn.ensemble import RandomForestClassifier
rf = RandomForestClassifier(n_estimators=100)
rf = rf.fit(X_train, y_train)
rf.score(X_test, y_test)


# In[20]:


sorted(zip(rf.feature_importances_, feature_names), reverse=True)


# In[21]:


import matplotlib.pyplot as plt
feats = {} # a dict to hold feature_name: feature_importance
for feature, importance in zip(data.columns, rf.feature_importances_):
    feats[feature] = importance #add the name/value pair 

importances = pd.DataFrame.from_dict(feats, orient='index').rename(columns={0: 'Gini-importance'})
importances.sort_values(by='Gini-importance').plot(kind='bar')#, rot=45)
# Save the figure
plt.savefig("../rf-graph.png")
plt.show()


# In[22]:



#append data to Postgres existing table
importances.to_sql('forest_importance', engine,if_exists='replace')


# In[30]:


model_score = rf.score(X_test, y_test)
model_score_df = pd.Series(model_score)


# In[31]:


#append data to Postgres existing table
model_score_df.to_sql('model_score', engine,if_exists='replace')


# In[23]:


from graphviz import Source
from sklearn import tree
Source(tree.export_graphviz(clf, out_file=None, feature_names=data.columns))


# In[24]:


#import pickle
#with open('rf-model.sav', 'wb') as f:
    #pickle.dump(rf, f)


# In[25]:


# in your prediction file   
#with open('rf-model.sav', 'rb') as f:
    #rf = pickle.load(f)
#preds = rf.predict(data)


# In[ ]:





# In[ ]:




