
##########################
# User Params
##########################

# conversions folks might want...
KG_PER_LB = 0.4535
MM_PER_IN = 25.4

# robot params
robot_weight_kg = 2.5
robot_wheel_radius_mm = 25
# seems like 1:1.9 is good for 50W and 1:1.2 for 65W
# mu=0.7 suggest 1:13 for 50W and 1:1 for 65W
robot_gear_ratio = "1:1.3"  # "motor:wheel", does not support more than 2 gears

# motor options
df45_50_rated_torque_Nm = 8.4 / 100       # datasheet rates nominal torque at 8.4 Ncm
df45_50_rated_rpm = 5260
df45_65_rated_torque_Nm = 13 / 100        # datasheet rates nominal torque at 13 Ncm
df45_65_rated_rpm = 4840

# choose motor
motor_nominal_torque = df45_50_rated_torque_Nm
motor_nominal_rpm = df45_50_rated_rpm

# more principled analysis seems to indicate this is very close to 1
# however we have to consider that imperfections in controls and design specific to RC
# may lower this conceptually. Based on Joe's GH link maybe this should be closer to 0.7
# which reflects what accelerations some dev A teams claimed they saw in practice
# not coincidentally this very very close to 1 / sqrt(2) which would be a wheel angle
# multiplier
mu_wheel_to_floor = 0.7

##############################
# calculations
##############################

F_GRAV_M_PER_S = 9.81
NUM_WHEELS = 4
wheel_radius_m = robot_wheel_radius_mm / 1000

def parse_gear_ratio(ratio_str):
    components = ratio_str.split(":")
    if len(components) != 2:
        print("invalid gear ratio format")
        exit(1)

    driver = float(components[0])
    driven = float(components[1])
    ratio = driven / driver
    return ratio


gear_ratio = parse_gear_ratio(robot_gear_ratio)

# can't apply force beyond that of gravity without active wheel technology (like glue or velcro)
f_grav_robot = F_GRAV_M_PER_S * robot_weight_kg             # calc force of gravity
f_grav_per_wheel_4 = f_grav_robot / NUM_WHEELS              # calc force per wheel
f_per_wheel_4 = f_grav_per_wheel_4 * mu_wheel_to_floor      # apply mu
t_per_wheel = wheel_radius_m * f_per_wheel_4                # calc torque per wheel

torque_baseline_negative_slack = t_per_wheel - motor_nominal_torque
print(f"Torque Negative Slack (max theoretical): {torque_baseline_negative_slack}")
if torque_baseline_negative_slack < 0:
    print("NOTE: motor has sufficient torque without gearing")
else:
    sugg_ratio = 1 + (torque_baseline_negative_slack / motor_nominal_torque)
    print(f"NOTE: suggested ratio (max theoretical): \"1:{sugg_ratio}\"\n")
    print(f"Selected ratio \"{robot_gear_ratio}\"")
    adjusted_motor_nominal_torque = motor_nominal_torque * gear_ratio
    adjusted_torque_negative_slack = t_per_wheel - adjusted_motor_nominal_torque
    print(f"Adjusted Torque Negative Slack (max theoretical): {adjusted_torque_negative_slack}")
    if adjusted_torque_negative_slack < 0:
        print("torque adjusted sufficiently")
    else:
        print("torque insufficient.")

    print("\n")
    max_theo_accel_at_bot_weight = (f_grav_robot / robot_weight_kg) * mu_wheel_to_floor
    print(f"Max Theoretical Acceleration at Robot Weight + Mu: {max_theo_accel_at_bot_weight}")

    adjusted_motor_nominal_speed = motor_nominal_rpm / gear_ratio
    amns_rps = adjusted_motor_nominal_speed / 60
    wheel_linear_speed = amns_rps * 2.0 * wheel_radius_m * 3.1415
    print(f"Adjusted Robot Top Speed: {wheel_linear_speed}")


