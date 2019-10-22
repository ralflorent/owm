# Importing relevant libraries

%matplotlib inline
import matplotlib.pyplot as plt
import numpy as np

# Plotting a graph from the two given lists of T1.2

x = np.array([1, 4, 14, 16, 10, 132, 7, 4, 6.4, 6.3, 9.3, 23])
y = np.array([9, 11, 3.4, 3.4656, 6, 0.5, 8, 3, 4, 4.4, 6.3, 9.3])

# figure
fig = plt.figure()

# subplot
ax1 = fig.add_subplot(111)

# plot line
ax1.plot(x, y, 'r', color='r')

# plot markers on top
ax1.plot(x, y, marker='o', color='b', ls='')

plt.xlabel('X label')
plt.ylabel('Y label')

# show plot inline
plt.show()