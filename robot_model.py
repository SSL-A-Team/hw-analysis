import numpy as np
from math import *

l = 0.080
theta = np.array([radians(30.0), radians(150.0), radians(225.0), radians(315.0)])
# theta = np.array([radians(45.0), radians(135.0), radians(225.0), radians(315.0)])
beta = theta

vel_cmd = np.matrix([[0.0], [4.0], [0.0]])

T_f = np.matrix([
    [sin(theta[0]), cos(theta[0]), l],
    [sin(theta[1]), cos(theta[1]), l],
    [sin(theta[2]), cos(theta[2]), l],
    [sin(theta[3]), cos(theta[3]), l],
])

vel_wheel = T_f * vel_cmd

print(vel_cmd)
print(T_f)
print(vel_wheel)

T_b = np.linalg.pinv(T_f)

rec_vel_body = T_b * vel_wheel

print(rec_vel_body)
