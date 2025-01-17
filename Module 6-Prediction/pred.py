import matplotlib.pyplot as plt
import os
import seaborn as sns
import numpy as np 
import pandas as pd 
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split,GridSearchCV
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, MinMaxScaler
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.neighbors import KNeighborsClassifier
# import tensorflow as tf
# import keras
# from keras.layers import Dense, Activation
# from keras.models import Sequential
# from keras import backend as K




# read the file
election_df=pd.read_csv('./LS_2.0.csv')
print('head is ',election_df.head())
# print('cols are ',election_df.columns)

#cleaning up the column names for better readability. convert to lower case remove escape characters.
for i in election_df.columns:
    x=i.lower().replace(' ','_').replace('\n','_').replace('__','_')
    election_df=election_df.rename(columns={i:x})

# print(election_df.columns)
print('Number of indian states: ',len(election_df['state'].unique()))
states=[]
num_constituency=[]
for i in election_df['state'].unique():
    states.append(i)
    num_constituency.append(len(election_df[election_df['state']==i]['constituency'].unique()))
# plt.figure(figsize=(20,8))
# plt.bar(x=states,height=num_constituency)
# plt.xlabel('states')
# plt.ylabel('number of constituencies')
# plt.title('number of constituencies in indian states in 2019')
# plt.xticks(rotation=90)
# plt.show()
# states=[]
# num_candidates=[]
# for i in election_df['state'].unique():
#     states.append(i)
#     num_candidates.append(len(election_df[election_df['state']==i]['name'].unique()))
# plt.figure(figsize=(20,8))
# plt.bar(x=states,height=num_candidates)
# plt.xlabel('states')
# plt.ylabel('number of candidates')
# plt.title('number of candidates in indian states in 2019')
# plt.xticks(rotation=90)
# plt.show()

# plt.figure(figsize=(15,8))
# election_df['winner'].value_counts().plot.pie(autopct='%.2f%%')
# plt.title('percentage of winners and losers')
# plt.ylabel('')
# plt.show()

# plt.figure(figsize=(20,8))
# sns.distplot(election_df['age'])
# plt.axvline(election_df['age'].mean(),color='red',label='mean')
# plt.axvline(election_df['age'].median(),color='blue',label='median')
# plt.axvline(election_df['age'].std(),color='green',label='std')
# plt.legend()
# plt.show()

# print('number of parties: ',len(election_df['party'].unique()))

# election_df['party'].value_counts()

# plt.figure(figsize=(15,8))
# election_df['gender'].value_counts().plot.pie(autopct='%.2f%%')
# plt.title('percentage of males and females')
# plt.ylabel('')

women_only=election_df[election_df['gender']=='FEMALE']
women_only['winner'].value_counts().plot.bar()
# plt.show()

print('75 women succeded from ',str(len(women_only)))

for i in women_only['state'].unique():
    print('state is : ',i)
    c=women_only[women_only['state']==i]
    for j,k,z in zip(c['name'],c['winner'],c['constituency']):
        if k==1:
            print('winner woman: ',j,' constituency: ',z)

election_df['education']=election_df['education'].str.replace('\n','')

# plt.figure(figsize=(15,8))
# election_df['education'].value_counts().plot.pie(autopct='%.2f%%')
# plt.title('Percentage of each edcational level of the participants in 2019 election')
# plt.ylabel('')
# plt.show()

for i in election_df['education'].unique():
    print('edcational level: ',i)
    c=election_df[election_df['education']==i]
    total=len(c)
    winners=0
    for j in c['winner']:
        if j==1:
            winners+=1
    if total>0:
        print(winners/total)

def change_val(x):
    # print("before x ",x)
    
    try:
        c = (x.split('Rs')[1].split('\n')[0].strip())
        
        c_2 = ''
        for i in c.split(","):
            # c_2 = i+c_2
            c_2 = c_2+i
        # print(" after x is ",c_2)    
        return c_2
    except:
        x = 0
        return x
election_df['assets'] = election_df['assets'].apply(change_val).astype('int')
election_df['liabilities'] = election_df['liabilities'].apply(change_val).astype('int')

