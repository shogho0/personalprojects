# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 09:25:29 2019

@author: Ghose
"""


import numpy as np
import pandas as pa
import matplotlib as mpl

dadfra = pa.read_csv(r'C:\Users\Ghose\Documents\Learning Python\Working with Data\adjacency_table.csv', engine = "python", index_col = 0)
citylist = list(dadfra.index)
nc = len(citylist)
#import tkinter as tk
#from tkinter import simpledialog
#
#application_window = tk.Tk()
#
#citl = simpledialog.askstring("Input", "What city are you leaving from?",
#                                parent=application_window)
#cita = simpledialog.askstring("Input", "What city are you coming to?",
#                                parent=application_window)
#numfla = dadfra.loc[citl, cita]
#numfal = dadfra.loc[cita,citl]
#if(numfla != numfal):
#    print("There are {} flights from {} to {}. This relationship is asymmetric, as there are {} flights back from {} to {}.".format(numfla, citl, cita, numfal, cita, citl))
#else:
#    print("There are {} flights from {} to {}. This relationship is symmetric.".format(numfla, citl, cita))

#function to normalize rows
def normalize_rows(x: np.ndarray):
    """
    function that normalizes each row of the matrix x to have unit length.

    Args:
     ``x``: A numpy matrix of shape (n, m)

    Returns:
     ``x``: The normalized (by row) numpy matrix.
    """
    return x/np.linalg.norm(x, ord=2, axis=1, keepdims=True)

stm = dadfra.values
temstm = stm.transpose()
temstm = normalize_rows(temstm)
stm = temstm.transpose()

#making better adjacency matrix
google = 0.15
stochastic = np.full((nc, nc), 1/nc)
adjmat = ((1-google)*stm) + (google*stochastic)

#power method function
def eigenvalue(A, v):
    Av = A.dot(v)
    return v.dot(Av)

def power_iteration(A):
    n, d = A.shape

    v = np.ones(d) / np.sqrt(d)
    ev = eigenvalue(A, v)

    while True:
        Av = A.dot(v)
        v_new = Av / np.linalg.norm(Av)

        ev_new = eigenvalue(A, v_new)
        if np.abs(ev - ev_new) < 0.01:
            break

        v = v_new
        ev = ev_new

    return ev_new, v_new  


pev = power_iteration(adjmat)[1]
temp = np.copy(pev)
sortpev = -np.sort(-temp)
airord = np.zeros(nc)
for i in range(nc):
    indinsortpev = np.where(sortpev == pev[i])[0][0]
    airord[i] = indinsortpev +1

airrank = np.zeros(nc, dtype = object)
for i in range(nc):
    airrank[i] = citylist[int(airord[i])-1]


import geopandas as gpa
import shapely as sp



    
import geopy as gp
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="specify_your_app_name_here")
def geocode_me(loc):
    try:
        return geolocator.geocode(loc)
    except gp.exc.GeocoderTimedOut:
        return geocode_me(loc)
citpt = list()
citx = np.zeros(nc)
city = np.zeros(nc)
for i in range(nc):
    cc = dadfra.index[i]
    location = geocode_me(cc)
    if(type(location) is not gp.location.Location):
       indslash = cc.find("/")
       location = geocode_me(cc[:indslash])
    x =  location.longitude
    y = location.latitude
    citx[i] = x
    city[i] = y
    citpt.append(sp.geometry.Point(x,y))

citfra = pa.DataFrame(citylist)
citfra["Rank"] = airord
citfra["x"] = citx
citfra["y"] = city
tempcol =citfra.columns.values
tempcol[0]= "City"
citfra.columns = tempcol

ptsgdf = gpa.GeoDataFrame(citfra, crs = {"init": "epsg:4269"},geometry = citpt)




usmap = gpa.read_file(r"C:\Users\Ghose\Documents\Learning Python\Working with Data\tl_2018_us_state.shp")
for i in range(6):
    del usmap[usmap.columns[0]]
for i in range(5):
    del usmap[usmap.columns[1]]


xarr = list()
yarr = list()
for i in range(len(usmap)):
    if(type(usmap["geometry"][i]) is sp.geometry.multipolygon.MultiPolygon):
        for j in range(len(usmap["geometry"][i])):
            xa, ya = usmap["geometry"][i][j].exterior.coords.xy
            xarr.append(np.asarray(xa).tolist())
            yarr.append(np.asarray(ya).tolist())
    else:
        xa, ya = usmap["geometry"][i].exterior.coords.xy
        xarr.append(np.asarray(xa).tolist())
        yarr.append(np.asarray(ya).tolist())

    
#tempcolg = usmap.columns.values
#tempcolg[1]= "ys"
#tempcolg[2] = "xs"
#usmap.columns = tempcolg


#usmap.drop(35, inplace = True)
#usmap.drop(36, inplace = True)
#usmap.drop(34, inplace = True)
#usmap.drop(41, inplace = True)
#usmap.drop(49, inplace = True)
#usmap.drop(31, inplace = True)
#usmap.drop(40, inplace = True)

from bokeh.plotting import figure, save, curdoc
from bokeh.io import show, output_file
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.models.widgets import TextInput
from bokeh.layouts import row, column
liness = None

def plotting():
    forcs = ptsgdf.drop('geometry', axis=1).copy()
    ptscs = ColumnDataSource(forcs)
    
#    uscs = usmap.drop('geometry', axis=1).copy()
#    usmcs = ColumnDataSource(uscs)
    

    plotp = figure(title= "Airport Rankings", plot_width = 1200, plot_height = 1000)
    
    text_input1 = TextInput(value="", title="Enter Departing City")
    text_input2 = TextInput(value="", title="Enter Destination City")
    text_input3 = TextInput(value="", title="Number of Flights from Departing City to Destination")
    
    
    def update1(attr, old, new):
        global liness
        if liness is not None:
            liness.visible = False
        
        xlist = list()
        ylist = list()
        loccom = text_input1.value
        if loccom:
            for i in range(nc):
                ind = list(dadfra.index).index(loccom)
                if dadfra.loc[loccom,:][i] > 0:
                    xlist.append([ptsgdf.loc[i,"x"],ptsgdf.loc[ind,"x"]])
                    ylist.append([ptsgdf.loc[i,"y"],ptsgdf.loc[ind,"y"]])
        
#        hover2 = HoverTool(names = ["airl"])
#        hover2.tooltips = [("Number of Flights")]
#        plotp.add_tools(hover1)
        liness = plotp.multi_line(xlist, ylist, line_width = 1, line_color = "green")  
        liness.visible = True   
        
       
        if loccom: 
            if text_input2.value:
                text_input3.value = str(int(dadfra.loc[text_input1.value,text_input2.value]))
        #inst = inst +1
        
    text_input1.on_change("value", update1)
    
    
    def update2(attr, old, new):
        if text_input1.value: 
            if text_input2.value:
                text_input3.value = str(int(dadfra.loc[text_input1.value,text_input2.value]))
        
       
    text_input2.on_change("value", update2)
  

    hover1 = HoverTool(names = ["airp"])
    plotp.patches(xarr, yarr, 
         color= "cyan",
         alpha=1.0, line_color="black", line_width=2)
    plotp.circle('x', 'y', source=ptscs, name = "airp", color='red', size=5)
    
    
    hover1.tooltips = [("Airport Name", "@City"),("Airport Rank", "@Rank")]
    plotp.add_tools(hover1)
    curdoc().add_root(row(plotp, column(text_input1,text_input2, text_input3)))

plotting()


#outfp = r"C:\Users\Ghose\Documents\Learning Python\Working with Data\airmap.html"
#save(plotp, outfp)
#bokeh serve --show