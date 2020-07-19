# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 19:36:02 2019

@author: shogh
"""

import pandas as pd
import numpy as np
from collections import defaultdict
import math

td = pd.read_csv("201910-citibike-tripdata.csv")

''' 
Creates a dictionary (id_to_station) that maps station ID's to station names
Creates a dictionary (ll_to_stat) that maps each station to a tuple: (latitude, longitude)
'''
id_to_station = defaultdict(str)
ll_to_stat = defaultdict(lambda: (0,0))
for i in range(td.shape[0]):
    if not (math.isnan(td.loc[i,'start station id']) or math.isnan(td.loc[i,'end station id'])):
        id_to_station[int(float(td.loc[i,'start station id']))] = td.loc[i,'start station name']
        id_to_station[int(float(td.loc[i,'end station id']))] = td.loc[i,'end station name']
        ll_to_stat[td.loc[i,'start station name']] = (td.loc[i,'start station latitude'],td.loc[i,'start station longitude'])
        ll_to_stat[td.loc[i,'end station name']] = (td.loc[i,'end station latitude'],td.loc[i,'end station longitude'])
        

'''
Creates a dictionary (dfps) that contains the number of bike rides starting at each station
'''
freq_per_start = td
for ind in td.columns:
    if ind == 'start station id':
        continue
    freq_per_start = freq_per_start.drop(columns = [ind])

freq_per_start = freq_per_start.dropna()
dfps = defaultdict(int)
for i in range(td.shape[0]):
    dfps[id_to_station[int(float(freq_per_start.iloc[i,0]))]] +=1

dfpsl = sorted(dfps.items(), key=lambda x:x[1],reverse=True) #Sorted list

'''
Creates a dictionary (dfpe) that contains the number of bike rides ending at each station
'''
freq_per_end = td
for ind in td.columns:
    if ind == 'end station id':
        continue
    freq_per_end = freq_per_end.drop(columns = [ind])

freq_per_end = freq_per_end.dropna()
dfpe = defaultdict(int)
for i in range(freq_per_end.size):
    dfpe[id_to_station[int(float(freq_per_end.iloc[i,0]))]] +=1

dfpel = sorted(dfpe.items(), key=lambda x:x[1],reverse=True) #Sorted list

'''
Creates a dictionary (dfpt) that contains the total number of bike rides from each station (starting + ending combined)
'''
dfpt = defaultdict(int)
for key in dfps:
    dfpt[key] += dfps[key]
for key in dfpe:
    dfpt[key] += dfpe[key]

dfptl = sorted(dfpt.items(), key=lambda x:x[1],reverse=True)


'''
Sorts stations by number of male and female riders
'''
'''
genderd = td
for ind in td.columns:
    if ind == 'gender' or ind == 'start station id' or ind == 'end station id':
        continue
    genderd = genderd.drop(columns = [ind])

gdict = defaultdict(lambda: [0,0])
for i in range(genderd.shape[0]):
    if not math.isnan(genderd.iloc[i,0]):
        if genderd.iloc[i,2] == 1:
            gdict[id_to_station[int(float(genderd.iloc[i,0]))]][0] += 1
        if genderd.iloc[i,2] == 2:
            gdict[id_to_station[int(float(genderd.iloc[i,0]))]][1] += 1
    
    if not math.isnan(genderd.iloc[i,1]):
        if genderd.iloc[i,2] == 1:
            gdict[id_to_station[int(float(genderd.iloc[i,1]))]][0] += 1
        if genderd.iloc[i,2] == 2:
            gdict[id_to_station[int(float(genderd.iloc[i,1]))]][1] += 1
            
gendlm = sorted(gdict.items(), key = lambda x:x[1],reverse=True)
gendlf = sorted(gdict.items(), key = lambda x:x[1][1],reverse=True)

#Females are underrpresented-no station where females exceed males
'''

'''
Creates adjacency matrix (dataframe adf)
'''
tdad = td
for ind in tdad.columns:
    if ind == 'start station name' or ind == 'end station name':
        continue
    tdad = tdad.drop(columns = [ind])
    
tdad= tdad.dropna()

admat = np.zeros((len(dfptl),len(dfptl)))
statlist = []
for tup in dfptl:
    statlist.append(tup[0])

for i in range(tdad.shape[0]):
    admat[statlist.index(tdad.iloc[i,0]),statlist.index(tdad.iloc[i,1])] += 1

adf= pd.DataFrame(data = admat, index = statlist, columns= statlist)
adf.to_excel("adjacency.xlsx")

'''
Creates dataframe mapping each station to number of rides in and out of it
'''
inoutmat = np.zeros((len(statlist),3))
for i in range(len(statlist)):
    inoutmat[i,0] = dfps[statlist[i]]
    inoutmat[i,1] =dfpe[statlist[i]]
    if inoutmat[i,0] == 0:
        inoutmat[i,2] = 100000
    else:
        inoutmat[i,2] = inoutmat[i,1]/inoutmat[i,0]
inoutdatf = pd.DataFrame(data = inoutmat, index = statlist, columns = ["Rides Starting From Station","Rides Ending At Station", "Ratio of Rides Ending to Rides Starting"])
inoutdatf.to_excel("stf.xlsx")

'''
Creates matrix containing asymmetry values
Asymmetry value between stations A and B is defined as:
    number of rides from station A to station  B/number of rides from station B to station A
'''
asymm_mat = np.zeros((len(dfptl),len(dfptl)))

for i in range(len(dfptl)):
    for j in range(len(dfptl)):
        if admat[j,i] == 0:
            asymm_mat[i,j] = 100000
        else:
            asymm_mat[i,j] = admat[i,j]/admat[j,i]
asymmdf = pd.DataFrame(data = asymm_mat, index =statlist, columns = statlist)
asymmdf.to_excel("asymrat.xlsx")

'''
Function to find distance between 2 points latitude and longitude.
Uses Haversine formula to find distance.
'''
def dist_pt(lat1, lon1, lat2, lon2): 
    rad_e = 6371 #radius of Earth is 6371 km
    latc = lat2-lat1
    lonc = lon2- lon1
    a = (math.pow(math.sin(latc/2),2)) + math.cos(lat1) * math.cos(lat2)*(math.pow(math.sin(lonc/2),2))
    return  rad_e * 2* math.atan2(math.sqrt(a),math.sqrt(1-a))

'''
Creates DataFrame listing distance between each pair of stations (set up similar to adjacency matrix)
'''
llmat = np.zeros((len(dfptl),len(dfptl)))
for i in range(len(dfptl)):
    p1 = ll_to_stat[statlist[i]]
    for j in range(len(dfptl)):
        p2 = ll_to_stat[statlist[j]]
        llmat[i,j] = dist_pt(p1[0],p1[1],p2[0],p2[1])
lldf = pd.DataFrame(data = llmat, index =statlist, columns = statlist)
lldf.to_excel("distancebetweenpts.xlsx")

'''
Creates DataFrame with latitude/longitude coordinates of each station
'''
coord_mat = np.zeros((len(dfptl),2))
curr = 0
for key in ll_to_stat:
    coord_mat[curr,0] = ll_to_stat[key][0]
    coord_mat[curr,1] = ll_to_stat[key][1]
    curr +=1
coord_df = pd.DataFrame(data = coord_mat, index = list(ll_to_stat.keys()), columns = ["Latitude","Longitude"])
coord_df.to_excel("coordinates.xlsx")
