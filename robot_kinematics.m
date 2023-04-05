clear;clc;close all
syms theta_robot x1(t) y1(t) phi_w1 phi_w2 phi_w3 phi_w4
syms theta_dot_robot(t) x1_dot(t) y1_dot(t)
syms theta1(t) theta2(t) theta3(t) theta4(t)
syms theta1_dot(t) theta2_dot(t) theta3_dot(t) theta4_dot(t)
syms r_wheel l_center_to_wheel

syms vel_body_inertia_frame [3 1]
vel_body_inertia_frame(1) = x1_dot;
vel_body_inertia_frame(2) = y1_dot;
vel_body_inertia_frame(3) = theta_dot_robot


% rotation matrix that transforms from inertial frame to robot frame
R_inertial_to_robot = [[cos(theta_robot), sin(theta_robot), 0];[-sin(theta_robot), cos(theta_robot), 0];[0,0,1]]

%kinematics that goes from body velocities to wheel velocities
Transform_body_vels_to_wheel_vels = [[-sin(phi_w1), cos(phi_w1), l_center_to_wheel];...
                                     [-sin(phi_w2), cos(phi_w2), l_center_to_wheel];...
                                     [-sin(phi_w3), cos(phi_w3), l_center_to_wheel];...
                                     [-sin(phi_w4), cos(phi_w4), l_center_to_wheel]]

%calculate wheel velocities
wheel_vels = (-1/r_wheel) * Transform_body_vels_to_wheel_vels * R_inertial_to_robot * vel_body_inertia_frame

eqn1 = theta1_dot(t) == wheel_vels(1);
eqn2 = theta2_dot(t) == wheel_vels(2);
eqn3 = theta3_dot(t) == wheel_vels(3);
eqn4 = theta4_dot(t) == wheel_vels(4);

%print the first equation as an example
pretty(eqn1)
pretty(simplify(eqn1))

