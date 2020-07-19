# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 19:19:45 2019

@author: shogh
"""

import pandas as pd
import numpy as np
from collections import defaultdict
import math
import folium as fo
#from folium.plugins import MarkerCluster

asymmdf = pd.read_excel("asymrat.xlsx")
asymm_mat = asymmdf.values
asymm_mat = np.delete(asymm_mat,0,1)


lldf = pd.read_excel("distancebetweenpts.xlsx")
llmat = lldf.values
llmat = np.delete(llmat,0,1)

statlist = list(asymmdf.columns)[1:]

coord_df = pd.read_excel("coordinates.xlsx")

'''
Creates a dictionary (ll_to_stat) that maps each station to a tuple: (latitude, longitude)
'''
ll_to_stat = defaultdict(lambda: (0,0))
for i in range(coord_df.shape[0]):
    ll_to_stat[coord_df.iloc[i,0]] = (coord_df.iloc[i,1],coord_df.iloc[i,2])
    
#21 stations have less than a 100 rides through them so they are easy eliminations-no need to include them in the model
numdel = 21
remove_list = list(asymmdf.columns)[len(asymmdf.columns)-numdel:]

#Start of MODEL
'''
rat_asymm #This is the minimum asymmetry ratio. 
threshold_asymm  #This is the threshold asymmetry value
num_remove #This is the number of stations to be removed.
threshold_dist #This is the threshold distance (how close stations need to be before one can be removed)
'''
def stations_to_remove(rat_asymm, threshold_asymm, threshold_dist,num_remove):
    remlist = []
    for i in range(asymm_mat.shape[0]-numdel):
        count = 0
        for j in range(asymm_mat.shape[1]-numdel):
            if  asymm_mat[i,j] >= threshold_asymm :
                count += 1
        if count/len(statlist) >= rat_asymm:
            remlist.append((statlist[i],count/len(statlist)))
            
    remlistdist = []
    added =[]
    for i in range(len(remlist)):
        ind = statlist.index(remlist[i][0])
        add = False
        for j in range(llmat.shape[1]-numdel):
            if ind  == j: #Making sure that distance to itself (which is always 0) doesn't count
                continue
            if j in added: #Making sure that any staton that is already designated for removal is not still checked for distance
                continue
            if llmat[ind,j] <= threshold_dist:
                add = True
                break
        
        if add:
            remlistdist.append(remlist[i])
            added.append(ind)
    
    remlistdist = sorted(remlistdist, key = lambda x:x[1], reverse = True)
    if len(remlistdist) > num_remove:
        remlistdist = remlistdist[:num_remove]
    
    retlist = []
    for tup in remlistdist:
        retlist.append(tup[0])
        
    return retlist

'''
Map Creation
'''
folium_map = fo.Map(location=[40.738, -73.98],
                        zoom_start=13,
                        tiles="OpenStreetMap")

#marker_cluster = MarkerCluster().add_to(folium_map)
for key in ll_to_stat:
    if key in remove_list:
        fo.Marker(
            location = [ll_to_stat[key][0],ll_to_stat[key][1]],
            popup = key, icon=fo.Icon(color='black')
        ).add_to(folium_map)
    else:
        #pu_str = key + "          " + "Rides Starting From Station: " + str(int(inoutdatf.loc[key,"Rides Starting From Station"]))+ "          " + "Rides Ending At Station: " + str(int(inoutdatf.loc[key,"Rides Ending At Station"]))
        fo.Marker(
            location = [ll_to_stat[key][0],ll_to_stat[key][1]],
            popup = key, icon=fo.Icon(color='blue')
        ).add_to(folium_map)

folium_map.save("map.html")

uin = input("Please enter 's' to start. Please enter 'q' to quit. ")
while uin != "q":
    athr = float(input("Please enter the threshold asymmetry value: "))
    arat = float(input("Please enter the minimum asymmetry ratio: "))
    thrd = float(input("Please enter the threshold distance: "))
    numr  = int(input("Please enter the number of stations to remove: "))
    plist = stations_to_remove(arat,athr,thrd,numr)
    print(plist)
    
    folium_map = fo.Map(location=[40.738, -73.98],
                        zoom_start=13,
                        tiles="OpenStreetMap")

   
    for key in ll_to_stat:
        if key in remove_list:
            fo.Marker(
                location = [ll_to_stat[key][0],ll_to_stat[key][1]],
                popup = key, icon=fo.Icon(color='black')
            ).add_to(folium_map)  
            
        elif key in plist:
            fo.Marker(
                location = [ll_to_stat[key][0],ll_to_stat[key][1]],
                popup = key,icon=fo.Icon(color='red')
            ).add_to(folium_map)
        
        else:
            fo.Marker(
                    location = [ll_to_stat[key][0],ll_to_stat[key][1]],
                    popup = key, icon=fo.Icon(color='blue')
                ).add_to(folium_map)
    
    folium_map.save("map.html")
    
    uin = input("Please enter 'c' to continue. Please enter 'q' to quit.")


