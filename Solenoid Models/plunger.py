import femm
import matplotlib.pyplot as plt

femm.openfemm()
femm.opendocument("S-22-150-HF Solenoid Plunger.fem");
femm.mi_saveas("temp.fem")
femm.mi_seteditmode("group")
z=[];
f=[];
for n in range(0,20):
	femm.mi_analyze()
	femm.mi_loadsolution()
	femm.mo_groupselectblock(1)
	fz=femm.mo_blockintegral(19)
	z.append(n*0.04921258333)
	f.append(fz)
	femm.mi_selectgroup(1)
	femm.mi_movetranslate(0, 0.04921258333)
femm.closefemm()
plt.plot(z,f)
plt.ylabel('Force, N')
plt.xlabel('Offset, in')
plt.show()
