# Collects IMU and GPS data sent over serial by the Arduino 
# ©2023 The Johns Hopkins University Applied Physics Laboratory LLC
import pandas as pd
import serial
import math
import os
import time,sys
import numpy as np
import csv,datetime
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.integrate import cumtrapz
from scipy import signal

SER_PORT = 'COM3'
SER_BAUD = 115200
accel_coeffs = [np.array([ 0.99745269, -0.6520448 ]), 
                         np.array([1.00104831, 0.13360992]), 
                         np.array([0.96619829, 0.83127514])]
no_calibration = [np.array([1, 0]),
                  np.array([1, 0]),
                  np.array([1, 0])]

stop_time = 300

def accel_fit(x_input,m_x,b):
    return (m_x*x_input)+b

def readSerial(s: serial) -> tuple:
        rawdata = s.readline()
        finalValue = rawdata.decode('utf-8').replace('\r' ,'').replace('\n','')
        data = finalValue.split(',')
        ax = float(data[0])
        ay = float(data[1])
        az = float(data[2])
        wx = float(data[3])
        wy = float(data[4]) 
        wz = float(data[5])
        if(data[6] or data[7] != ""):
            lat = float(data[6])
            long = float(data[7])
        else:
            lat,long = 0,0
        return(ax, ay, az,wx,wy,wz,lat, long)

def haversine(prevlat,currlat,prevlon,currlon,prevt,currt) -> tuple:
    prevla = math.radians(prevlat)
    currla = math.radians(currlat)
    prevlo = math.radians(prevlon)
    currlo = math.radians(currlon)
    
    
    dy = 2*6371000*np.arcsin(math.sqrt(((np.sin((currla - prevla)/2))**2) + np.cos(prevla)*np.cos(currla)*((np.sin(0/2))**2)))
    dx = 2*6371000*np.arcsin(math.sqrt(((np.sin(0/2))**2) + np.cos(prevla)*np.cos(prevla)*((np.sin((currlo-prevlo)/2))**2)))
    vy = dy/(currt - prevt)
    vx = dx/(currt - prevt)
    return dy,dx,vy,vx

def recordData(s: serial):
    esp32.reset_input_buffer()
    esp32.reset_output_buffer()
    x_accel_array,y_accel_array,z_accel_array,wx_array,wy_array,wz_array,lat_array,long_array,t_array = [],[],[],[],[],[],[],[],[]
    t0 = time.time()
    while True:
        data = readSerial(s)
        print(data)
        t_array.append(time.time()-t0)
        x_accel_array.append(accel_fit(data[0],*accel_coeffs[0]))
        y_accel_array.append(accel_fit(data[1],*accel_coeffs[1]))
        z_accel_array.append(accel_fit(data[2],*accel_coeffs[2]))
        wx_array.append(data[3])
        wy_array.append(data[4])
        wz_array.append(data[5])
        lat_array.append(data[6])
        long_array.append(data[7])
          
        if (time.time()-t0 > stop_time):
            break

    x_accel_array = signalFilter(x_accel_array, stop_time)
    y_accel_array = signalFilter(y_accel_array, stop_time)
    z_accel_array = signalFilter(z_accel_array, stop_time)
    
    vx_array = np.append(0.0,cumtrapz(x_accel_array,x=t_array))
    vy_array = np.append(0.0,cumtrapz(y_accel_array,x=t_array))
    vz_array = np.append(0.0,cumtrapz(z_accel_array,x=t_array))
    
    arr = np.transpose(np.asarray([x_accel_array,y_accel_array,z_accel_array,wx_array,wy_array,wz_array,vx_array,vy_array,vz_array,lat_array,long_array,t_array]))
    print(pd.DataFrame(arr))
    pd.DataFrame(arr).to_csv('trial1.csv', index_label = "Index", header  = ['X Accel','Y Accel','Z Accel','X Rotation','Y Rotation','Z Rotation','X Vel','Y Vel','Z Vel','Lat','Long','time'])    
    return

def signalFilter(accel_array, dt_stop):
    Fs_approx = len(accel_array)/dt_stop
    b_filt,a_filt = signal.butter(4,5,'low',fs=Fs_approx)
    accel_array = signal.filtfilt(b_filt,a_filt,accel_array)
    return accel_array
        
if __name__ == '__main__':  
    esp32 = serial.Serial(SER_PORT, baudrate=SER_BAUD) 
    input("Press enter to start collecting data...")
    recordData(esp32)
