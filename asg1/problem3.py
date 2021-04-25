import matplotlib.pyplot as plt
import math


def main():

    M = 0
    N = 20
    p = 0.2
    #math.comb(n, k)
    prob = 0
    i = 1

    while prob < 0.1:
        prob += math.comb(N, i)*pow(p, i)*pow(1 - p, N - i)
        i += 1
        print("prob is now: " + str(prob))

    print("min users to calculate congestion: " + str(i))
    #plot as a function of n, not a range inside N

    M = (i - 1)*(200000)

    print("M is: " + str(M) + " bits per second")

main()
