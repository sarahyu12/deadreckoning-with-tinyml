# Calibration
#
# This script was modified from
#   https://makersportal.com/blog/calibration-of-an-inertial-measurement-unit-imu-with-raspberry-pi-part-ii
#   https://github.com/makerportal/mpu92-calibration/blob/main/accel/accel_calibration.py
#  Copyright (c) 2021 Maker Portal LLC
#  Author: Joshua Hrisko
#  GPL-3.0 license (see a copy of the license in the same directory as this file)
#
# 2023

import pandas as pd
import serial
import math
import os
import time,sys
sys.path.append('../')
import numpy as np
import csv,datetime
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.integrate import cumtrapz
from scipy import signal

SER_PORT = 'COM3'
SER_BAUD = 115200

# class SerialPort:
    # def __init__(self, port, baud=9600):
    #     self.port = port
    #     self.baud = baud
    #     self.ser = serial.Serial(self.port, self.baud, timeout=None, xonxoff=False, rtscts=False, dsrdtr=False)
    #     self.ser.flushInput()
    #     self.ser.flushOutput()
        
    # def Read(self) -> str:
    #     self.ser.flushInput()
    #     bytesToRead = self.ser.readline()
    #     decodedMsg = bytesToRead.decode('utf-8')
    #     decodedMsg = decodedMsg.rstrip()
    #     return decodedMsg

    # def Close(self) -> None:
    #     self.ser.close()
        
def RecordData(s: serial) -> tuple:
        rawdata = s.readline()
        finalValue = rawdata.decode('utf-8').replace('\r','').replace('\n','')
        data = finalValue.split(',')
        ax = float(data[0])
        ay = float(data[1])
        az = float(data[2])
        return(ax, ay, az)

def accel_cal(s: serial):
    print("-"*50)
    print("Accelerometer Calibration")
    mpu_offsets = [[],[],[]] # offset array to be printed
    axis_vec = ['z','y','x'] # axis labels
    cal_directions = ["upward","downward","perpendicular to gravity"] # direction for IMU cal
    cal_indices = [2,1,0] # axis indices
    for qq,ax_qq in enumerate(axis_vec):
        ax_offsets = [[],[],[]]
        print("-"*50)
        for direc_ii,direc in enumerate(cal_directions):
            input("-"*8+" Press Enter and Keep IMU Steady to Calibrate the Accelerometer with the -"+\
              ax_qq+"-axis pointed "+direc)
            [RecordData(s) for ii in range(0,cal_size)] # clear buffer between readings
            mpu_array = []
            while len(mpu_array)<cal_size:
                try:
                    ax,ay,az = RecordData(s)
                    print([ax, ay, az])
                    mpu_array.append([ax,ay,az]) # append to array
                except:
                    continue
            ax_offsets[direc_ii] = np.array(mpu_array)[:,cal_indices[qq]] # offsets for direction

        # Use three calibrations (+1g, -1g, 0g) for linear fit
        popts,_ = curve_fit(accel_fit,np.append(np.append(ax_offsets[0],
                                 ax_offsets[1]),ax_offsets[2]),
                   np.append(np.append(9.8*np.ones(np.shape(ax_offsets[0])),
                    -9.8*np.ones(np.shape(ax_offsets[1]))),
                        0.0*np.ones(np.shape(ax_offsets[2]))),
                            maxfev=10000)
        mpu_offsets[cal_indices[qq]] = popts # place slope and intercept in offset array
    print('Accelerometer Calibrations Complete')
    return mpu_offsets
    
def imu_integrator(s: serial):
    #############################
    # Main Loop to Integrate IMU
    #############################
    #
    data_indx = 1 # index of variable to integrate
    dt_stop = 5 # seconds to record and integrate

    plt.style.use('ggplot')
    plt.ion()
    fig,axs = plt.subplots(3,1,figsize=(12,9))
    break_bool = False
    while True:
        #
        ##################################
        # Reading and Printing IMU values 
        ##################################
        #
        accel_array,t_array = [],[]
        print("Starting Data Acquisition")
        [axs[ii].clear() for ii in range(0,3)]
        t0 = time.time()
        loop_bool = False
        while True:
            try:
                ax,ay,az=(RecordData(s)) 
                t_array.append(time.time()-t0)
                data_array = [ax,ay,az]
                accel_array.append(accel_fit(data_array[data_indx],
                                             *accel_coeffs[data_indx]))
                if not loop_bool:
                    loop_bool = True
                    print("Start Moving IMU...")
            except:
                continue
            if time.time()-t0>dt_stop:
                print("Data Acquisition Stopped")
                break
            
        if break_bool:
            break
        #
        ##################################
        # Signal Filtering
        ##################################
        #
        Fs_approx = len(accel_array)/dt_stop
        b_filt,a_filt = signal.butter(4,5,'low',fs=Fs_approx)
        accel_array = signal.filtfilt(b_filt,a_filt,accel_array)
        # accel_array = np.multiply(accel_array,9.80665)
        #
        ##################################
        # Print Sample Rate and Accel
        # Integration Value
        ##################################
        #
        print("Sample Rate: {0:2.0f}Hz".format(len(accel_array)/dt_stop))
        veloc_array = np.append(0.0,cumtrapz(accel_array,x=t_array))
        dist_approx = np.trapz(veloc_array,x=t_array)
        dist_array = np.append(0.0,cumtrapz(veloc_array,x=t_array))
        print("Displace in y-dir: {0:2.2f}m".format(dist_approx))
        axs[0].plot(t_array,accel_array,label="$"+mpu_labels[data_indx]+"$",
                    color=plt.cm.Set1(0),linewidth=2.5)
        axs[1].plot(t_array,veloc_array,
                    label="$v_"+mpu_labels[data_indx].split("_")[1]+"$",
                    color=plt.cm.Set1(1),linewidth=2.5)
        axs[2].plot(t_array,dist_array,
                    label="$d_"+mpu_labels[data_indx].split("_")[1]+"$",
                    color=plt.cm.Set1(2),linewidth=2.5)
        [axs[ii].legend() for ii in range(0,len(axs))]
        axs[0].set_ylabel('Acceleration [m$\cdot$s$^{-2}$]',fontsize=16)
        axs[1].set_ylabel('Velocity [m$\cdot$s$^{-1}$]',fontsize=16)
        axs[2].set_ylabel('Displacement [m]',fontsize=16)
        axs[2].set_xlabel('Time [s]',fontsize=18)
        axs[0].set_title("MPU9250 Accelerometer Integration",fontsize=18)
        plt.pause(0.01)
        plt.savefig("accel_veloc_displace_integration.png",dpi=300,
                    bbox_inches='tight',facecolor="#FCFCFC")
    
def accel_fit(x_input,m_x,b):
    return (m_x*x_input)+b # fit equation for accel calibration

if __name__ == '__main__':  
    esp32 = serial.Serial(SER_PORT, baudrate=SER_BAUD) 
    mpu_labels = ['a_x','a_y','a_z'] # gyro labels for plots
    cal_size = 1000 # number of points to use for calibration 
    old_vals_bool = True # True uses values from another calibration
    if not old_vals_bool:
        accel_coeffs = accel_cal(esp32) # grab accel coefficients
    else:
        
         accel_coeffs = [np.array([ 0.99745269, -0.6520448 ]), 
                         np.array([1.00104831, 0.13360992]), 
                         np.array([0.96619829, 0.83127514])]
    print(accel_coeffs)
    input("Press enter to continue...")
    data = np.array([RecordData(esp32) for ii in range(0,cal_size)])
    imu_integrator(esp32)
    
    
    
        
        
