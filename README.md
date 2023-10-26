# DeadReckoning

Dead reckoning is a method of navigation where the current position is calculated by using a previously known position, and any measurements of speed, acceleration, heading, and time. Dead reckoning does not incoporate external references, as one might in triangulation or trilateration.  
  
A subset of dead reckoning called inertial navigation uses only inertial measurement sensors (IMU - inertial measurement unit) - accelerometers and gyroscopes. Inertial navigation is notoriously inaccurate; the naive approach involves doubly integrating acceleration to determine position, so errors within the sensor hardware are compounded in the output. This repository includes a script, `deadreckoning.py`, which demonstrates the double integration approach.  
Performance can be improved somewhat by calibrating the IMU; `calibration.py` demonstrates this.  
  
Various techniques exist to improve inertial navigation. One budding area of interest here, like in so many fields, is machine learning. The iPython notebook `tensorflow.ipynb` demonstrates how one can train a neural network to predict velocity values given acceleration measurements; this approach outperforms the double integration approach.  
Acceleration and ground truth data are captured using the Arduino code in this repository, with an MPU6050 IMU and a GPS.  
  
This repository also includes samples of captured data, and trained models. 
  
©2023 The Johns Hopkins University Applied Physics Laboratory LLC  
  
_calibration.py in the Python folder is licensed under GPL-3.0 as it was modified from a script by Joshua Hrisko, Copyright (c) 2021 Maker Portal LLC. (a copy of the license is included in the Python directory)_
