# -*- coding: utf-8 -*-
"""
Created on Jan 24 2019

@author: Angelo Rossi, Ralph Florent
"""
# Import relevant libraries
import matplotlib
from matplotlib import pyplot as plt
%matplotlib inline

import numpy as np
import pandas as pd # we'll use pandas to load data
from scipy.interpolate import interp1d

# We'll be looking at phylosiclicates (clays), as they have a fairly complex spectra with many features:
# In the data_samples folder we have two spectra for Montmorillonite
PATH = '../assets/data/spectral_data/'
specSlPhyMontm = pd.read_csv(PATH + 'FRTC596_537-220-5x5_Al-phyllo_montm.txt', skipinitialspace=True, sep=' ',
                    skiprows=3, header=None)

relabMontm = pd.read_csv(PATH + 'montmorillonite-1292F35-RELAB.txt', skipinitialspace=True, sep=' ',
                      skiprows=3, header=None)
# also we have two spectra for Nontronite
specFePhyNontr = pd.read_csv(PATH + 'FRTC596_537-220-5x5_Fe-phyllo_nontr.txt', skipinitialspace=True, sep=' ',
                         skiprows=3, header=None)

relabNontr = pd.read_csv(PATH + 'nontronite-CBJB26-RELAB.txt', skipinitialspace=True, sep=' ',
                         skiprows=3, header=None)

specFePhyNontr[:5] # take a look at what our data looks like

# This worked, lets fix all dataframes now:
specSlPhyMontm = specSlPhyMontm.rename(columns={0:'wavelength',1:'specSlPhyMontm'})
relabMontm     = relabMontm.rename(columns={0:'wavelength',1:'relabMontm'})
specFePhyNontr = specFePhyNontr.rename(columns={0:'wavelength',1:'specFePhyNontr'})
relabNontr     = relabNontr.rename(columns={0:'wavelength',1:'relabNontr'})

#lets check:
relabNontr[:5]

#lets plot:
ax1 = specSlPhyMontm.plot.line(0, figsize=(15,5), title="Montmorillonite")
relabMontm.plot.line(0, ax=ax1) # ax=ax plots all on the same axis

ax2 = specFePhyNontr.plot.line(0, figsize=(15,5), title="Nontronite")
relabNontr.plot.line(0, ax=ax2)

ax3 = relabMontm.plot.line(0, figsize=(15,5), title="Montmorillonite vs Nontronite")
relabNontr.plot.line(0, ax=ax3)

plt.show()

#lets put this into a function so we can reuse it later:
def removeCont(pSample):
    pSampleLineX=[pSample[0][0],pSample[0][-1]]
    pSampleLineY=[pSample[1][0],pSample[1][-1]]
    pSampleLine=[pSampleLineX,pSampleLineY]
    finterp = interp1d(pSampleLine[0],pSampleLine[1])#create interploation function
    return pSample[1]-finterp(pSample[0])

# Lets try this on a bigger fake dataset:
pivot = lambda sample: [[a[0] for a in sample],[a[1] for a in sample]]

sample = np.asarray([list(x) for x in zip(range(32),[x[0] for x in np.random.random((32,1)).tolist()])])
pSample=pivot(sample)
plt.plot(pSample[0],pSample[1], '-',pSample[0],removeCont(pSample),'-')
plt.legend(['original', 'continuum removed'], loc='best')
plt.show()

#we can now easily find a maximum value above the continuum for points other than first and last:
max(removeCont(pSample)[1:-1])

#furthermore, we can ask numpy for an index of max:
maxIndex = np.argmax(removeCont(pSample)[1:-1]) +1
maxIndex

#Armed with this information we can repeat the previous step for a subset:
plt.plot(pSample[0][:maxIndex],pSample[1][:maxIndex], '-',pSample[0][:maxIndex],
         removeCont([pSample[0][:maxIndex],pSample[1][:maxIndex]]),'-')
plt.legend(['original', 'continuum removed'], loc='best')
plt.show()

# From henceforth we could do this recursively - that is to use the output of a function as an input to itself:
def getMaxima(pSample):
    def getMaximaInner(innerSample):
        contRem=removeCont(innerSample)
        #print(contRem)
        maxIndex=np.argmax(contRem)
        #print(maxIndex)
        maxVal=contRem[maxIndex]
        maxLoc=innerSample[0][maxIndex]
        if len(contRem)>2 and maxVal>contRem[0] and maxVal>contRem[-1]: # check that the maximum is more than edges
            maxLocArray.append(maxLoc)
            #print(maxLoc)
            subsetLeft=[innerSample[0][:maxIndex+1],innerSample[1][:maxIndex+1]]
            #print(subsetLeft[0])
            subsetRight=[innerSample[0][maxIndex:],innerSample[1][maxIndex:]]
            #print(subsetRight[0])
            getMaximaInner(subsetLeft)
            getMaximaInner(subsetRight)
    maxLocArray=[] #initialize array to store a list of points on a convex hull
    getMaximaInner(pSample)
    maxLocArray.sort()
    return [pSample[0][0]]+maxLocArray+[pSample[0][-1]]

