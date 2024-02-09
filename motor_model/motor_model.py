from matplotlib import pyplot as plt
import numpy as np

def delete_lines_with_prefix(file_path, prefix):
    # Read the content of the file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Filter out lines starting with the specified prefix
    filtered_lines = [line for line in lines if not line.startswith(prefix)]
    new_path = "new_" + file_path
    # Write the filtered lines back to the file
    with open(new_path, 'w') as file:
        file.writelines(filtered_lines)

data = {"FL": {}, "BL": {}, "BR": {}, "FR": {}}

def process_model(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    for line in lines:
        data_split = line.split()
        if len(data_split) > 2 and data_split[1] == "INFO" and data_split[2] == "ROBOT":
            fl_dutycycle = float(data_split[12])
            fl_rads = float(data_split[18])

            bl_dutycycle = float(data_split[13])
            bl_rads = float(data_split[19])

            br_dutycycle = float(data_split[14])
            br_rads = float(data_split[20])

            fr_dutycycle = float(data_split[15])
            fr_rads = float(data_split[21])

            if fl_dutycycle in data["FL"]:
                data["FL"][fl_dutycycle].append(fl_rads)
            else:
                data["FL"][fl_dutycycle] = [fl_rads]

            if bl_dutycycle in data["BL"]:
                data["BL"][bl_dutycycle].append(bl_rads)
            else:
                data["BL"][bl_dutycycle] = [bl_rads]

            if br_dutycycle in data["BR"]:
                data["BR"][br_dutycycle].append(br_rads)
            else:
                data["BR"][br_dutycycle] = [br_rads]

            if fr_dutycycle in data["FR"]:
                data["FR"][fr_dutycycle].append(fr_rads)
            else:
                data["FR"][fr_dutycycle] = [fr_rads]

    fl = np.array([[0,0]])
    for dutycycle_key in data["FL"].keys():
        fl = np.append(fl, [[dutycycle_key, sum(data["FL"][dutycycle_key])/len(data["FL"][dutycycle_key])]], axis = 0) 

    bl = np.array([[0,0]])
    for dutycycle_key in data["BL"].keys():
        bl = np.append(bl, [[dutycycle_key, sum(data["BL"][dutycycle_key])/len(data["BL"][dutycycle_key])]], axis = 0) 

    br = np.array([[0,0]])
    for dutycycle_key in data["BR"].keys():
        br = np.append(br, [[dutycycle_key, sum(data["BR"][dutycycle_key])/len(data["BR"][dutycycle_key])]], axis = 0) 

    fr = np.array([[0,0]])
    for dutycycle_key in data["FR"].keys():
        fr = np.append(fr, [[dutycycle_key, sum(data["FR"][dutycycle_key])/len(data["FR"][dutycycle_key])]], axis = 0) 

    # Delete filler point for appending
    fl = np.delete(fl, 0, 0)
    bl = np.delete(bl, 0, 0)
    br = np.delete(br, 0, 0)
    fr = np.delete(fr, 0, 0)

    fig, axs = plt.subplots(2)
    fig.suptitle('Vertically stacked subplots')
    axs[0].plot(fl[:,1], fl[:,0], label="FL", marker=".")
    axs[0].plot(bl[:,1], bl[:,0], label="BL", marker=".")
    axs[0].plot(br[:,1], br[:,0], label="BR", marker=".")
    axs[0].plot(fr[:,1], fr[:,0], label="FR", marker=".")
    axs[0].legend()

    # Total array
    total = np.array([[0,0]])
    total = np.append(total, fl, axis = 0)
    total = np.append(total, bl, axis = 0)
    total = np.append(total, br, axis = 0)
    total = np.append(total, fr, axis = 0)

    # Delete filler point for appending
    total = np.delete(total, 0, 0)

    # Get indices that would sort the first column
    sorted_indices = np.argsort(total[:, 0])

    # Use the sorted indices to reorder the array
    total = total[sorted_indices]

    # Delete rows with rads 0
    rows_to_delete = np.where(total[:, 1] == 0)
    total = np.delete(total, rows_to_delete, axis=0)

    axs[1].scatter(total[:,1], total[:,0], label='All')

    # Fit polynomial 
    coefficients = np.polyfit(total[:,1], total[:,0], 1)

    print("Coefficients: " + str(coefficients))

    poly_fit = np.poly1d(coefficients)
    y_fit = poly_fit(total[:,1])
    axs[1].plot(total[:,1], y_fit, label='Least-Squares Fit', marker="_")
    
    # Choose the column for which you want to create a linearly spaced array
    column_values = total[:, 1]

    # Calculate the minimum and maximum values in the selected column
    min_value = np.min(column_values)
    max_value = np.max(column_values)

    # Create a linearly spaced array based on the minimum and maximum values
    linearly_spaced_array = np.linspace(min_value, max_value, num=40)

    max_rads = 5260 * 0.1047
    current_motor_y = linearly_spaced_array / max_rads
    axs[1].plot(linearly_spaced_array, current_motor_y, label='Expected', marker="_")



    axs[1].legend()
    plt.show()


def plot_capture(file_path):

    data2 = {"FL": {}, "BL": {}, "BR": {}, "FR": {}}

    with open(file_path, 'r') as file:
        lines = file.readlines()

    fl = np.array([[0,0,0,0]])
    bl = np.array([[0,0,0,0]])
    br = np.array([[0,0,0,0]])
    fr = np.array([[0,0,0,0]])

    target = [-32.30769231, -33.88663968, -33.88663968, -32.30769231]


    for line in lines:
        data_split = line.split()
        if len(data_split) > 2 and data_split[1] == "INFO" and data_split[2] == "ROBOT":
            time = float(data_split[0])
            
            fl_set_point = float(data_split[7])
            fl_measured_rads = float(data_split[18])

            bl_set_point = float(data_split[8])
            bl_measured_rads = float(data_split[19])

            br_set_point = float(data_split[9])
            br_measured_rads = float(data_split[20])

            fr_set_point = float(data_split[10])
            fr_measured_rads = float(data_split[21])

            fl = np.append(fl,[[time, fl_set_point, fl_measured_rads, 100.0*(target[0]-fl_measured_rads)/(target[0]+0.00000001)]], axis=0)
            bl = np.append(bl,[[time, bl_set_point, bl_measured_rads, 100.0*(target[1]-bl_measured_rads)/(target[1]+0.00000001)]], axis=0)
            br = np.append(br,[[time, br_set_point, br_measured_rads, 100.0*(target[2]-br_measured_rads)/(target[2]+0.00000001)]], axis=0)
            fr = np.append(fr,[[time, fr_set_point, fr_measured_rads, 100.0*(target[3]-fr_measured_rads)/(target[3]+0.00000001)]], axis=0)

    # Delete filler point for appending
    fl = np.delete(fl, 0, 0)
    bl = np.delete(bl, 0, 0)
    br = np.delete(br, 0, 0)
    fr = np.delete(fr, 0, 0)

    fig, axs = plt.subplots(2)
    fig.suptitle('Vertically stacked subplots')
    axs[0].plot(fl[:,0], fl[:,2], label="FL", marker=".")
    axs[0].plot(bl[:,0], bl[:,2], label="BL", marker=".")
    axs[0].plot(br[:,0], br[:,2], label="BR", marker=".")
    axs[0].plot(fr[:,0], fr[:,2], label="FR", marker=".")
    axs[0].axhline(target[0], label="Target F", marker="_", color ='black')
    axs[0].axhline(target[1], label="Target B", marker="_", color ='gray')

    print("File '" + file_path + "' Average error: " +
        str(np.average(fl[:,3])) + " " +\
        str(np.average(bl[:,3])) + " " +\
        str(np.average(br[:,3])) + " " +\
        str(np.average(fr[:,3])))

    axs[0].legend()
    axs[1].set_title('Percent Error from Expected Setpoint')
    axs[1].plot(fl[:,0], fl[:,3], label="FL", marker=".")
    axs[1].plot(bl[:,0], bl[:,3], label="BL", marker=".")
    axs[1].plot(br[:,0], br[:,3], label="BR", marker=".")
    axs[1].plot(fr[:,0], fr[:,3], label="FR", marker=".")
    axs[1].legend()
    plt.show()

# Example usage:
file_path = "Model3_p_1_i_0.0001.txt"  # Replace with the path to your text file
prefix_to_delete = "â””â”€"  # Replace with the specific character you want to filter

delete_lines_with_prefix(file_path, prefix_to_delete)
#process_model("new_" + file_path)
plot_capture("new_" + file_path)