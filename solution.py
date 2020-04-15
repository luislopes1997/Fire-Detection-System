import probability
import sys
from itertools import product


class Problem:

    def __init__(self, fh):
        "Loads problem from opened file object fh and creates a Bayesian Network"

        self.R = []                         # Rooms
        self.C = {}                         # Connections
        self.S = {}                         # Sensors
        self.P = float()                    # Propagation Probability
        self.M = {}                         # Measurements
        self.RoomProbs = {}                 # Probability of fire in each room
        self.NB = probability.BayesNet()    # Bayesian Network
        self.load(fh)                       # load data from input file
        self.createBayes()                  # create Bayesian Network

    def load(self, fh):
        "Loads problem from opened file object fh"

        time = 0
        aux_C = []
        for ln in fh.readlines():
            # Room
            if ln[0] == 'R':
                self.R = ln[1:].split()
            # Connections
            if ln[0] == 'C':
                aux_C = ln[1:].split()
            # Sensors
            if ln[0] == 'S':
                aux = ln[1:].split()
                for i in aux:
                    aux2 = i.split(':')
                    aux2[2] = float(aux2[2])
                    aux2[3] = float(aux2[3])
                    self.S[aux2[0]] = aux2[1:]
            # Propagation Prob
            if ln[0] == 'P':
                self.P = float(ln[1:].split()[0])
            # Measurements
            if ln[0] == 'M':
                time += 1
                aux = ln[1:].split()
                self.M[time] = {}
                for i in aux:
                    aux2 = i.split(':')
                    self.M[time][aux2[0]] = aux2[1]

        # Construct dictionary of connections
        for room in self.R:
            self.C[room] = []
        for connect in aux_C:
            aux = connect.split(',')
            self.C[aux[0]].append(aux[1])
            self.C[aux[1]].append(aux[0])

        ####################################################################
        print('ROOM')
        print(self.R)
        print('CONNECTIONS')
        print(self.C)
        print('SENSORS')
        print(self.S)
        print('PROPAGATION')
        print(self.P)
        print('MEASUREMENT')
        print(self.M)
        print('-------------------------------------------')
        ####################################################################

    def createBayes(self):
        " "

        # Analise each time instant
        for inst in range(1, len(self.M)+1):
            # ROOMS
            for room in self.R:
                actual_room = room + '_' + str(inst)
                if inst == 1:
                    # initial probability unknown
                    self.NB.add([actual_room, '', 0.5])
                else:
                    # probabilities affected by propagations
                    before_room = room + '_' + str(inst-1)
                    parent = self.C[room]
                    nb_parents = 1
                    for x in parent:
                        before_room = before_room + ' ' + x + '_' + str(inst-1)
                        nb_parents += 1
                    print('----------')
                    print(actual_room)
                    print(before_room)
                    print(self.create_Probs(nb_parents, actual_room))
                    self.NB.add([actual_room, before_room,
                                 self.create_Probs(nb_parents, actual_room)])

                print(self.NB.variable_node(actual_room))
            # SENSORS
            for measure in self.M[inst]:
                actual_sensor = measure + '_' + str(inst)
                actual_room = self.S[measure][0] + '_' + str(inst)
                self.NB.add([actual_sensor, actual_room,
                             self.create_Probs(1, measure)])

                print('----------')
                print(self.create_Probs(1, measure))
                print(self.NB.variable_node(actual_sensor))

        # print(self.RoomProbs)
        # solution_room = max(self.RoomProbs, key=self.RoomProbs.get)
        # solution = [solution_room, self.RoomProbs[solution_room]]
        # return  tuple(solution)

    def create_Probs(self, nb_parents, room):
        " "

        # Only parent are the same room in the previous time instant, or its a sensor
        if nb_parents == 1:
            # it's a room
            if room[0] == 'R':
                return {True: 1, False: 0}
            # it's a sensor
            elif room[0] == 'S':
                tpr = self.S[room][1]
                fpr = self.S[room][2]
                return {True: tpr, False: fpr}
        # Parents are the same room and other roomas (notation is different)
        else:
            cpt = {}
            combinations = list(product([True, False], repeat=nb_parents))
            for i in range(int(len(combinations)/2.0)):
                cpt[combinations[i]] = 1
            for i in range(int(len(combinations)/2.0), len(combinations)-1):
                cpt[combinations[i]] = self.P
            cpt[combinations[-1]] = 0
            return cpt

    def solve(self):
        " "
        print('-------------------------------------------')
        print(self.NB)
        print('--- SOLVE ---')

        m = {}
        T, F = True, False
        for time in self.M:
            sensor = self.M[time].keys()
            for names in sensor:
                state = self.M[time][names]
                j = names + '_' + str(time)
                if state == 'T':
                    m[j] = True
                else:
                    m[j] = False

        for room in self.R:
            actual_room = room + '_' + str(len(self.M))
            print(actual_room)
            print(m)
            probs = probability.elimination_ask(actual_room, m, self.NB).show_approx('{:}')
            t = float(probs.split(',')[1].split(': ')[1])
            self.RoomProbs[room] = t

        solution_room = max(self.RoomProbs, key=self.RoomProbs.get)
        solution = [solution_room, self.RoomProbs[solution_room]]
        return tuple(solution)


def solver(input_file):
    " "
    return Problem(input_file).solve()


### MAIN ###


def main():
    ""

    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], "r") as f:
                solution = solver(f)
                print(solution)

        except IOError:
            print("IO error")
    else:
        print("Usage:", sys.argv[0], "<filename>")


main()
