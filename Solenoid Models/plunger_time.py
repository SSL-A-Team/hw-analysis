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
m = 0.0538641 # kg
delta_t = 0.1 # s
travel_dist = 0.015 # m
for t_whole in range(0,20):
    femm.mi_analyze()
    femm.mi_loadsolution()
    femm.mo_groupselectblock(1)
    f_inst = femm.mo_blockintegral(19) # Newtons
    
    # f = ma
    a_inst = f_inst / m 

    v_f = v_i + a_inst*delta_t
    delta_d = (v_i + v_f)/2 * delta_t
    d_total = d_total + delta_d
    t.append(t,t_whole*delta_t)
    z.append(z,d_total)
    f.append(f,f_inst)
    if (d_total >= travel_dist):
        # Gone to end of stop
        break
    # Next round initial velocity is current final velocity
    v_i = v_f
    femm.mi_selectgroup(1)
    femm.mi_movetranslate(0, delta_d*METER_TO_IN) # Inches

femm.closefemm()

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