winner_only=election_df[election_df['winner']==1]
comp_dict={}
for i,j,k in zip(winner_only['name'],winner_only['assets'],winner_only['liabilities']):
    comp_dict[i]=j-k
print(comp_dict)

#drop the winner column y-target
x=election_df.drop('winner',axis=1)
y=election_df['winner']

#split 80-20
x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=0.2,random_state=4)

print(x_train.shape,y_train.shape)
print(x_test.shape,y_test.shape)

#drop these columns
cols_to_remove=['name','general_votes','postal_votes','over_total_electors_in_constituency','over_total_votes_polled_in_constituency','total_electors']
x_train=x_train.drop(cols_to_remove,axis=1)
x_test=x_test.drop(cols_to_remove,axis=1)

#preprocess / cleaning replace unknowns with 0
def replacing(x):
    if x=='Not Available':
        x=x.replace('Not Available','0')
        x=int(x)
    else:
        return x
    return x

def convert_nan(x):
    if x==0:
        return np.nan
    else:
        return x 
    
x_train['criminal_cases']=x_train['criminal_cases'].apply(replacing).apply(convert_nan)
x_test['criminal_cases']=x_test['criminal_cases'].apply(replacing).apply(convert_nan)
x_train['criminal_cases']=x_train['criminal_cases'].astype('float')
x_test['criminal_cases']=x_test['criminal_cases'].astype('float')

for i,j in zip(x_train.columns,x_test.columns):
    if x_train[i].dtype=='object':
        x_train[i]=x_train[i].str.lower()
    if x_test[j].dtype=='object':
        x_test[j]=x_test[j].str.lower()

x_train['age']=x_train['age'].fillna(x_train['age'].median())
x_test['age']=x_test['age'].fillna(x_test['age'].median())
x_train['symbol']=x_train['symbol'].fillna('Unknown')
x_test['symbol']=x_test['symbol'].fillna('Unknown')

x_train['category']=x_train['category'].fillna('Unknown')
x_test['category']=x_test['category'].fillna('Unknown')
x_train['education']=x_train['education'].fillna('Not Available')
x_test['education']=x_test['education'].fillna('Not Available')

x_train['gender']=x_train['gender'].fillna('Unknown')
x_test['gender']=x_test['gender'].fillna('Unknown')
x_train['assets']=x_train['assets'].fillna(0)
x_test['assets']=x_test['assets'].fillna(0)

x_train['liabilities']=x_train['liabilities'].fillna(0)
x_test['liabilities']=x_test['liabilities'].fillna(0)
x_train['criminal_cases']=x_train['criminal_cases'].fillna(0)
x_test['criminal_cases']=x_test['criminal_cases'].fillna(0)

#Check categorical columns for cardinality
for i in x_train.columns:
    if x_train[i].dtype=='object':
        print(i,': ',str(len(x_train[i].unique())))

#if object may cause issues.Col perform one hot conding if its not a number. Unecessary stuff getting added. Separate objects and numeric ones(number).
object_cols = [col for col in x_train.columns if x_train[col].dtype == "object"]
numeric_cols=[col for col in x_train.columns if x_train[col].dtype !='object']

#store in low_card_cols if col has 130 unique values then its low_card_cols and then drop it. 130- brute force gave best value. Separate cols with too many unknown values or less contributions. High cardinality -eg name too many values. Very high dimensionality. High card cols are const names,cand names. objects-- strings. Not taking high cardinality values for specifically not int and non float values. Drop high cardinality values. low cards are impos.
low_card_cols = [col for col in object_cols if x_train[col].nunique() < 130]
high_card_cols = list(set(object_cols)-set(low_card_cols))

print("before ",x_train.head)
#output a non-sparse matrix. convert to attributes with yes or no. prevent algo from doing unecessary operations on objects.
OH_encoder=OneHotEncoder(handle_unknown='ignore', sparse=False)

