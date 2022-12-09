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


T_b = np.matrix([
    [sin(theta[0]), sin(theta[1]), sin(theta[2]), sin(theta[3])],
    [cos(theta[0]), cos(theta[1]), cos(theta[2]), cos(theta[3])],
    [1.0 / l,       1.0 / l,       1.0 / l,       1.0 / l],
])

body_vel_rec = T_b * vel_wheel
print(body_vel_rec / 4.0)
# # print(body_vel_rec)
# body_vel_rec[0] = body_vel_rec[0] * (2.0 / 3.0)
# body_vel_rec[1] = body_vel_rec[1] * 0.40
# # body_vel_rec = np.array([body_vel_rec[0][0] * (2.0 / 3.0), body_vel_rec[1][0] * 0.40, body_vel_rec[2]])
# print(body_vel_rec)