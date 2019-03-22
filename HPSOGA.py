import numpy as np
import random
from GATSPv2 import hamilton


class Node():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self, node):
        xDis = abs(self.x - node.x)
        yDis = abs(self.y - node.y)
        distance = np.sqrt((xDis ** 2) + (yDis ** 2))
        return distance

    def __repr__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"


class Sensor(Node):
    def __init__(self, x, y, p=0):
        Node.__init__(self, x, y)
        self.p = p


class Station(Node):
    def __init__(self):
        Node.__init__(self, 0, 0)


def distance(i, j):
    return np.sqrt((i.x - j.x)**2 + (i.y - j.y)**2)


T = []
Tmax = 0
n = 4
P = 0
Pm = 1  # Watt
v = 5  # m/s
Emax = 10800  # J
Emin = 540  # J
Em = 4000  # J
U = 5  # W

sensorList = [Station(), Sensor(1, 2), Sensor(3, 6),
              Sensor(4, 2), Sensor(-2, 4)]
[path, length] = hamilton(sensorList)
tau_tsp = length / v  # tau_min_tsp
tau_i_vac = []
E_min = tau_tsp * Pm  # E'm
for i in range(n):
    T.append((Emax - Emin) * (1 / U - 1 / (U - sensorList[i+1].p))) 
    if (Tmax < T[i]):
        T = T[i]
    P = P + sensorList[i+1].p

for i in range(n):
    tau_i_vac[i] = T - tau_tsp - P * T / U
    if(tau_i_vac[i] < 0):
        btn_flag = 1
        # Add si to the set of below zero vacation time nodes
        #  ni = ⌈T ∗ pi ∗ (U − pi) /U · (Emax − Emin)⌉; //compute the minimum
        #  charging number of each node;
        # Add ni to the set of charging number CN of si

if (btn_flag == 1 and Em > E_min):
    sit_flag = 1
elif (btn_flag == 0 and Em < E_min):
    sit_flag = 2
elif (btn_flag == 1 and Em < E_min):
    sit_flag = 3
