#pragma once
#include <Eigen/Dense>

namespace drivetrain_controls {

    inline static Eigen::Matrix<double, 3, 3> make_dynamics_matrix() {
        return (Eigen::Matrix<double, 3, 3>() << 1, 0, 0, 
                                                 0, 1, 0, 
                                                 0, 0, 1).finished();
    }

    inline static Eigen::Matrix<double, 3, 4> make_control_matrix() {
        return (Eigen::Matrix<double, 3, 4>() << -8.23333e-05, -0.000116437, 0.000116437, 8.23333e-05, 
                                                 7.85058e-05, -7.85058e-05, -7.85058e-05, 7.85058e-05, 
                                                 0.000681965, 0.000835234, 0.000835234, 0.000681965).finished();
    }

    inline static Eigen::Matrix<double, 5, 3> make_output_matrix() {
        return (Eigen::Matrix<double, 5, 3>() << -20.2429, 35.0618, 3.29555, 
                                                 -28.6278, -28.6278, 3.29555, 
                                                 28.6278, -28.6278, 3.29555, 
                                                 20.2429, 35.0618, 3.29555, 
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
        return (Eigen::Matrix<double, 5, 5>() << 1.18682e-05, 0, 0, 0, 0, 
                                                 0, 1.18682e-05, 0, 0, 0, 
                                                 0, 0, 1.18682e-05, 0, 0, 
                                                 0, 0, 0, 1.18682e-05, 0, 
                                                 0, 0, 0, 0, 0.00244346).finished();
    }

    inline static Eigen::Matrix<double, 3, 5> make_ss_kalman_gain_matrix() {
        return (Eigen::Matrix<double, 3, 5>() << -0.00823069, -0.0116399, 0.0116399, 0.00823069, 1.57551e-18, 
                                                 0.00786165, -0.00783362, -0.00783362, 0.00786165, -1.14777e-06, 
                                                 0.06698, 0.0820302, 0.0820302, 0.06698, 0.00011093).finished();
    }

}