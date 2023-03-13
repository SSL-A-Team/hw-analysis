import femm
import matplotlib.pyplot as plt

femm.openfemm()
femm.opendocument("S-22-150-HF Solenoid Plunger.fem");
femm.mi_saveas("temp.fem")
femm.mi_seteditmode("group")
z=[];
f=[];
t=[];
v_i = 0
d = 0
a = 0
m = 1 # TODO 
delta_t = 0.1
travel_dist = 0.4921258333
for t_whole in range(0,20):
    femm.mi_analyze()
    femm.mi_loadsolution()
    femm.mo_groupselectblock(1)
    f_inst=femm.mo_blockintegral(19)
    # f = ma
    a = f_inst / m
    v_f = v_i + a*delta_t
    delta_d = (v_i + v_f)/2 * delta_t
    d = d + delta_d
    t.append(t,t_whole*delta_t)
    z.append(z,d)
    f.append(f,f_inst)
    if (d > travel_dist):
        # Gone to end of stop
        break
    femm.mi_selectgroup(1)
    femm.mi_movetranslate(0, delta_d)

femm.closefemm()
plt.subplot(1,2,1)
plt.plot(t,z)
plt.xlabel('Time, s')
plt.ylabel('Offset, in')
plt.subplot(1,2,2)
plt.plot(t,f)
plt.xlabel('Time, s')
plt.ylabel('Force, N')
plt.show()
