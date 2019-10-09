# tsp.py
#
# written by Juan Lee <juanlee@kaist.ac.kr>

import sys, random

############################################################
# CONSTANTS
#

CROSSOVER_STRATEGY = "cx" # my | cx | <else - no crossover> (default)
SELECTION_STRATEGY = "elitism" # overselect (default) | elitism

GENE_MAX_LENGTH = 100
GENE_MUTATE_RATE = 0.2

INITIALIZE_SAME_AS_EXISTING_RATE = 0.1
INITIALIZE_MUTATE_ONCE_FROM_EXISTING_RATE = 0.2

GENERATION = 10000
POPULATION_SIZE = 150

OVERSELECT_RATE = 0.2
ELITISM_RATE = 0.2


############################################################

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

# createRandom: nodes -> random path
def createRandom(nodes):
    ids = list(map(lambda node: node[0], nodes))
    random.shuffle(ids)
    return ids

# getDistance: nodes, path -> distance
def getDistance(nodes, path):
    total = 0
    for idx in range(len(path)):
        n1 = nodes[path[idx] - 1]
        n2 = nodes[path[(idx+1) % len(path)] - 1]

        total += ((n1[1] - n2[1])**2 + (n1[2] - n2[2])**2)**0.5
    return total

# mutate: path, r -> path
# - mutate if p < r
def mutate(path, r):
    if random.random() < r:
        id1 = random.choice(path)
        id2 = random.choice(path)
        while id2 == id1:
            id2 = random.choice(path)
        
        idx1 = path.index(id1)
        idx2 = path.index(id2)
        path[idx1], path[idx2] = path[idx2], path[idx1]
    return path

# myCrossOver: path, path -> two paths
# - cross over two paths and create one
# - because of the criterion of TSP, what I do is:
#   1. select some part from first gene starting from random position with random length (<100)
#   2. exchange genes from second gene without touchinng any unselected gene in step 1
#   3. in step 2, the changed genes' order should be preserved
# - this assumes similar position of genes might represent path's property
def myCrossOver(p1, p2):
    s = random.randint(0, len(p1)-1)
    e = random.randint(s, s + GENE_MAX_LENGTH)
    e = min(e, len(p1) - 1)
    np1 = p1[:]
    np2 = p2[:]
    exchangePart = p1[s:e+1]
    
    idx1 = s
    idx2 = 0
    while idx1 < e + 1:
        if np2[idx2] in exchangePart:
            np1[idx1], np2[idx2] = np2[idx2], np1[idx1]
            idx1 += 1
        idx2 += 1
    return (np1, np2)

# cxCrossOver: path, path -> two paths
# - cross over using cycle crossover algorithm
def cxCrossOver(x1, x2):
    y1 = [-1] * len(x1)
    y2 = [-1] * len(x2)

    y1[0] = x1[0]
    y2[0] = x2[0]
    i = 0

    # do once first
    while x2[i] not in y1:
        j = x1.index(x2[i])
        y1[j] = x1[j]
        y2[j] = x2[j]
        i = j

    for i in range(len(y1)):
        if y1[i] == -1:
            y1[i] = x2[i]
            y2[i] = x1[i]

    return (y1, y2)

# crossOver
def crossOver(p1, p2):
    if CROSSOVER_STRATEGY == "my":
        return myCrossOver(p1, p2)
    elif CROSSOVER_STRATEGY == "cx":
        return cxCrossOver(p1, p2)
    return (p1, p2)

