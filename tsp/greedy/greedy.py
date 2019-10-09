# tsp.py
# - TSP solver
#
# Writtenn by Juan Lee (juanlee@kaist.ac.kr)

import sys, time

##################################################
# Node Utilities
#

# node structure
# id: {id, x, y}
def distanceBtw(f, t):
    return ((f['x'] - t['x'])**2 + (f['y'] - t['y'])**2)**0.5

# path structure
# [p1, p2, ..., pn]
def distance(path, nodes):
    dist = 0
    for idx in range(len(path)):
        cur = path[idx]
        nxt = path[(idx+1) % len(path)]

        dist += distanceBtw(nodes[cur], nodes[nxt])
    return dist

def distanceOfEdges(nodes):
    dists = {}
    asList = []
    keys = list(nodes.keys())
    for i in range(len(keys)):
        ki = keys[i]
        dists[(ki, ki)] = 0
        for j in range(i+1, len(keys)):
            kj = keys[j]
            d = distanceBtw(nodes[ki], nodes[kj])
            dists[(ki, kj)] = d
            dists[(kj, ki)] = d

            asList.append((ki, kj, d))
    return dists, asList

def saveDistance(filename, distanceTable, dimension):
    with open(filename, 'w') as f:
        for i in range(dimension):
            for j in range(dimension):
                f.write(str(distanceTable[(i+1, j+1)]) + ", ")
            f.write("\n")

def loadDistance(filename, dimension):
    distanceTable = {}
    with open(filename, 'r') as f:
        for i in range(dimension):
            line = f.readline().strip().split(",")
            distanceTable[(i, i)] = 0
            for j in range(i+1, dimension):
                dist = float(line[j])
                distanceTable[(i+1, j+1)] = dist
                distanceTable[(j+1, i+1)] = dist
    return distanceTable

##################################################
# File Utilities
#

def loadFromFile(filename):
    nodes = {}
    with open(filename, 'r') as f:
        lines = f.readlines()
        lines = list(map(lambda x:x.strip(), lines))

        s = lines.index("NODE_COORD_SECTION")
        e = lines.index("EOF")
        parsed = lines[s+1: e]
        parsed = list(map(lambda x: tuple(map(lambda y: float(y), x.split())), parsed))
    
    for node in parsed:
        nodes[int(node[0])] = {
            "id": int(node[0]),
            "x": node[1],
            "y": node[2]
        }
    
    return nodes

def saveToFile(path, filename = 'greedy.csv'):
    with open(filename, "w") as f:
        for p in path:
            f.write("%d\n" % p)

##################################################
# TSP Utils
#
def greedy_from(n, nodes):
    # 51, 1111492.9231858053 # 1 to 62
    path = [n]
    toVisit = list(nodes.keys())
    toVisit.remove(n)
    while len(toVisit) > 0:
        m = 999999999
        mIdx = -1
        for target in toVisit:
            dist = distanceBtw(nodes[target], nodes[path[-1]])
            if dist < m:
                m = dist
                mIdx = target
        
        toVisit.remove(mIdx)
        path.append(mIdx)
    return path

##################################################
# Main
#

def solve(nodes):
    return greedy_from(random.randint(1, len(nodes)), nodes)

def main():
    tsp_file = sys.argv[1]
    nodes = loadFromFile(tsp_file)
    path = solve(nodes)
    dist = distance(path, nodes)
    
    saveToFile(path)

    print(dist)

if __name__ == '__main__':
    main()


####