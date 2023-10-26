# Calculates velocities from GPS data and writes them to a csv file
# ©2023 The Johns Hopkins University Applied Physics Laboratory LLC

import csv
import numpy as np
import math
import pandas as pd

def haversine(prevlat,currlat,prevlon,currlon,prevt,currt) -> tuple:
    prevla = math.radians(prevlat)
    currla = math.radians(currlat)
    prevlo = math.radians(prevlon)
    currlo = math.radians(currlon)
    
    
    dy = 2*6371000*np.arcsin(math.sqrt(((np.sin((currla - prevla)/2))**2) + np.cos(prevla)*np.cos(currla)*((np.sin(0/2))**2)))
    d = 2*6371000*np.arcsin(math.sqrt(((np.sin((currla - prevla)/2))**2) + np.cos(prevla)*np.cos(currla)*((np.sin((currlo-prevlo)/2))**2)))
    dx = 2*6371000*np.arcsin(math.sqrt(((np.sin(0/2))**2) + np.cos(prevla)*np.cos(prevla)*((np.sin((currlo-prevlo)/2))**2)))
    v = d/(currt - prevt)
    vy = dy/(currt - prevt)
    vx = dx/(currt - prevt)
    return dy,dx,vy,vx,v

df =pd.read_csv(r"C:\Users\yusj1\Documents\Python_Scripts\DeadReckoningTest\test4.csv")
lat = df["Lat"].to_numpy(dtype="float64")
long = df["Long"].to_numpy(dtype="float64")
time = df["time"].to_numpy(dtype="float64")

avg_vy, avg_vx,avg_v = [],[],[]
firstData = False
prevvx,prevvy,prevv = 0,0,0
prevx,prevy,prevt = 0,0,0


for i in range(len(lat)):
    if(firstData):
        if(lat[i] and long[i] != 0):
            data = haversine(prevy,lat[i],prevx,long[i],prevt,time[i])
            prevvx = data[3]
            prevvy = data[2]
            prevv = data[4]
            avg_vy[avg_vy < 0] = prevvy
            avg_vx[avg_vx < 0] = prevvx
            avg_v[avg_v < 0] = prevv
            avg_vy = np.append(avg_vy,-1)
            avg_vx = np.append(avg_vx,-1)
            avg_v = np.append(avg_v,-1)   
        else:
            avg_vy = np.append(avg_vy,-1)
            avg_vx = np.append(avg_vx,-1)
            avg_v = np.append(avg_v,-1)   

    if(not firstData):
        if(lat[i] and long[i] != 0):
            prevx = long[i]
            prevy = lat[i]
            prevt = time[i]
            firstData = True
            avg_vy = np.append(avg_vy,-1)
            avg_vx = np.append(avg_vx,-1)
            avg_v = np.append(avg_v,-1)   
        else:
            avg_vy = np.append(avg_vy,1)
            avg_vx = np.append(avg_vx,1)
            avg_v = np.append(avg_v,-1)   

print(len(avg_v))
df['V'] = avg_v

notZero = False
prevValue,currentValue = 0,0
prevVelocity = []
for x in avg_v:
    if(notZero):
        if(x == currentValue):
           prevVelocity = np.append(prevVelocity, prevValue)
        else:
           prevVelocity = np.append(prevVelocity, currentValue)
           prevValue = currentValue
           currentValue = x
    if(not notZero):
        if(x == 0):
            prevVelocity = np.append(prevVelocity, 0)
        if(x != 0):
            prevVelocity = np.append(prevVelocity,0)
            currentValue = x
            notZero = True
            
            
print(len(prevVelocity))      
    
df['Prev V'] = prevVelocity
df.to_csv('d_test4.csv')    

#Haversine Distance Formula
# D = 3440.1*arccos[(sin(latA) * sin(latB)) + cos(latA)*cos(latB)*cos(longA - longB)]
# lat and long must be in radians.
# distance in nautical miles
