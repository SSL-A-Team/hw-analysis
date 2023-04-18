import math
import femm
import matplotlib.pyplot as plt
import csv

METER_TO_IN = 39.3701

femm.openfemm()
femm.opendocument("Custom Solenoid Plunger.fem");
femm.mi_saveas("temp.fem")

# https://powerwerx.com/magnet-wire?gclid=CjwKCAjw3POhBhBQEiwAqTCuBspa54KSxFLKjKy1bmjxpT-bpOp5qmJF7khzsoOMwnbXEvoaQ9Z_BxoC4lMQAvD_BwE
# Gauge, Finished Wire Diameter (mm), Max Resistance ohm/km
wire_info = [[10, 2.65,  3.342],
            [12, 2.10,  5.316],
            [14, 1.68,  8.438],
            [16, 1.33,  13.45],
            [18, 1.06,  21.37],
            [20, 0.851, 33.86],
            [22, 0.678, 54.44],
            [24, 0.541, 85.92],
            [26, 0.432, 138.0],
            [28, 0.343, 217.8]]


# Boundary/Air preloaded

# Parameters are wire gauge, coil thickness, and coil length
coil_thickness_range = [0.00635, 0.015875] # m
wire_info_index = 5
coil_total_length = 0.055626 # m (length of original)


coil_inner_width = 0.030872 # m
plunger_height = 0.00625 # m (out of page)
plunger_margin = 0.0005 # m distance away from inner coil walls
coil_height = plunger_height + plunger_margin

coil_thickness_temp = coil_thickness_range[0]
wire_selection_awg = str(wire_info[wire_info_index][0]) + " AWG"
wire_diameter = wire_info[wire_info_index][1]/1000 # m
wire_resistance_per_m = wire_info[wire_info_index][2]/1000 # ohm/m

print(wire_selection_awg)
# Turn calculation
# Assume just stack the wires right next to each other
turn_per_layer = round(coil_total_length/wire_diameter)
# Assume wire stacks directly on top
number_of_layers = round(coil_thickness_temp/wire_diameter)

turns = turn_per_layer*number_of_layers
print("Turn per layer: " + str(turn_per_layer))
print("Layers: " + str(number_of_layers))
print("Turns: " + str(turns))

# Wire length calulation

# Perimeter of single slice assuming no corners
# (Perpendicular to the view in femm file)
#              inner_width
#                   |
#                   V
#         ____|___________|_____
#        |        coil         | 
#       _| _ _|___________|_ _ |_
#        |    |           |    |
# -->    |    |   Plunger |    |  <-- height
#        |    |           |    |
#       _| _ _|___________|_ _ |_
#        |                     |
#        |____|___________|____|
#              
#                   ^
#                   |

simple_inner_most_perimeter = 2*coil_height + 2*coil_inner_width
simple_perimeter_total = simple_inner_most_perimeter * number_of_layers
print("Simple Perimeter Total:" + str(simple_perimeter_total))
# Each corner adds 2 lengths equal to the wire diameter to the perimeter scaling per layer 
# So 4 corners * 2 lengths * wire_diameter * number_of_layers
#     |
#     V    
#    __________|________
#   |             wire 2 
#   |     _____|________
#   |    |        wire 1
# __|  __|   __|________ 
#   |    |     |
#   |    |     |
#   |    |     |

corner_perimeter_total = 4 * 2 * wire_diameter * number_of_layers
print(corner_perimeter_total)
slice_perimeter_total = simple_perimeter_total + corner_perimeter_total

wire_length = slice_perimeter_total*turn_per_layer

print("Wire Length: " + str(wire_length))
coil_resistance = wire_length*wire_resistance_per_m
print("Coil Resistance: " + str(coil_resistance))

# Coil generation
coil_group = 0
for side in range(0,2):
    femm.mi_seteditmode("nodes")
    direction_scale = -1
    if side == 1:
        direction_scale = 1

    # x,y top left and bottom right of the rectangle
    coil_top_left = [direction_scale*(coil_inner_width + coil_thickness_temp), coil_total_length/2]
    coil_bottom_right = [direction_scale*(coil_inner_width), -coil_total_length/2]
    femm.mi_drawrectangle(coil_top_left[0], coil_top_left[1], coil_bottom_right[0], coil_bottom_right[1])
    femm.mi_seteditmode("blocks")

    coil_center = [(coil_top_left[0]+coil_bottom_right[0])/2,(coil_top_left[1]+coil_bottom_right[1])/2]

    femm.mi_addblocklabel(coil_center[0], coil_center[1])
    femm.mi_selectlabel(coil_center[0], coil_center[1])
    # Turns divided by 2 going into and out of the page for each half
    femm.mi_setblockprop(wire_selection_awg, 1, 0,"Coil", 0, coil_group, direction_scale*turns/2) 

femm.mi_clearselected()

#
# Plunger
#
plunger_length = 0.020 # m
plunger_center_offset = 0.015 # m distance away the leading edge is from the center of coils length 
plunger_group = 1

# x,y top left and bottom right of the rectangle
femm.mi_seteditmode("nodes")
plunger_top_left = [-(coil_inner_width-plunger_margin), -plunger_center_offset]
plunger_bottom_right = [(coil_inner_width-plunger_margin), -(plunger_center_offset + plunger_length)]
femm.mi_drawrectangle(plunger_top_left[0], plunger_top_left[1], plunger_bottom_right[0], plunger_bottom_right[1])
femm.mi_seteditmode("blocks")
plunger_center = [(plunger_top_left[0]+plunger_bottom_right[0])/2,(plunger_top_left[1]+plunger_bottom_right[1])/2]

femm.mi_addblocklabel(plunger_center[0],plunger_center[1])
femm.mi_selectlabel(plunger_center[0],plunger_center[1])
femm.mi_setblockprop('1020 Steel',1,0,"","",plunger_group)
femm.mi_clearselected()

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
kicker_board_capacitance = 0.002 # Farads
tau = coil_resistance * kicker_board_capacitance

golf_ball_restitution = 0.7

d_total = 0 # m
a_inst = 0 # m/s^2
m = 0.061 # kg
delta_t = 0.01 # s
travel_dist = 0.015 # m
for t_whole in range(0,60):
    # i=− V_0/R *e^(-t/tau)
    current_inst = (initial_voltage / coil_resistance) * math.exp(-(t_whole*delta_t) / tau)
    current_samples.append(current_inst)
    femm.mi_setcurrent("Coil", current_inst)
    femm.mi_analyze()
    femm.mi_loadsolution()
    femm.mo_groupselectblock(1)
    f_inst = femm.mo_blockintegral(19) # Newtons
    # f = ma
    a_inst = f_inst / m 
    input()
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
