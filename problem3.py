import matplotlib.pyplot as plt
import math



def main():
    #n is amount of users
    #p is prob that node is active

    #we have congestion when number of users is greater than 1mb/200kb,
    #max capacity without congestion is 5
    #which is 6


    max_users = 100
    p = 0.2
    x_coords = []
    y_coords = []

    for N in range(0, max_users):

        if N <= 5:
            x_coords.append(N)
            y_coords.append(0)

        else:
            #math.comb(n, k)
            prob = 0
            for i in range(6, N):
                prob += math.comb(N, i)*pow(0.2, i)*pow(0.8, N - i)

            x_coords.append(N)
            y_coords.append(prob)

    print("x coords: " + str(x_coords))
    print("y coords: " + str(y_coords))

    plt.scatter(x_coords, y_coords)
    plt.show()
    #plot as a function of n, not a range inside N



main()
