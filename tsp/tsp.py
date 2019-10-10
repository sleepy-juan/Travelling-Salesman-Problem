import sys

from aco import aco
from ga import ga
from greedy import greedy
from mst import mst

def parseArguments():
    args = {}
    args["tspfile"] = sys.argv[1]
    idx = 2
    while idx < len(sys.argv):
        if sys.argv[idx] == "-h" or sys.argv[idx] == "-l":
            args[sys.argv[idx]] = True
            idx += 1
        else:
            args[sys.argv[idx]] = sys.argv[idx+1]
            idx += 2
    return args

def printHelp():
    # \033[32m green light
    # \x1b[1;49;32m green bold
    # \033[33m yellow light
    # \x1b[1;49;33m yellow
    # \x1b[0m default

    print('''\x1b[1;49;32mTraveling Salesman Problem Solver
Coursework#2, CS454, AI-based SE, KAIST
Written by Juan Lee <juanlee@kaist.ac.kr>\x1b[0m

\x1b[1;49;33mUsage of TSP sovler\x1b[0m
$ python3 tsp.py tspfile.tsp

\x1b[1;49;33m===== Flags =====\x1b[0m
\033[33m> General Flags\x1b[0m
-a alg: choose algorithm. alg is one of aco, ga, greedy, or mst. greedy is default.
-h: show help
-l: print log

\033[33m> Ant Colony Optimization\x1b[0m
-p size: the number of ants. 10 is default.
-w weight: pheromone weight. 0.5 is default. length weight is set (1-weight)
-f size: the number of generations. 100 is default.
-i value: initial pheromone. 1 is default
-e length: estimated shortest tour for ACO. 1000000 is default
-r rate: evaporation rate. 0.1 is default
-x strategy: examination strategy. one of tester and mst. mst is default.

\033[33m> Genetic Algorithm\x1b[0m
-p size: the size of population. 150 is default
-w rate: selection rate. 0.1 is default.
-f size: the number of generations. 100 is default.
-x value: crossover strategy. value is one of my, cx, pmx, and no. cx is default.
-s value: selection strategy. value is one of overselect and elitism. overselect is default.
-m rate: mutation rate. 0.05 is default.
-fl length: gene max length for my crossover algorithm. 100 is default.
-ie rate: ratio of maintaining best solution at initializing
-im rate: ratio of generating mutated second-best solution at initializing.

\033[33m> Greedy Algorithm\x1b[0m
-i node: initial node. randomly chosen node is default.

\x1b[1;49;33m===== Example =====\x1b[0m
This is an example of tsp solver solving rl11849.tsp using Ant Colony Optimization algorithm with one ant, almost (0.9) depending on length, and run 1000 generations. 
$ python3 tsp.py rl11849.tsp -a aco -p 1 -w 0.1 -f 1000

This is an example of tsp solver solving rl11849.tsp using Greedy Algorithm starting from node 52. (now deterministic)
$ python3 tsp.py rl11849.tsp -a greedy -i 52''')

def main():
    try:
        args = parseArguments()
    except:
        args = {"-h": True}
    
    if "-l" not in args:
        args["-l"] = False
    else:
        args["-l"] = True
    
    # handle argument
    if "-h" in args:
        printHelp()
        return

    if "-a" not in args:
        greedy(args)
        return
    
    if args["-a"] == "aco":
        aco(args)
    elif args["-a"] == "ga":
        ga(args)
    elif args["-a"] == "greedy":
        greedy(args)
    elif args["-a"] == "mst":
        mst(args)
    else:
        printHelp()

if __name__ == '__main__':
    main()