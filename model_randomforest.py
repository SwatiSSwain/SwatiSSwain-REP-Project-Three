#!/usr/bin/env python
# coding: utf-8

# In[1]:


from sklearn import tree
import pandas as pd
import os


# In[2]:


# SQL Alchemy
from sqlalchemy import create_engine
import sqlalchemy
import psycopg2

# In[3]:

from urllib.parse import urlparse

#os.environ["DATABASE_URL"] = "postgres://sxwlsbsllohawb:4723d0dab89d2da6bf1aae12930fd6865874a185e4e4dca60e5af580ccd1a185@ec2-52-200-48-116.compute-1.amazonaws.com:5432/d7shhrp5hdjs4d"

if "DATABASE_URL" in os.environ :
    url = urlparse(os.environ.get('DATABASE_URL'))
    db = "dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname)
    schema = "schema.sql"
    conn = psycopg2.connect(db)
    #cur = conn.cursor()
else: 
    conn = psycopg2.connect(host="localhost", port = 5432, database="world_happiness")

cur = conn.cursor()


# Create Engine for employee db
#engine = create_engine('postgres://sxwlsbsllohawb:4723d0dab89d2da6bf1aae12930fd6865874a185e4e4dca60e5af580ccd1a185@ec2-52-200-48-116.compute-1.amazonaws.com:5432/d7shhrp5hdjs4d')
#engine = create_engine('postgresql://swain:db@localhost:5432/world_happiness')
#connection = engine.connect()


# In[4]:

#Dictionary to store all scrape data
collect_data = {}

def predict(predictor_list):
    
    #indicators_df = pd.read_sql("select * from happiness_indicators_final WHERE indicatorname in  %s;", ((predictor_list),), connection)
    #print(predictor_list)
    cur.execute("select * from happiness_indicators_final WHERE indicatorname in  %s;", ((predictor_list),))
    indicators_df = cur.fetchall()
    indicators_df=pd.DataFrame(indicators_df,columns = ['countryname' , 'indicatorname', 'value', 'target_groups'])
                                
  
# In[5]:


    pivot_df = indicators_df.pivot(index='countryname', columns='indicatorname', values='value')


    # In[6]:


    pivot_df.head()


    # In[7]:


    pivot_df=pivot_df.dropna(how='any')


    # In[8]:


    pivot_df.count()


    # In[9]:


    #target_groups_df = pd.read_sql("SELECT distinct countryname,target_groups  from happiness_indicators_final", connection)
    cur.execute("SELECT distinct countryname,target_groups  from happiness_indicators_final WHERE indicatorname in  %s;", ((predictor_list),))
    target_groups_df = cur.fetchall()
    target_groups_df=pd.DataFrame(target_groups_df,columns = ['countryname' ,  'target_groups'])
                                
    target_groups_df.head() 


    # In[10]:


    merged_df = pd.merge(pivot_df, target_groups_df 
                    ,left_on="countryname"
                    ,right_on = "countryname"
                    ,how="inner")



    # In[12]:


    target = merged_df["target_groups"]
    target.head()


    # In[13]:


    #target_names = pd.read_sql("SELECT distinct target_groups  from happiness_indicators_final", connection)
    cur.execute("SELECT distinct target_groups  from happiness_indicators_final WHERE indicatorname in  %s;", ((predictor_list),))
    target_names = cur.fetchall()
    target_names=pd.DataFrame(target_names,columns = ['target_groups'])
    target_names


    # In[14]:


    data = merged_df.drop(["target_groups","countryname"], axis=1)


    # In[15]:


    feature_names = data.columns

    # In[17]:


    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(data, target, random_state=42)


    # In[18]:


    #clf = tree.DecisionTreeClassifier()
    #clf = clf.fit(X_train, y_train)
    #clf.score(X_test, y_test)


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

    importances = pd.DataFrame.from_dict(feats, orient='index').rename(columns={0: 'Feature-importance'})
    importances=importances.sort_values(by='Feature-importance', ascending=False)
    #importances=importances.sort_values(by='Gini-importance').plot(kind='bar')
    # Save the figure
    #plt.savefig("rf-graph.png")
    #plt.show()



    importances_df=importances.reset_index()

    importances_df.columns = ['Predictors', 'Feature-importance']

    # Save html code 
    importances_html=importances_df.to_html(classes='table table-striped',header=['Predictors', 'Feature Importance'],index=False,justify='unset')

    #Save MARS fact html string

    collect_data['importances_html'] = importances_html


    # In[30]:


    model_score = rf.score(X_test, y_test)
    model_score_df = pd.Series(model_score)
    #Dictionary to store all scrape data
    collect_data['model_score'] = model_score

    #Logistic Regression
    # Scale your data
    # Import dependencies
    from sklearn.preprocessing import LabelEncoder, MinMaxScaler,StandardScaler
    #from tensorflow.keras.utils import to_categorical
    #from tensorflow import keras

    # scale the data
    X_scaler =  MinMaxScaler().fit(X_train)
    X_train_scaled = X_scaler.transform(X_train)
    X_test_scaled = X_scaler.transform(X_test)

    # Label-encode data set
    label_encoder = LabelEncoder()
    label_encoder.fit(y_train.values.ravel())
    encoded_y_train = label_encoder.transform(y_train.values.ravel())
    encoded_y_test = label_encoder.transform(y_test.values.ravel())

    # Create a logistic regression model
    from sklearn.linear_model import LogisticRegression
    model = LogisticRegression(solver='lbfgs',class_weight='balanced', max_iter=10000)
    model.fit(X_train_scaled, encoded_y_train)

    predictions = model.predict(X_test_scaled)

    # Calculate classification report
    from sklearn.metrics import classification_report
    clf_report = classification_report(encoded_y_test, predictions,
                                   target_names = target_names['target_groups'].values.tolist(),
                                   output_dict=True
                                   )

    clf_report=pd.DataFrame(clf_report)
    collect_data['clf_report'] = clf_report




    #from graphviz import Source
    #from sklearn import tree
    #Source(tree.export_graphviz(rf, out_file=None, feature_names=data.columns))


   
    #print(importances)
    return collect_data

# In[ ]:


#predict()


# In[ ]:




