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

def saveToFile(path, filename = 'spanning.csv'):
    with open(filename, "w") as f:
        for p in path:
            f.write("%d\n" % p)

##################################################
# TSP Utils
#

def spanning(table, edges, nodes):
    edges.sort(key = lambda node: node[2]) # sort by distance
    vertice = [{
        "group": -1,
        "id": i,
        "neighbors": []
    } for i in range(len(nodes.keys()) + 1)]
    nEst = 0
    groupIdToAssign = 0

    # from the shortest
    for edge in edges:
        x, y, dist = edge

        vx = vertice[x]
        vy = vertice[y]

        # node is already connected
        if len(vx["neighbors"]) == 2 or len(vy["neighbors"]) == 2:
            continue
        # nodes are same group; it makes cycle
        if vx["group"] == vy["group"] and vx["group"] != -1:
            continue
        
        vx["neighbors"].append(y)
        vy["neighbors"].append(x)

        # group rearranging
        if vx["group"] == vy["group"]:    # only if group == -1
            vx["group"] = groupIdToAssign
            vy["group"] = groupIdToAssign
            groupIdToAssign += 1
        elif vx["group"] == -1: # only vx is solo
            vx["group"] = vy["group"]
        elif vy["group"] == -1:
            vy["group"] = vx["group"]
        else:   # both nodes has own group
            xg = vx["group"]
            yg = vy["group"]
            for vertex in vertice:
                if vertex["group"] == yg:
                    vertex["group"] = xg
        
        nEst += 1
        if nEst == len(nodes.keys()):
            break

    single = []
    for vertex in vertice:
        if len(vertex["neighbors"]) < 2 and vertex["id"] != 0:
            single.append(vertex["id"])

    vertice[single[0]]["neighbors"].append(single[1])
    vertice[single[1]]["neighbors"].append(single[0])
    
    result = [1]
    while len(result) < len(nodes.keys()):
        current = result[-1]
        neighbors = vertice[current]["neighbors"]
        if neighbors[0] in result:
            result.append(neighbors[1])
        else:
            result.append(neighbors[0])
    
    return result

##################################################
# Main
#

def solve(nodes):
    print("start!")
    table, edges = distanceOfEdges(nodes)
    print("distance calculation done!")
    return spanning(table, edges, nodes)

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