# overselect: nodes, population, r -> population, dist, path
# - top r make new (1-r) and other (1-r) make r
def overselect(nodes, population):
    population.sort(key = lambda path: getDistance(nodes, path))
    nTop = int(len(population) * OVERSELECT_RATE)
    nBottom = len(population) - nTop
    top = population[:nTop]
    bottom = population[nTop:]

    mDist = 99999999999999999999
    mPath = None

    newpopulation = []
    while len(newpopulation) < nBottom:
        rp1 = random.choice(top)
        rp2 = random.choice(top)
        np1, np2 = crossOver(rp1, rp2)
        np1 = mutate(np1, GENE_MUTATE_RATE)
        np2 = mutate(np2, GENE_MUTATE_RATE)
        newpopulation += [np1, np2]

        dist1 = getDistance(nodes, np1)
        dist2 = getDistance(nodes, np2)
        if dist1 < mDist:
            mDist = dist1
            mPath = np1
        if dist2 < mDist:
            mDist = dist2
            mPath = np2
    while len(newpopulation) < nTop + nBottom:
        rp1 = random.choice(bottom)
        rp2 = random.choice(bottom)
        np1, np2 = crossOver(rp1, rp2)
        np1 = mutate(np1, GENE_MUTATE_RATE)
        np2 = mutate(np2, GENE_MUTATE_RATE)
        newpopulation += [np1, np2]

        dist1 = getDistance(nodes, np1)
        dist2 = getDistance(nodes, np2)
        if dist1 < mDist:
            mDist = dist1
            mPath = np1
        if dist2 < mDist:
            mDist = dist2
            mPath = np2

    return newpopulation, mDist, mPath

# elitism
# - remains top R% elites
def elitism(nodes, population):
    population.sort(key = lambda path: getDistance(nodes, path))
    nTop = int(len(population) * ELITISM_RATE)
    top = population[:nTop]

    newpopulation = []
    mDist = 99999999999999999999
    mPath = None

    for elite in top:
        newpopulation.append(elite[:])

        dist = getDistance(nodes, elite)
        if dist < mDist:
            mDist = dist
            mPath = elite[:]
    while len(newpopulation) < POPULATION_SIZE:
        rp1 = random.choice(top)
        rp2 = random.choice(top)
        np1, np2 = crossOver(rp1, rp2)
        np1 = mutate(np1, GENE_MUTATE_RATE)
        np2 = mutate(np2, GENE_MUTATE_RATE)
        newpopulation += [np1, np2]

        dist1 = getDistance(nodes, np1)
        dist2 = getDistance(nodes, np2)
        if dist1 < mDist:
            mDist = dist1
            mPath = np1
        if dist2 < mDist:
            mDist = dist2
            mPath = np2
    
    return newpopulation, mDist, mPath

# select
def select(nodes, population):
    if SELECTION_STRATEGY == "elitism":
        return elitism(nodes, population)
    return overselect(nodes, population, OVERSELECT_RATE)

# selectFromPopulation: nodes, paths, n -> paths
# - select n top paths from population
def selectFromPopulation(nodes, paths, n):
    paths.sort(key = lambda path: getDistance(nodes, path))
    n = min(n, len(paths))
    return paths[:n]

# saveToFile
def saveToFile(filename, path):
    with open(filename, 'w') as f:
        path = map(lambda s:str(s), path)
        f.write("\n".join(path))

# initializeFromExisting: filename, nodes, size -> population
# - existing 10%
# - mutated 20%
# - random 70%
def initializeFromExisting(filename, nodes, n):  
    with open(filename, 'r') as f:
        path = f.readlines()
        path = list(map(lambda x: int(x.strip()), path))
    
    population = []
    while len(population) < n * INITIALIZE_SAME_AS_EXISTING_RATE:
        population.append(path[:])
    while len(population) < n * (INITIALIZE_SAME_AS_EXISTING_RATE + INITIALIZE_MUTATE_ONCE_FROM_EXISTING_RATE):
        population.append(mutate(path, 1))
    while len(population) < n:
        population.append(createRandom(nodes))
    return population

# initializeWithRandom
def initializeWithRandom(nodes, n):
    population = []
    for i in range(n):
        population.append(createRandom(nodes))
    return population

# Genetic Algorithm Main
def ga():
    nodes = parse(sys.argv[1])

    # initialize
    population = initializeFromExisting("ga.csv", nodes, POPULATION_SIZE)

    # generations
    m = 99999999999999
    for i in range(GENERATION):
        population, mDist, mPath = select(nodes, population)

        if m > mDist:
            m = mDist
            print("- [%s] %f" % (str(i).zfill(6), mDist))
            saveToFile("ga.csv", mPath)
        elif m < mDist:
            print("+", end="", flush=True)
        else:
            print(".", end="", flush=True)

if __name__ == '__main__':
    ga()