#perform onehotencoder on both test and train frames for low cords. more useful version than x
OH_cols_train = pd.DataFrame(OH_encoder.fit_transform(x_train[low_card_cols]))
OH_cols_test = pd.DataFrame(OH_encoder.transform(x_test[low_card_cols]))

#onehotencoder ruins the index so fix it back. copy the index
OH_cols_train.index = x_train.index
OH_cols_test.index = x_test.index

# print("after ",x_train.head)
# print(OH_cols_train.head)

#drop the initial lowcordcols and concat it with the more useful oh_cols
x_train = x_train.drop(low_card_cols, axis=1)
x_test = x_test.drop(low_card_cols, axis=1)

# Add one-hot encoded columns to numerical features as they have more useful contents.
x_train = pd.concat([x_train, OH_cols_train], axis=1)
x_test = pd.concat([x_test, OH_cols_test], axis=1)

# print("concat ",x_train.head)

# tested this part--- found constituency to be a bad column as it had all unique values.
good_label_cols=[i for i in high_card_cols if set(x_train[i])==set(x_test[i])]
bad_label_cols=list(set(high_card_cols)-set(good_label_cols))

print('bad label cols ',bad_label_cols)

print('good_label_cols ',good_label_cols)

#drop constituency as its a bad column not much contribution. axis 1 row wise. one row at a time. 0-col wise.
x_train=x_train.drop('constituency',axis=1)
x_test=x_test.drop('constituency',axis=1)

#'criminal_cases', 'age', 'assets', 'liabilities', 'total_votes' are numeric cols.
print('numeric cols ',numeric_cols)
print('low card cols ',low_card_cols)
print('high card cols ',high_card_cols)
print('object cols ',object_cols)

#min max normalization. Convert it to range of 0-1. min value is 0 and max is 1. Relationship between the values is not lost but is given a intermediary corresponding value. Much easier to handle. Every value between 0-1. 
for i in numeric_cols:
    x_train[i]=((x_train[i]-x_train[i].min())/(x_train[i].max()-x_train[i].min()))
    x_test[i]=((x_test[i]-x_test[i].min())/(x_test[i].max()-x_test[i].min()))

def select_model():
    models=[{
        'name':'LogisticRegression',
        'estimator':LogisticRegression(),
        'hyperparameters':{
            'solver':["newton-cg", "lbfgs", "liblinear"]
        }
    # },
    # {
    #     'name':'KNeighborsClassifier',
    #     'estimator':KNeighborsClassifier(),
    #     'hyperparameters':{
    #         "n_neighbors": range(1,20,2),
    #         "weights": ["distance", "uniform"],
    #         "algorithm": ["ball_tree", "kd_tree", "brute"],
    #         "p": [1,2]
    #     }
    # },
    # {
    #     'name':'RandomForestClassifier',
    #     'estimator':RandomForestClassifier(),
    #     'hyperparameters':{
    #         "n_estimators": [4, 6, 9],
    #         "criterion": ["entropy", "gini"],
    #         "max_depth": [2, 5, 10],
    #         "max_features": ["log2", "sqrt"],
    #         "min_samples_leaf": [1, 5, 8],
    #         "min_samples_split": [2, 3, 5]
    #     }
    }
        
    ]

    # used this to  figure which model is best. gave logistic as the best one and solver as liblinear.
#     for i in models:
#         print(i['name'])
#         grid=GridSearchCV(i['estimator'],
#                           param_grid=i['hyperparameters'],
#                           cv=10,
#                           scoring='roc_auc')
#         grid.fit(x_train,y_train)
#         i["best_params"] = grid.best_params_
#         i["best_score"] = grid.best_score_
#         i["best_model"] = grid.best_estimator_

#         print("Best Score: {}".format(i["best_score"]))
#         print("Best Parameters: {}\n".format(i["best_params"]))

#     return models

# select_model()

lr=LogisticRegression(solver='liblinear')
lr.fit(x_train,y_train)
pred=lr.predict(x_test)

print('roc_auc_score is ',roc_auc_score(y_test,pred))
print('f1-score is ' ,f1_score(y_test,pred))
