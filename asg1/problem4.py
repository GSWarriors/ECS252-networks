import matplotlib.pyplot as plt
import math

def main():

    x_coords = []
    y_coords = []
    std_dev_vals = []

    ro = 0.1
    while ro < 0.9:
        mean_val = 0
        std_dev = 0

        mean_val = ro/(1 - ro)

        std_dev = math.sqrt(mean_val*(1/(1- ro)))


        x_coords.append(ro)
        y_coords.append(mean_val)
        std_dev_vals.append(std_dev)

        ro += 0.1


    #plt.scatter(x_coords, y_coords)
    #plt.xlabel("ro")
    #plt.ylabel("Mean number of packets in system")
    #plt.show()

    plt.scatter(x_coords, std_dev_vals)
    plt.xlabel("ro")
    plt.ylabel("Standard deviation of packets in system")
    plt.show()






main()
