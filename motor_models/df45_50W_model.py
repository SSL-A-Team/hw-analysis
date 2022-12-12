#!/usr/bin/env python3

import matplotlib.pyplot as plt
from scipy import stats

###########################
#  Known Motor Constants  #
###########################

nanotec_df45_50W_rated_torque_Nm = 0.084
# nanotec_df45_50W_torque_data_points_Nm = [0.011, 0.027, 0.048, 0.060, 0.081, 0.084, 0.111, 0.271, 0.376,  0.459,  0.481 ]
# nanotec_df45_50W_vel_data_points_RPM =   [6065,  5781,  5518,  5385,  5174,  5140,  4840,  3017,  2011,   1017,   544   ]
# nanotec_df45_50W_current_consumption_A = [0.505, 0.797, 1.340, 1.690, 2.260, -1,    3.060, 7.150, 10.460, 13.470, 13.940]
# exclude 0.084 data point because for some reason data is incomplete there
nanotec_df45_50W_torque_data_points_Nm = [0.011, 0.027, 0.048, 0.060, 0.081, 0.111, 0.271, 0.376,  0.459,  0.481 ]
nanotec_df45_50W_vel_data_points_RPM =   [6065,  5781,  5518,  5385,  5174,  4840,  3017,  2011,   1017,   544   ]
nanotec_df45_50W_current_consumption_A = [0.505, 0.797, 1.340, 1.690, 2.260, 3.060, 7.150, 10.460, 13.470, 13.940]

torques = nanotec_df45_50W_torque_data_points_Nm
currents = nanotec_df45_50W_current_consumption_A

m_t2c, b_t2c, r_value_t2c, p_value_t2c, std_err_t2c = stats.linregress(torques, currents)
m_c2t, b_c2t, r_value_c2t, p_value_c2t, std_err_c2t = stats.linregress(currents, torques)

m_t2c = round(m_t2c, 5)
b_t2c = round(b_t2c, 5)
r_value_t2c = round(r_value_t2c, 5)
m_c2t = round(m_c2t, 5)
b_c2t = round(b_c2t, 5)
r_value_c2t = round(r_value_c2t, 5)

print("Units: Current (A), Torque (nM)")
print(f"regression for current to torque: I   = {m_t2c}*tau + {b_t2c}")
print(f"regression for torque to current: tau = {m_c2t}*I   + {b_c2t}")



