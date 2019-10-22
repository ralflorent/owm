# -*- coding: utf-8 -*-
"""
Created on Jan 23 2019

@author: Angelo Rossi, Ralph Florent
"""
# this can be used for any data load and eventual plot, from composition, to spectral, time series (present example)
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

# define file path to load data from file
path = '../assets/data/'
filename = 'sample-time-series@task4.1.xlsx'

# load and show data from excel source
xl = pd.ExcelFile(path + filename)
xl.sheet_names

# parse into computationally operable data
df = xl.parse("sample-sheet-2")
df.head()

plt.plot(df.Date, df.B)
plt.title('Preview of the Sample')
plt.xlabel('Date (year)')
plt.ylabel('Units')
plt.show()

# query a subset of date greater than 2000
subset_from2000 = df.query('Date > "2000-07-1"')

# display a subset of the results
subset_from2000.head()

# Display the dimension of the subset
subset_from2000.shape

# Plot the subset of date greater than 2000
plt.plot(subset_from2000.Date, subset_from2000.B)
plt.title('Subset of Date > 2000')
plt.xlabel('Date (year)')
plt.ylabel('Units')
plt.show()