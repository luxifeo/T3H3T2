import numpy as np
import random
from GATSPv2 import hamilton

MUTATION_RATE = 0.01


def create_list(size, value):
    '''
    Utility function
    Return a list filled with value
    '''
    result = []
    for i in range(size):
        result.append(value)
    return result


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
U = 4  # W
sit_flag = 0
sensorList = [Station(), Sensor(1, 2), Sensor(3, 6),
              Sensor(4, 2), Sensor(-2, 4)]
[path, length] = hamilton(sensorList)
tau_tsp = length / v  # tau_min_tsp
tau_i_vac = []
E_min = tau_tsp * Pm  # E'm


def algorithm2():
    for i in range(1, n):
        T.append((Emax - Emin) *
                 (1 / sensorList[i].p - 1 / (U - sensorList[i].p)))
        if (Tmax < T[i]):
            Tmax = T[i]
        P = P + sensorList[i+1].p

    for i in range(n):
        tau_i_vac[i] = T[i] - tau_tsp - P * Tmax / U
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


def breed(parent1, parent2):
    q_cap = len(parent1) - \
        1 if len(parent1) > len(parent2) else len(parent2) - 1
    p = random.randint(0, q_cap)
    q = random.randint(p, q_cap)
    seg1 = parent1[p:(q+1)]
    seg2 = parent2[p:(q+1)]
    child1 = parent1[q+1:] + parent1[:p]
    for x in range(len(seg2)):
        child1.remove(seg2[x])
    child2 = parent2[p:] + parent2[:p]
    for x in range(len(seg1)):
        child2.remove(seg1[x])
    child1 = child1 + seg1 + seg2
    child2 = child2 + seg2 + seg1
    child1[:(q-p+1)] = seg2
    child2[:(q-p+1)] = seg1
    return [child1, child2]


def mutation(path, path_best, global_best):
    c = 0.3  # factor constant

    def encode(obj_path, target):
        '''
        Encode the target chromosome according to the path thats needs to be mutated.
        Because the path may contains duplicates, adjacency representation of it will
        cause unexpected errors or not able to decode properly. 
        '''
        temp = obj_path.copy()
        result = []
        for i in range(len(temp)):
            index = temp.index(target[i])
            result.append(index)
            temp[index] = -1
        return result

    def decode(obj_path, target):
        '''
        Decode the unduplicated path to the original one.
        '''
        result = []
        for i in range(len(obj_path)):
            result.append(obj_path[target[i]])
        return result

    def adjacency(path):
        '''
        Return the adjacency representation of the path.
        The path must not contain duplicate values and should be processed 
        before by encode function above
        '''
        adj_path = create_list(len(path), -1)
        for i in range(1, len(path)):
            adj_path[i - 1] = path[i]
        adj_path[path[len(path - 1)]] = path[0]
        return adj_path

    def adj_decode(path):
        '''
        Return the path representation of the adjacency represation path 
        '''
        org_path = create_list(len(path), -1)
        org_path[0] = 0  # The path starts at 0, for convenience
        for i in range(1, len(path)):
            next_city = path[next_city]
            org_path[i] = next_city
        return org_path

    def add(path, velo):
        for i in range(len(path)):
            if path[i] != velo[i] and velo[i] != 0:
                path[velo.index(velo[i])] = path[velo[i]]
                path[velo[i]] = path[i]
                path[i] = velo[i]
        return path

    def subtract(path1, path2):
        velo = []  # velo = path2 - path1
        for i in range(len(path)):
            if path1[i] == path2[i]:
                velo.append(i)
            else:
                velo.append(path2[i])
        return

    def multiply(path1, c):
        product = []
        rand = np.random.rand(len(path1))
        for i in len(rand):
            if rand(i) < c:
                product.append(path[i])
            else:
                product.append(-1)
        return

    def speed_add(velo1, velo2):
        velo = []
        for x in range(len(velo1)):
            if velo2[x] != -1:
                velo.append(velo2[x])
            else:
                velo.append(velo1[x])
        return velo

    random_roll = np.random.rand()
    if (random_roll > MUTATION_RATE):
        adj_path = adjacency(path)
        adj_p_best = adjacency(encode(path, path_best))
        adj_g_best = adjacency(encode(path, global_best))
        velo = speed_add(multiply(subtract(adj_path, adj_p_best), c),
                         multiply(subtract(adj_path, adj_g_best), c))
        adj_mutated_path = add(adj_path, velo)
        mutated_path = adj_decode(adj_mutated_path)
        if (-1 in mutated_path):
            print("Mutation creates sub-tour path, reverts mutation....")
            return path
        else:
            return decode(path, mutated_path)
    else:
        return path


def seed(size, sensor_amount, bottleneck):
    population = []
    init_path = [0] + [i for i in range(sensor_amount) + 1]
    if(sit_flag == 1 or sit_flag == 3):
        init_path.insert(random.randint(0, len(init_path)), bottleneck)
    if(sit_flag == 2 or sit_flag == 3):
        init_path.insert(random.randint(0, len(init_path)), 0)
    random.shuffle(init_path)
    while(len(population) < size):
        if(constraint_check(init_path)):
            population.insert(init_path)

    return population


def fitness(path):
    
    return


def constraint_check(path1):
    return
