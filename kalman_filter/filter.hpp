#pragma once
#include <Eigen/Dense>

namespace drivetrain_controls {

    inline static Eigen::Matrix<double, 3, 3> make_dynamics_matrix() {
        return (Eigen::Matrix<double, 3, 3>() << 1, 0, 0, 
                                                 0, 1, 0, 
                                                 0, 0, 1).finished();
    }

    inline static Eigen::Matrix<double, 3, 4> make_control_matrix() {
        return (Eigen::Matrix<double, 3, 4>() << 0, 0, 0, 0, 
                                                 0, 0, 0, 0, 
                                                 0, 0, 0, 0).finished();
    }

    inline static Eigen::Matrix<double, 5, 3> make_output_matrix() {
        return (Eigen::Matrix<double, 5, 3>() << 20.4082, 35.348, 3.46939, 
                                                 20.4082, -35.348, 3.46939, 
                                                 -28.8615, -28.8615, 3.46939, 
                                                 -28.8615, 28.8615, 3.46939, 
                                                 0, 0, 1).finished();
    }

    inline static Eigen::Matrix<double, 5, 4> make_feed_forward_matrix() {
        return (Eigen::Matrix<double, 5, 4>() << 0, 0, 0, 0, 
                                                 0, 0, 0, 0, 
                                                 0, 0, 0, 0, 
                                                 0, 0, 0, 0, 
                                                 0, 0, 0, 0).finished();
    }

    inline static Eigen::Matrix<double, 3, 3> make_process_noise_matrix() {
        return (Eigen::Matrix<double, 3, 3>() << 1.5e-05, 0, 0, 
                                                 0, 1.5e-05, 0, 
                                                 0, 0, 1.5e-05).finished();
    }

    inline static Eigen::Matrix<double, 5, 5> make_observation_noise_matrix() {
        return (Eigen::Matrix<double, 5, 5>() << 0.118, 0, 0, 0, 0, 
                                                 0, 0.118, 0, 0, 0, 
                                                 0, 0, 0.118, 0, 0, 
                                                 0, 0, 0, 0.118, 0, 
                                                 0, 0, 0, 0, 0.00244).finished();
    }

    inline static Eigen::Matrix<double, 3, 5> make_ss_kalman_gain_matrix() {
        return (Eigen::Matrix<double, 3, 5>() << 0.00357313, 0.00357313, -0.00486448, -0.00486448, 0.00108943, 
                                                 0.0043247, -0.0043247, -0.0035311, 0.0035311, -2.80598e-19, 
                                                 0.00425502, 0.00425502, 0.00314511, 0.00314511, 0.0529033).finished();
    }

}