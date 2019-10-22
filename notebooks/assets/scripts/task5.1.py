# -*- coding: utf-8 -*-
"""
Created on Jan 23 2019

@author: Angelo Rossi, Ralph Florent
"""
# Import relevant libraries
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import h5py

# define file path to load data from file
path = '../assets/data/hdf/'
filename = 'data-file@task4.3.hdf5'

# load and show data from hdf5 source
filepath = path + filename
file = h5py.File(filepath, 'r')
list(file.keys())

domain_10 = file['Domain_10']
list(domain_10)

ster_data = domain_10['STER']
list(ster_data)

dataset = ster_data['min_1']['boom_1']['temperature']
list(dataset.attrs)

# Distribute the data between date and mean (from columns)
from datetime import datetime

sample_date_mean = dataset['date', 'mean']
dates = [x[0] for x in sample_date_mean]
temps = [y[1] for y in sample_date_mean]
datesStr=["".join([chr(y) for y in x[:-2]]) for x in dates]
times = [datetime.strptime(d, '%Y-%m-%d %H:%M:%S') for d in datesStr]
print(times[:5])

plt.plot(times, temps)
plt.title('Preview of the Sample Date-Temperature')
plt.xlabel('Times ')
plt.ylabel('Temperature')
plt.show() 