#maxList=getMaxima([pSample[0][:5],pSample[1][:5]])
maxList=getMaxima(pSample)
print(maxList)

hull=[maxList,[x[1] for x in sample if x[0] in maxList]]
plt.plot(pSample[0],pSample[1], '-',hull[0],hull[1],'-')
plt.show()

#Now lets try it with a real dataset:
sample = np.asarray(relabMontm)
pSample = pivot(sample)
maxList = getMaxima(pSample)
print(maxList)
hull = [maxList,[x[1] for x in sample if x[0] in maxList]]
plt.plot(pSample[0],pSample[1], '-',hull[0],hull[1],'-')

# You may notice that the formation of a convex hull is distorted 
# by a long row of zeros at the end of the data sample
# Lets remove all zeros:
cleanSample=[value for value in sample if value[1]>0]
pSample=pivot(cleanSample)
maxList=getMaxima(pSample)
#print(maxList)
pHull=[maxList,[x[1] for x in sample if x[0] in maxList]]
plt.plot(pSample[0],pSample[1], '-',pHull[0],pHull[1],'-')
plt.legend(['spectrum', 'convex hull'])
plt.show()

# Next we can subtact the convex hull from our data, in a manner similar to how we subtracted continuum ealier
def removeHull(pSample,pHull):
    finterp = interp1d(pHull[0],pHull[1])#create interploation function
    return pSample[1]-finterp(pSample[0])

hullRemoved = removeHull(pSample,pHull)
plt.plot(pSample[0],pSample[1],'-',pSample[0],hullRemoved, '-')
plt.legend(['spectrum', 'convex hull removed'])
plt.show()

# we can easily find indices for these values:
splitInd=[pSample[0].index(x) for x in pHull[0]]
print(splitInd)

#then we can split the array along the indices using list comprehension:
splitSample=[[pSample[0][splitInd[i]:splitInd[i+1]],hullRemoved[splitInd[i]:splitInd[i+1]]] 
             for i in range(len(splitInd)-1) if splitInd[i+1]-splitInd[i]>2]
for s in splitSample:
    plt.plot(s[0],s[1],'-')
plt.show()

# Finding local minima is then straightforward:
listMinimaX=[x[0][np.argmin(x[1])] for x in np.asarray(splitSample)]
print(listMinimaX)

# we can use list comprehension again to get corresponding Y-values
listMinimaY=[pSample[1][pSample[0].index(x)] for x in listMinimaX]
print(listMinimaY)

#And we can combine the two and plot the minima on a graph:
splitSample=[[pSample[0][splitInd[i]:splitInd[i+1]],pSample[1][splitInd[i]:splitInd[i+1]]] 
             for i in range(len(splitInd)-1) if splitInd[i+1]-splitInd[i]>2]
for s in splitSample:
    plt.plot(s[0],s[1],'-')
plt.plot(listMinimaX,listMinimaY,'x',color='black')
plt.show()

# We've now identified some deep absorption bands, a some shallow that are probably noise.
# We can filter out the shallow ones by appling a threshold:
# First get the band depths with hull removed:
listMinimaYhullRemoved=[hullRemoved[pSample[0].index(x)] for x in listMinimaX]
print(listMinimaYhullRemoved)

# Now apply a threshold:
threshold=0.05
listMinimaSigX=[q[0] for q in list(zip(listMinimaX,listMinimaYhullRemoved)) if q[1]<-threshold]
listMinimaSigYhullRemoved=[q[1] for q in list(zip(listMinimaX,listMinimaYhullRemoved)) if q[1]<-threshold]
listMinimaSigY=[pSample[1][pSample[0].index(x)] for x in listMinimaSigX]

#then we can split the array along the indices using list comprehension:
splitSample=[[pSample[0][splitInd[i]:splitInd[i+1]],hullRemoved[splitInd[i]:splitInd[i+1]]] 
             for i in range(len(splitInd)-1) if splitInd[i+1]-splitInd[i]>2]
plt.figure(figsize=(15,5)) #make larger figure
for s in splitSample:
    plt.plot(s[0],s[1],'-')
for xc in listMinimaSigX:
    plt.axvline(x=xc,color='black')
plt.show()

# Finally, lets see where do these band depths plot on original spectra:
plt.figure(figsize=(15,5))
splitSample=[[pSample[0][splitInd[i]:splitInd[i+1]],pSample[1][splitInd[i]:splitInd[i+1]]] 
             for i in range(len(splitInd)-1) if splitInd[i+1]-splitInd[i]>2]
for s in splitSample:
    plt.plot(s[0],s[1],'-')
plt.plot(listMinimaSigX,listMinimaSigY,'o',color='black')
plt.show()

print("adsorption band center wavelenghts are:")
for item in listMinimaSigX:
    print(item, "micrometers")