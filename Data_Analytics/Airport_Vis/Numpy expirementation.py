# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 20:17:49 2019

@author: Ghose
"""

import numpy as np
import pandas as pa
import matplotlib as mpl



#reads in CSV and prints shape
dat = pa.read_csv(r'C:\Users\Ghose\Documents\Learning Python\Working with Data\data for airstuff.csv', sep =" , ", engine = "python")
print(dat.shape)


#Separates columns
bigcol = dat.columns[0]
collist = bigcol.split(",")[2:4]


#Separates rows
rowlist = list(dat.index)
rollist = list()
for ro in rowlist:
     rollist.append(dat.iloc[ro,0].split(","))

#Converts rollist into array, deletes unnecessary columns, and gets rid of extra quotation mark
rollist = np.array(rollist)
rollist = np.delete(rollist, [0,1,3,5], axis=1)
for i in range(2):
    for j in range(len(rollist)):
        rollist[j,i] = rollist[j,i][1:]

#Adds rollist to the dataframe
cur = 0;
for col in collist:
    dat[col] = pa.Series(rollist[:,cur])
    cur += 1

del dat[bigcol]
#print(dat.iloc[:5])
#end of data processing 


#print(dat.ORIGIN_CITY_NAME.value_counts()[:10].plot(kind="bar"))
#print(dat.ORIGIN_CITY_NAME.value_counts()[:100].plot.box())



#filter = (dat[collist[0]] == dat.loc[0,collist[0]]) & (dat[collist[1]] == dat.loc[0,collist[1]])
#print(dat[filter])

#Creates adjacency matrix
citdat = dat.ORIGIN_CITY_NAME.value_counts()
citlist = list(citdat.index)
numcit = len(citdat)
admat = np.zeros([numcit,numcit])

for i in range(numcit):
    for j in range(numcit):
        filter = (dat[collist[0]] == citlist[i]) & (dat[collist[1]] == citlist[j])
        admat[i,j] = len(dat[filter])
    print(i)  
    
#
#for i in range(346):
#    if admat[numcit-1,:][i] >0:
#        print(true)

dadmat = pa.DataFrame(admat, index = citlist, columns = citlist)
dadmat.to_csv(r'C:\Users\Ghose\Documents\Learning Python\Working with Data\adjacency_table.csv', header = True, index = True)
#print(dadmat.iloc[0,1:10].plot(kind= "bar"))



