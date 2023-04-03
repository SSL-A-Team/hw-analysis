import math
import femm
import matplotlib.pyplot as plt
import csv

METER_TO_IN = 39.3701

femm.openfemm()
femm.opendocument("Custom Solenoid Plunger.fem");
femm.mi_saveas("temp.fem")

#
# Coil Creation
#

# Boundary/Air preloaded

#
# Coil sides
#
coil_inner_radius = 0.005 # m
coil_thickness = 0.020 # m
coil_total_length = 0.040 # m
turns = 200
coil_group = 0
for side in range(0,2):
    femm.mi_seteditmode("nodes")
    direction_scale = -1
    if side == 1:
        direction_scale = 1

    # x,y top left and bottom right of the rectangle
    coil_top_left = [direction_scale*(coil_inner_radius + coil_thickness), coil_total_length/2]
    coil_bottom_right = [direction_scale*(coil_inner_radius), -coil_total_length/2]
    femm.mi_drawrectangle(coil_top_left[0], coil_top_left[1], coil_bottom_right[0], coil_bottom_right[1])
    femm.mi_seteditmode("blocks")

    coil_center = [(coil_top_left[0]+coil_bottom_right[0])/2,(coil_top_left[1]+coil_bottom_right[1])/2]

    femm.mi_addblocklabel(coil_center[0], coil_center[1])
    femm.mi_selectlabel(coil_center[0], coil_center[1])
    femm.mi_setblockprop('22 AWG', 1, 0,"Coil", 0, coil_group, direction_scale*turns) 

femm.mi_clearselected()
#
# Plunger
#
plunger_margin = 0.0005 # m distance away from inner coil walls
plunger_length = 0.020 # m
plunger_center_offset = 0.015 # m distance away the leading edge is from the center of coils length 
plunger_group = 1

# x,y top left and bottom right of the rectangle
femm.mi_seteditmode("nodes")
plunger_top_left = [-(coil_inner_radius-plunger_margin), -plunger_center_offset]
plunger_bottom_right = [(coil_inner_radius-plunger_margin), -(plunger_center_offset + plunger_length)]
femm.mi_drawrectangle(plunger_top_left[0], plunger_top_left[1], plunger_bottom_right[0], plunger_bottom_right[1])
femm.mi_seteditmode("blocks")
plunger_center = [(plunger_top_left[0]+plunger_bottom_right[0])/2,(plunger_top_left[1]+plunger_bottom_right[1])/2]

femm.mi_addblocklabel(plunger_center[0],plunger_center[1])
femm.mi_selectlabel(plunger_center[0],plunger_center[1])
femm.mi_setblockprop('1020 Steel',1,0,"","",plunger_group)
femm.mi_clearselected()

# Wire length 
awg_22_diameter = 0.00064262
# TODO calculate resistance

#
# Simulation
#
femm.mi_seteditmode("group")

plunger_displacement_samples=[];
force_samples=[];
time_samples=[];
current_samples=[]
prev_velocity = 0 # m/s
velocity = 0 # m/s

# Iterate over length of coil

# Variables for modeling current decay in coil
initial_voltage = 170  # volts
coil_resistance = 1.9 # ohms
kicker_board_capacitance = 0.002 # Farads
tau = coil_resistance * kicker_board_capacitance

golf_ball_restitution = 0.7

d_total = 0 # m
a_inst = 0 # m/s^2
m = 0.061 # kg
delta_t = 0.01 # s
travel_dist = 0.015 # m
for t_whole in range(0,60):
    input()
    # i=− V_0/R *e^(-t/tau)
    current_inst = (initial_voltage / coil_resistance) * math.exp(-(t_whole*delta_t) / tau)
    current_samples.append(current_inst)
    femm.mi_setcurrent("Coil", current_inst)

    femm.mi_analyze()
    femm.mi_loadsolution()
    femm.mo_groupselectblock(1)
    f_inst = femm.mo_blockintegral(19) # Newtons
    input()
    # f = ma
    a_inst = f_inst / m 

    velocity = prev_velocity + a_inst*delta_t
    delta_d = (prev_velocity + velocity)/2 * delta_t
    d_total = d_total + delta_d
    time_samples.append(t_whole*delta_t)
    plunger_displacement_samples.append(d_total)
    force_samples.append(f_inst)
    if (d_total >= travel_dist):
        # Gone to end of stop
        break
    # Next round initial velocity is current final velocity
    prev_velocity = velocity
    femm.mi_selectgroup(1)
    print(delta_d)
    femm.mi_movetranslate(0, delta_d)


femm.closefemm()

# plunger weight: 55g
# boot weight: 6g
# total kicker weight: 61g

# 6.35mm of contact travel w/ ball

# E = m * v^2
# m_ball * v_ball^2 = m_plunger * v_plunger^2
# v_ball = sqrt((m_plunger * v_plunger^2) / m_ball)
v_ball = golf_ball_restitution*math.sqrt((m * velocity**2) / 0.0459)
print(f"Expected ball velocity: {v_ball} m/s")
#
#
##with open('solenoid_sim_output.csv', 'w', newline='') as csvfile:
##    csv_writer = csv.writer(csvfile, delimiter=',')
##    csv_writer.writerow(["Time", "Current", "Force", "Displacement"])
##    for sample_index in range(len(time_samples)):
##        csv_writer.writerow([time_samples[sample_index], current_samples[sample_index], force_samples[sample_index], plunger_displacement_samples[sample_index]])
#
#
print("Avg. Force:" + repr(sum(force_samples)/len(force_samples)))
plt.subplot(1,3,1)
plt.plot(time_samples,plunger_displacement_samples)
plt.xlabel('Time, s')
plt.ylabel('Offset, m')
plt.subplot(1,3,2)
plt.plot(time_samples,force_samples)
plt.xlabel('Time, s')
plt.ylabel('Force, N')
plt.subplot(1,3,3)
plt.plot(time_samples,current_samples)
plt.xlabel('Time, s')
plt.ylabel('Current, A')
plt.show()
