# aco.py
#
# written by Juan Lee <juanlee@kaist.ac.kr>

import sys, random

##################################################
# Constants
#
INITIAL_PHEROMONE = 1

WEIGHT_PHEROMONE = 1
WEIGHT_LENGTH = 1

ESTIMATED_SHORTEST_TOUR = 3000

EVAPORATION_RATE = 0.1

ANT_NUMBER = 10
GENERATION = 10000

##################################################
# File Utilities
#

# parse: filename -> nodes
# - nodes: (int id, float x, float y)
def parse(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        lines = list(map(lambda line: line.strip(), lines))
        s = lines.index("NODE_COORD_SECTION")
        e = lines.index("EOF")
        nodes = lines[s+1: e]
        nodes = list(map(lambda node: [int(node.split()[0]), float(node.split()[1]), float(node.split()[2])], nodes))
    return nodes

# saveToFile
def saveToFile(filename, path):
    with open(filename, 'w') as f:
        path = map(lambda s:str(s), path)
        f.write("\n".join(path))

##################################################
# Anthill
#

# class Anthill
class Anthill:
    def __init__(self, nodes):
        self.nodes = nodes
        self.pheromone = {}
        self.edges = {}

        self.weightMax = 0
        self.weightMin = 9999999999

        self._init()

    def _init(self):
        self.dimension = len(self.nodes)
        for i in range(self.dimension):

            self.pheromone[(i, i)] = 0
            self.edges[(i, i)] = 0
            for j in range(i+1, self.dimension):
                dist = ((self.nodes[i][1] - self.nodes[j][1]) ** 2 + (self.nodes[i][2] - self.nodes[j][2]) ** 2) ** 0.5
                self.edges[(i, j)] = dist
                self.edges[(j, i)] = dist

                if self.weightMax < dist:
                    self.weightMax = dist
                if self.weightMin > dist:
                    self.weightMin = dist

                self.pheromone[(i, j)] = INITIAL_PHEROMONE
                self.pheromone[(j, i)] = INITIAL_PHEROMONE
    
    def tracePheromone(self, L, route):
        deposit = ESTIMATED_SHORTEST_TOUR / L
        for idx in range(self.dimension):
            idx1 = route[idx] - 1
            idx2 = route[(idx+1) % len(route)] - 1

            self.pheromone[(idx1, idx2)] += deposit
            self.pheromone[(idx2, idx1)] += deposit
    
    def evaporate(self):
        for i in range(self.dimension):
            for j in range(i+1, self.dimension):
                self.pheromone[(i, j)] *= (1 - EVAPORATION_RATE)
                self.pheromone[(j, i)] *= (1 - EVAPORATION_RATE)

##################################################
# Ant
#

# class Ant
class Ant:
    def __init__(self, anthill, name, testFlag = False):
        self.anthill = anthill
        self.name = name
        self.testFlag = testFlag
    
    def begin(self):
        self.current = random.randint(1, self.anthill.dimension)
        self.route = [self.current]

        self.endFlag = False
    
    def end(self):
        return self.endFlag
    
    def turn(self):
        if not self.endFlag:
            self.move()

            if len(self.route) == self.anthill.dimension:
                self.endFlag = True
                if not self.testFlag:
                    self.anthill.tracePheromone(self.routeDistance(self.anthill.nodes), self.route)
    
    def move(self):
        prob_divider = 0
        for i in range(1, self.anthill.dimension + 1):
            if self.current == i or i in self.route:
                continue

            if self.anthill.edges[(i-1, self.current-1)] == 0:
                self.route.append(i)
                self.current = i

                return
            
            dist = self.anthill.edges[(i-1, self.current-1)]
            eta = (self.anthill.weightMax - self.anthill.weightMin) / (dist - self.anthill.weightMin + 1)
            if self.testFlag: eta = 1
            tau = self.anthill.pheromone[(i-1, self.current-1)]

            prob_divider += (eta**WEIGHT_LENGTH) * (tau**WEIGHT_PHEROMONE)
        
        prob_list = []
        prob_index = []
        for i in range(1, self.anthill.dimension + 1):
            if self.current == i or i in self.route:
                continue
            
            dist = self.anthill.edges[(i-1, self.current-1)]
            eta = (self.anthill.weightMax - self.anthill.weightMin) / (dist - self.anthill.weightMin + 1)
            if self.testFlag: eta = 1
            tau = self.anthill.pheromone[(i-1, self.current-1)]

            prob = (eta**WEIGHT_LENGTH) * (tau**WEIGHT_PHEROMONE)
            prob_list.append(prob / prob_divider)
            prob_index.append(i)
        
        prob = random.random()

        found = -1
        for i in range(len(prob_list)):
            prob -= prob_list[i]
            if prob < 0:
                found = prob_index[i]
                break
        
        self.route.append(found)
        self.current = found
    
    def routeDistance(self, nodes):
        total = 0
        for idx in range(len(self.route)):
            n1 = nodes[self.route[idx] - 1]
            n2 = nodes[self.route[(idx+1) % len(self.route)] - 1]

            total += ((n1[1] - n2[1])**2 + (n1[2] - n2[2])**2)**0.5
        return total

# Ant Colony Optimisation Main
def aco():
    nodes = parse(sys.argv[1])

    anthill = Anthill(nodes)
    ants = [Ant(anthill, i) for i in range(ANT_NUMBER)]

    for ant in ants:
        ant.begin()
    
    for gen in range(GENERATION):
        while not ants[0].end():
            for ant in ants:
                ant.turn()
        anthill.evaporate()
        for ant in ants:
            ant.begin()
        
        tester = Ant(anthill, "tester", True) # tester
        tester.begin()
        while not tester.end():
            tester.turn()
        print("[%s]" % str(gen).zfill(6), tester.routeDistance(nodes))    

if __name__ == '__main__':
    aco()