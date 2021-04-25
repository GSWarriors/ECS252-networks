import math
import matplotlib.pyplot as plt


def main():

    #24 circuits (m)
    #k is summated
    #lambda/mu is listed, is x variable


    #plot call blocked prob as function of lambda, so traffic_flow_list*(1/180)


    traffic_flow_list = [0.1, 0.2, 0.8, 1.6, 3.2, 6.4, 12.8, 25.6, 51.2, 102.4, 204.8]
    mu = 1/180
    lbda = [val*mu for val in traffic_flow_list]


    call_blocked_prob = []
    m = 24

    for i in range(0, len(traffic_flow_list)):

        curr_traffic_flow = traffic_flow_list[i]

        numerator = pow(curr_traffic_flow, m)*(1/math.factorial(m))
        denominator = 0

        for k in range(0, m + 1):
            denominator += pow(curr_traffic_flow, k)*(1/math.factorial(k))

        call_blocked_prob.append(numerator/denominator)

    print("lambda is: " + str(lbda))
    print()
    print("call blocked probability is: " + str(call_blocked_prob))

    plt.plot(lbda, call_blocked_prob)
    plt.xlabel("Arrival rate (lambda)")
    plt.ylabel("Call blocked probability")
    plt.show()


main()
