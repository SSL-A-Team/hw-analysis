import math
import femm
import matplotlib.pyplot as plt
import csv

METER_TO_IN = 39.3701
# part number, solenoid outer diameter (mm), solenoid inner diameter (mm), solenoid length (mm), plunger length (mm), awg, coil resistance (ohm), turns
solenoid_info = [
#["S-63-38-SH", 9.652, 2.413,   16.764, 13.894, 31, 1.93, 197.825]]
#["S-69-38-H",  9.7,   3.734,   17.5,   11.271,  31, 2.29, 250.8095238],
#["S-10-38-H",  9.7,   3.734,   25.4,   17.177,  30, 2.54, 320.2608696],
#["S-10-50-H",  12.7,  4.775,   25.4,   17.177, 28, 2.25, 360],
#["S-16-50-H",  12.7,  4.775,   40.64,  29.178, 27, 2.33, 494.2424242],
#["S-15-75-H",  19.05, 7.9502,  38.1,   26.702, 26, 2.68, 460.2608696],
["S-20-90-H",  23,    11.0998,  50.8,  36.1,  25, 2.5 , 429.6875]]
#["S-20-100-H", 25.4,  11.0998,  50.8,  35.719,  24, 2.95, 606.3888889],
#["S-20-125-H", 31.8,  11.0998,  50.8,  35.719,  23, 2.7 , 615.7894737],
#["S-25-125-H", 31.75, 11.0998,  63.5,  45.244,  22, 2.49, 688.4117647],
#["S-22-150-H", 38.1,  15.7988,  55.626,37.052,  21, 1.9 , 518.1818182],
#["S-29-150-H", 38.1,  15.7988,  72.39, 49.625,  21, 2.6 , 712.9032258]]

initial_voltage = 170  # volts
kicker_board_capacitance = 0.002 # Farads
golf_ball_restitution = 0.7
plunger_margin = 0.99 # % of inner diameter
coil_group = 1
plunger_group = 2
solenoid_results = [[]]

for solenoid in solenoid_info:
    femm.openfemm()
    femm.opendocument("Bought Solenoid Plunger.fem");
    femm.mi_saveas("temp.fem")
    femm.mi_seteditmode("group")

    name = solenoid[0]
    solenoid_outer = solenoid[1]/1000 
    solenoid_inner = solenoid[2]/1000
    solenoid_length = solenoid[3]/1000
    plunger_length = solenoid[4]/1000
    awg = str(solenoid[5]) + " AWG"
    coil_resistance = solenoid[6]
    turns = solenoid[7]

    print(name)

    # Coil generation
    femm.mi_seteditmode("nodes")

    # r,z top left and bottom right of the rectangle
    coil_top_left = [solenoid_inner, solenoid_length/2]
    coil_bottom_right = [solenoid_outer, -solenoid_length/2]
    femm.mi_drawrectangle(coil_top_left[0], coil_top_left[1], coil_bottom_right[0], coil_bottom_right[1])
    femm.mi_selectrectangle(coil_top_left[0], coil_top_left[1], coil_bottom_right[0], coil_bottom_right[1], 0)
    femm.mi_setnodeprop("",coil_group)
    femm.mi_clearselected()
    femm.mi_seteditmode("blocks")

    coil_center = [(coil_top_left[0]+coil_bottom_right[0])/2,(coil_top_left[1]+coil_bottom_right[1])/2]

    femm.mi_addblocklabel(coil_center[0], coil_center[1])
    femm.mi_selectlabel(coil_center[0], coil_center[1])
    femm.mi_setblockprop(awg, 1, 0,"Coil", 0, coil_group, turns) 

    femm.mi_clearselected()

    #
    # Plunger
    #
    plunger_center_offset = plunger_length/2 # m distance away the leading edge is from the center of coils length 
    

    # r,z top left and bottom right of the rectangle
    femm.mi_seteditmode("nodes")
    plunger_top_left = [0, -plunger_center_offset]
    plunger_bottom_right = [solenoid_inner*plunger_margin, -(plunger_center_offset + plunger_length)]
    femm.mi_drawrectangle(plunger_top_left[0], plunger_top_left[1], plunger_bottom_right[0], plunger_bottom_right[1])
    femm.mi_selectrectangle(plunger_top_left[0], plunger_top_left[1], plunger_bottom_right[0], plunger_bottom_right[1], 0)
    femm.mi_setnodeprop("",plunger_group)
    femm.mi_clearselected()
    femm.mi_seteditmode("blocks")
    plunger_center = [(plunger_top_left[0]+plunger_bottom_right[0])/2,(plunger_top_left[1]+plunger_bottom_right[1])/2]

    femm.mi_addblocklabel(plunger_center[0],plunger_center[1])
    femm.mi_selectlabel(plunger_center[0],plunger_center[1])
    femm.mi_setblockprop('1020 Steel',1,0,"","",plunger_group) 
    femm.mi_clearselected()

    plunger_displacement_samples=[];
    force_samples=[];
    time_samples=[];
    current_samples=[]
    prev_velocity = 0 # m/s
    velocity = 0 # m/s

    # Variables for modeling current decay in coil

    tau = coil_resistance * kicker_board_capacitance
    stroke_length = plunger_length/2 # mm

    d_total = 0 # m
    a_inst = 0 # m/s^2
    m = 0.061 # kg
    delta_t = 0.1 # s
    for t_whole in range(0,60):
        input()
        # i=− V_0/R *e^(-t/tau)
        current_inst = (initial_voltage / coil_resistance) * math.exp(-(t_whole*delta_t) / tau)
        current_samples.append(current_inst)
        femm.mi_setcurrent("Coil", current_inst)

        femm.mi_analyze()
        input()
        femm.mi_loadsolution()
        input()
        femm.mo_groupselectblock(plunger_group)
        f_inst = femm.mo_blockintegral(19) # Newtons
        input()
        # f = ma
        a_inst = f_inst / m 

        print(a_inst)
        print(f_inst)
        velocity = prev_velocity + a_inst*delta_t
        delta_d = (prev_velocity + velocity)/2 * delta_t
        d_total = d_total + delta_d
        time_samples.append(t_whole*delta_t)
        plunger_displacement_samples.append(d_total)
        force_samples.append(f_inst)
        if (d_total >= stroke_length):
            # Gone to end of stop
            break
        # Next round initial velocity is current final velocity
        prev_velocity = velocity
        femm.mi_selectgroup(1)
        input()
        femm.mi_movetranslate(0, delta_d) # m

    femm.closefemm()

    solenoid_results[name] = [time_samples,force_samples]

    # plunger weight: 55g
    # boot weight: 6g
    # total kicker weight: 61g

    # 6.35mm of contact travel w/ ball

    # E = m * v^2
    # m_ball * v_ball^2 = m_plunger * v_plunger^2
    # v_ball = sqrt((m_plunger * v_plunger^2) / m_ball)
    v_ball = golf_ball_restitution*math.sqrt((m * velocity**2) / 0.0459)
    print(f"Expected ball velocity: {v_ball} m/s")






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
