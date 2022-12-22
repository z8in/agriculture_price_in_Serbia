import requests
from pandas.io.json import json_normalize
import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt

import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context
    
url = 'https://opendata.stat.gov.rs/data/WcfJsonRestService.Service1.svc/dataset/0306IND01/2/json'
dataset = pd.read_json(url)

dataset['vrednost'] = pd.to_numeric(dataset['vrednost'])
dataset['god'] = pd.to_numeric(dataset['god'])

# checking for names of agriculture products for translate to English
dataset['nProizvod'].unique()

#renaming agriculture products from Serbian to English

mapping = {'Pšenica':'Wheat', 
           'Ječam':'Barley', 
           'Kukuruz':'Corn', 
           'Ovas':'Oat', 
           'Raž':'Rye', 
           'Uljana repica':'Oilseed rape',
           'Šećerna repa':'Sugar beet', 
           'Suncokret':'Sunflower', 
           'Soja':'Soy', 
           'Duvan':'Tobacco', 
           'Krompir':'Potato',
           'Paradajz':'Tomato', 
           'Kupus i kelj':'Cabbage and kale', 
           'Crni luk':'Onion', 
           'Paprika':'Pepper', 
           'Pasulj':'Bean',
           'Dinje i lubenice':'Melon and Watermelon', 
           'Lucerka':'Alfalfa', 
           'Jabuke':"Apples", 
           'Kruške':'Pear', 
           'Šljive':'Plum',
           'Orasi':'Nuts', 
           'Grožđe':'Grapes', 
           'Jagode':'Strawberries', 
           'Maline':'Raspberries', 
           'Trešnje':'Cherries', 
           'Višnje':'Sour cherries',
           'Kajsije':'Apricots', 
           'Breskve':'Peach', 
           'mršave i mesnate svinje':'fleshy pigs',
           'masne i polumasne svinje':'fat pigs', 
           'Ovce - ukupno':'sheeps', 
           'Tovni pilići':'Chickens',
           'Kravlje mleko, mil.l':'Cow milk', 
           'Ovčije mleko, mil.l':'Sheep milk', 
           'Jaja, mil.kom.':'Eggs',
           'Vuna, t':'Wool', 
           'Med, t':'Honey'
           }

# after changing name of agriculture products
# list is printed for corrected values to be entered

dataset['nProizvod'] = dataset['nProizvod'].replace(mapping)
unique_names = dataset['nProizvod'].unique()
print("Here is a list of products for which you can check prices over the years: ")
print(unique_names)

# creating variable with name of product
product = str(input("Enter product name: "))
# selecting data with only selected product
cond = dataset.loc[dataset['nProizvod'] == product]
# creating new column with pecentage of price change for each row
cond['price relation to previous year'] = cond['vrednost'].pct_change().fillna(0)
# rounding values to 4 decimals for easy viewing
cond['price relation to previous year'] = cond['price relation to previous year'].round(4)
# dropping unnecessary columns 
cond = (cond.loc[:, ['nProizvod', 'god', 'vrednost', 'price relation to previous year']])

# putting all data into senteces for easy understanding
# and for extracting key data for prices over the year

max_price_decrease = cond['price relation to previous year'].min()
max_price_increase = cond['price relation to previous year'].max()
year_max_price_decrease = cond.loc[cond['price relation to previous year']==max_price_decrease, 'god'].values[0]
year_max_price_decrease_previous = year_max_price_decrease - 1
year_max_price_increase = cond.loc[cond['price relation to previous year']==max_price_increase, 'god'].values[0]
year_max_price_increase_previous = year_max_price_increase - 1
purchase_price_max_decrease = cond.loc[cond['price relation to previous year']==max_price_decrease, 'vrednost'].values[0]
purchase_price_max_decrease_previous = (purchase_price_max_decrease/(1 + max_price_decrease)).round(2)
purchase_price_max_increase = cond.loc[cond['price relation to previous year']==max_price_increase, 'vrednost'].values[0]
purchase_price_max_increase_previous = (purchase_price_max_increase/(1 + max_price_increase)).round(2)
print("For " + str(product) + " biggest decrease in price was in year " + str(year_max_price_decrease) + 
      " where price was " + str(purchase_price_max_decrease) + "rsd" + " which is total decrease of " + 
      str((max_price_decrease*100).round(2)) + "%" + " from previous year " + str(year_max_price_decrease_previous)
      + " where price was " + str(purchase_price_max_decrease_previous) + "rsd")
print("For " + str(product) + " biggest increase in price was in year " + str(year_max_price_increase) + 
      " where price was " + str(purchase_price_max_increase) + "rsd" + " which is total decrease of " + 
      str((max_price_increase*100).round(2)) + "%" + " from previous year " + str(year_max_price_increase_previous)
      + " where price was " + str(purchase_price_max_increase_previous) + "rsd")

year = dataset['god'].unique()

# creating bar plot
fig, ax = plt.subplots()
ax.bar(year, cond['vrednost'])
ax.set_xlabel('Year')
ax.set_ylabel('Price')
ax.set_title('Price of ' + str(product) + " from year " + str(dataset['god'].min()) + "-" + str(dataset['god'].max()))
plt.show()