# Performs dead reckoning of IMU data using double-integration of acceleration
# ©2023 The Johns Hopkins University Applied Physics Laboratory LLC

import csv
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.integrate import cumtrapz

df = pd.read_csv(r"C:\Users\yusj1\Documents\Python_Scripts\DeadReckoningTest\trail1_data.csv")
df2 = pd.read_csv(r"C:\Users\yusj1\Documents\Python_Scripts\DeadReckoningTest\predictedvalue00.csv")

predicted_v = df2['0'].to_numpy()
V = df["Y Vel"].to_numpy(dtype="float64")
t_array = df["time"].to_numpy(dtype="float64")
rotation = df['Z Rotation'].to_numpy(dtype="float64")
gpsv = df["V"].to_numpy(dtype="float64")

print(len(t_array))
print(len(predicted_v))
rotation = rotation + 0.02
for i in range(0, len(rotation)):
    if rotation[i] <= 0.01:
        if rotation[i] >= -0.01:
            rotation[i] = 0

rot,prevt = 0,0

trueRotation = np.append(0.0, cumtrapz(rotation, x=t_array))
xVel,yVel = [],[]
pxVel,pyVel=[],[]
gpsx,gpsy=[],[]
for i,p in enumerate(rotation):
    vy = np.cos(trueRotation[i])*V[i]
    vx = np.sin(trueRotation[i])*V[i]
    xVel.append(vx)
    yVel.append(vy)
for i,p in enumerate(rotation):
    vy = np.cos(trueRotation[i])*predicted_v[i]
    vx = np.sin(trueRotation[i])*predicted_v[i]
    pxVel.append(vx)
    pyVel.append(vy)
for i,p in enumerate(rotation):
    vy = np.cos(trueRotation[i])*gpsv[i]
    vx = np.sin(trueRotation[i])*gpsv[i]
    gpsx.append(vx)
    gpsy.append(vy)

x=np.append(0.0, cumtrapz(xVel, x=t_array))
y=np.append(0.0, cumtrapz(yVel, x=t_array))
plt.plot(x, y, label="double integration")
plt.xlabel ('Meters')
plt.ylabel ('Meters')
px=np.append(0.0, cumtrapz(pxVel, x=t_array))
py=np.append(0.0, cumtrapz(pyVel, x=t_array))
plt.plot(px, py, label="machine learning")
gx=np.append(0.0, cumtrapz(gpsx, x=t_array))
gy=np.append(0.0, cumtrapz(gpsy, x=t_array))
plt.plot(gx, gy, label="gps")
plt.legend()
plt.show()
