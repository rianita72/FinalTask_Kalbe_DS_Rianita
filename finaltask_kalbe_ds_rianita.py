# -*- coding: utf-8 -*-
"""FinalTask_Kalbe_DS_Rianita.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Rwyws5rI8pat6tLBphjDlQkyf0zXtgNC

### Import Library
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn import preprocessing
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import SimpleExpSmoothing, Holt
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from math import sqrt

from pandas.plotting import autocorrelation_plot


import warnings
warnings.filterwarnings('ignore')

from google.colab import drive
drive.mount("/content/gdrive")

import os
os.chdir(r"/content/gdrive/My Drive")

"""### Data Exploration & Data Cleaning"""

import pandas as pd
df1 =  pd.read_csv('/content/gdrive/My Drive/kalbe/Product.csv', delimiter=';')

df1.sample(5)

df1.isnull().sum()

df1.duplicated().sum()

import pandas as pd
df2 =  pd.read_csv('/content/gdrive/My Drive/kalbe/Transaction.csv', delimiter=';')

df2.sample(5)

df2.isnull().sum()

df2.duplicated().sum()

import pandas as pd
df3 =  pd.read_csv('/content/gdrive/My Drive/kalbe/Store.csv', delimiter=';')

df3.sample(5)

df3.isnull().sum()

df3.duplicated().sum()

import pandas as pd
df4 =  pd.read_csv('/content/gdrive/My Drive/kalbe/Customer.csv', delimiter=',')

df4.sample(5)

df4.isnull().sum()

#impute missing data categorical

df4['Marital Status'].fillna(df4['Marital Status'].mode()[0], inplace=True)

df4.duplicated().sum()

# data cleansing income
df4['Income']=df4['Income'].replace('[,]','.', regex=True)

# data cleansing latitude, longitude

df3['Latitude']=df3['Latitude'].replace('[,]','.', regex=True)

df3['Longitude,,']=df3['Longitude,,'].replace('[,]','.', regex=True)

df2['Date']=pd.to_datetime(df2['Date'])

"""### Data Merge Altogether"""

df_merge = pd.merge(df1, df2.drop(columns=['Price']), on=['ProductID'])
df_merge = pd.merge(df_merge, df3, on=['StoreID'])
df_merge = pd.merge(df_merge, df4, on=['CustomerID'])

df_merge.head()

df_merge.value_counts()

# Groupby data by Date to time series modeling
df_new = df_merge.groupby(['Date']).agg({
         'Qty' : 'sum'
}).reset_index()

# load new data
df_new

# decomposed data
decomposed = seasonal_decompose(df_new.set_index('Date'))


plt.figure(figsize=(8,8))

plt.subplot(311)
decomposed.trend.plot(ax=plt.gca())
plt.title('Trend')

plt.subplot(312)
decomposed.seasonal.plot(ax=plt.gca())
plt.title('Seasonality')

plt.subplot(313)
decomposed.resid.plot(ax=plt.gca())
plt.title('Residuals')

plt.tight_layout()

# cek auto correlation
autocorrelation_plot(df_new['Qty'])

"""### Split Train-Test Data"""

# Split train test data

#set it as the index a data datetime
df_new['Date'] = pd.to_datetime(df_new['Date'])
df_new.set_index('Date', inplace=True)

# Split the data into a training set and a test set
train_size = int(len(df_new) * 0.8)  # Adjust the split ratio as needed
train_data, test_data = df_new[:train_size], df_new[train_size:]

# Plot the training and test data
plt.figure(figsize=(12, 6))
plt.plot(train_data, label='Training Data')
plt.plot(test_data, label='Test Data')
plt.title('Training-Test Data Split')
plt.xlabel('Date')
plt.ylabel('Value')
plt.legend()
plt.show()

train_data.shape,test_data.shape

"""### Cek Stationarity Data"""

# cek the stationarity data
from statsmodels.tsa.stattools import adfuller
result=adfuller (df_new)
print('Test Statistic: %f' %result[0])
print('p-value: %f' %result[1])
print('Critical values:')
for key, value in result[4].items ():
     print('\t%s: %.3f' %(key, value))

"""### ARIMA Modeling"""

def rmse(y_actual, y_pred):

  ####function to calculate rmse


  print(f'RMSE Value{mean_squared_error(y_actual, y_pred)**0.5}')


def eval(y_actual, y_pred):

  ####function to evaluation machine learning modelling


  print(f'MAE Value{mean_absolute_error(y_actual, y_pred)}')

#ARIMA Modeling

ARIMAModel = ARIMA(train_data, order = (40, 2, 1))
ARIMAModel = ARIMAModel.fit()

y_pred = ARIMAModel.get_forecast(len(test_data))


y_pred_df = y_pred.conf_int()
y_pred_df['prediction'] = ARIMAModel.predict(start= y_pred_df.index[0], end =y_pred_df.index[-1])
y_pred_df.index = test_data.index
y_pred_out = y_pred_df['prediction']
eval(test_data['Qty'], y_pred_out)

plt.figure(figsize=(20,5))

plt.plot(train_data['Qty'])
plt.plot(test_data['Qty'], color='red')
plt.plot(y_pred_out, color='black', label='ARIMA Predictions')
plt.legend()

# Plot residual errors
residuals = pd.y_pred_df(model_fit.resid)
fig, ax = plt.subplots(1,2)
residuals.plot(title="Residuals", ax=ax[0])
residuals.plot(kind='kde', title='Density', ax=ax[1])
plt.show()

"""### Clustering"""

# cek data
df_merge.head()

# cek korelasi antar data
df_merge.corr()

# Making new data groupby customerID
df_cluster = df_merge.groupby(['CustomerID']).agg({
             'TransactionID' : 'count',
             'Qty' : 'sum'
}).reset_index()

df_cluster.sample(5)

data_cluster = df_cluster.drop(columns=['CustomerID'])

data_cluster_normalize = preprocessing.normalize(data_cluster)

data_cluster_normalize

K = range(2, 8)
fits = []
score = []

for k in K:
  model =KMeans(n_clusters = k , random_state=0, n_init='auto').fit(data_cluster_normalize)

  fits.append(model)

  score.append(silhouette_score(data_cluster_normalize, model.labels_, metric='euclidean'))

# choose 4 cluster
sns.lineplot(x = K, y =score);

# Fits Model
fits[1]

df_cluster['cluster_label'] = fits[1].labels_

# Making new data after clustering
df_cluster.groupby(['cluster_label']).agg({
    'CustomerID' : 'count',
    'TransactionID' : 'mean',
    'Qty' : 'mean'
})

"""#### Conclusion:
Berdasarkan hasil clustering maka:

1. Cluster 0 :
   Yaitu pelanggan yang memiliki quantity atau jumlah pembelian barang dalam jumlah yang relatif sedang(tidak sedikit tetapi juga tidak terlalu banyak) tetapi dengan jumlah transaksi terbanyak.

2. Cluster 1 :
   Yaitu pelanggan yang memiliki quantity atau jumlah pembelian barang dengan jumlah paling sedikit diantara dua cluster lainnya tapi memiliki total transaksi yang sedang atau rata-rata.

3. Cluster 2 :
   Yaitu cluster dengan kelas terendah dimana pelanggan yang memiliki jumlah pembelian barang paling sedikit dan total transaksi yang paling sedikit
"""