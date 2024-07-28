import numpy as np


class RobotModel:
    """
    Calculates and returns matrices for our current system model
    """

    def __init__(self):
        # FL, BL, BR, FR with X positive
        self.wheel_angles = np.deg2rad([330, 45, 135, 210])
        self.wheel_dist = 0.0814
        self.wheel_radius = 0.0247

        # Noises
        self.init_variance = 0.1 # Diagonal of P matrix is variance at the start of the filter running, which should be small at start
        # Assume initial covariance between sensors is zero
        self.process_noise = 0.05
        encoder_noise_rads = np.radians(0.068) # rads for AS5047P encoder RMS output noise (1 sigma)
        encoder_sampling_period = 0.01 # s
        self.encoder_noise = encoder_noise_rads/(1/encoder_sampling_period)

        gyro_noise_noise_density = 0.007  # deg/s/√Hz for BMI085 Noise density (typ.)
        # TODO find maximum rotation speed
        # 
        gyro_sampling_freq = 100 # Hz TODO data rate reporting tolerance 
        self.gyro_noise = np.radians(gyro_noise_noise_density) * np.sqrt(gyro_sampling_freq) * 1/10000 # in rad/s

        # Dimensions:
        self.num_states = 3 # [v_x, v_y, w_z]
        self.num_inputs = 4 # [w_i_fl, w_i_bl, w_i_br, w_i_fr]
        self.num_outputs = 5 # [w_o_fl, w_o_bl, w_o_br, w_o_fr, w_gyro]

    # System dynamics
    def get_A_matrix(self):
        A = np.zeros((self.num_states, self.num_states))
        return A

    # System Input Model
    def get_B_matrix(self):
        B = np.zeros((self.num_states, self.num_inputs))
        T_body_to_wheel = self.get_T_body_to_wheel()
        # Jacobian is the pseudo-inverse aka T_wheel_to_robot for inverse kinematics
        B = np.linalg.pinv(T_body_to_wheel)
        return B

    # Observation model
    def get_H_matrix(self):
        H = np.zeros((self.num_outputs, self.num_states))
        H[0:4,:] = self.get_T_body_to_wheel()
        H[4, :] = np.array([0, 0, 1])
        return H

    # Feedthrough matrix
    def get_D_matrix(self):
        D = np.zeros((self.num_outputs, self.num_inputs))
        return D

    # Estimation Covariance
    def get_P_init_matrix(self):
        P = np.eye(self.num_states) * self.init_variance
        return P

    # Covariance of the process noise
    def get_Q_matrix(self):
        Q = np.round(3.0 * self.process_noise * 0.0001 * np.eye(self.num_states), 10)
        return Q

    # Covariance of the observation noise
    def get_R_matrix(self):
        R = np.eye(self.num_outputs)
        R[:4, :4] *= self.encoder_noise
        R[4, 4] *= self.gyro_noise
        return R

    def generate_model(self):
        return {
            "A": self.get_A_matrix(),
            "B": self.get_B_matrix(),
            "H": self.get_H_matrix(),
            "D": self.get_D_matrix(),
            "P": self.get_P_init_matrix(),
            "Q": self.get_Q_matrix(),
            "R": self.get_R_matrix(),
        }

    def get_T_body_to_wheel(self):
        #       ^   Vx
        #       |
        # Vy <--- 
        #
        # https://www.mdpi.com/2076-3417/12/12/5798
        T_body_to_wheel = np.zeros((self.num_inputs, self.num_states))
        for i, angle in enumerate(self.wheel_angles):
           T_body_to_wheel[i, :] = np.array([np.cos(angle), np.sin(angle), -self.wheel_dist])
        T_body_to_wheel /= -self.wheel_radius

        return T_body_to_wheel
    
    def get_T_wheel_to_body(self):
        #       ^   Vx
        #       |
        # Vy <--- 
        #
        # https://www.mdpi.com/2076-3417/12/12/5798
        T_wheel_to_body = self.get_T_body_to_wheel()

        return np.linalg.pinv(T_wheel_to_body)