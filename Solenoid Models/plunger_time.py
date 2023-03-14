import math
import femm
import matplotlib.pyplot as plt

METER_TO_IN = 39.3701

femm.openfemm()
femm.opendocument("S-22-150-HF Solenoid Plunger.fem");
femm.mi_saveas("temp.fem")
femm.mi_seteditmode("group")
z=[];
f=[];
t=[];
v_i = 0 # m/s
v_f = 0 # m/s

d_total = 0 # m
a_inst = 0 # m/s^2
m = 0.061 # kg
delta_t = 0.0001 # s
travel_dist = 0.015 # m
for t_whole in range(0,60):
    femm.mi_analyze()
    femm.mi_loadsolution()
    femm.mo_groupselectblock(1)
    f_inst = femm.mo_blockintegral(19) # Newtons
    
    # f = ma
    a_inst = f_inst / m 

    v_f = v_i + a_inst*delta_t
    delta_d = (v_i + v_f)/2 * delta_t
    d_total = d_total + delta_d
    t.append(t_whole*delta_t)
    z.append(d_total)
    f.append(f_inst)
    if (d_total >= travel_dist):
        # Gone to end of stop
        break
    # Next round initial velocity is current final velocity
    v_i = v_f
    femm.mi_selectgroup(1)
    femm.mi_movetranslate(0, delta_d*METER_TO_IN) # Inches

femm.closefemm()

# plunger weight: 55g
# boot weight: 6g
# total kicker weight: 61g


# E = m * v^2
# m_ball * v_ball^2 = m_plunger * v_plunger^2
# v_ball = sqrt((m_plunger * v_plunger^2) / m_ball)
v_ball = 0.8*math.sqrt((m * v_f**2) / 0.0459)
print(f"Expected ball velocity: {v_ball} m/s")

print("Avg. Force:" + repr(sum(f)/len(f)))
plt.subplot(1,2,1)
plt.plot(t,z)
plt.xlabel('Time, s')
plt.ylabel('Offset, m')
plt.subplot(1,2,2)
plt.plot(t,f)
plt.xlabel('Time, s')
plt.ylabel('Force, N')
plt.show()
