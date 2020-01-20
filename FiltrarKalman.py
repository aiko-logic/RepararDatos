import sys
import csv
import time, datetime
from filterpy.kalman import KalmanFilter

reader = csv.reader(open("DatosPrueba.csv"), delimiter=',')

f = KalmanFilter (dim_x=1, dim_z=1)

f.x = np.array([76.3])   # initial state (location and velocity)

my_filter.F = np.array([[1.,1.],
                [0.,1.]])    # state transition matrix
my_filter.H = np.array([[1.,0.]])    # Measurement function
my_filter.P *= 1000.                 # covariance matrix
my_filter.R = 5                      # state uncertainty
my_filter.Q = Q_discrete_white_noise(2, dt, .1) # process uncertainty

with open("Datos Prueba Filtrados.csv", "w") as fp:
    for row in reader:
        linea = row[0]+", "+row[1]
        print >> fp, linea
        
fp.close()