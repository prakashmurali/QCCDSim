import networkx as nx
import numpy as np
from machine_state import MachineState
from utils import *
from route import *
from schedule import *
from machine import Trap, Segment, Junction

class RebalanceTraps:
    def __init__(self, machine, system_state):
        self.machine = machine
        self.ss = system_state
   
    def clear_all_blocks(self):
        m = self.machine
        graph = nx.DiGraph(m.graph)
        demand = {}
        weight = {}
        capacity = {}
        ss = self.ss
        trap_free_space = {}
        for k in self.ss.trap_ions:
            trap_free_space[k] = m.traps[k].capacity - len(ss.trap_ions[k])
        req_free_space = 0
        for k in self.ss.trap_ions:
            #If a trap is blocked, remove one ion from it
            if trap_free_space[k] == 0:
                req_free_space += 1
                demand[m.traps[k]] = -1
        for k in self.ss.trap_ions:
            #If ions need to be moved, and this ion has 2 or more spaces, accepts ions
            if req_free_space != 0 and trap_free_space[k] > 1:
                offer = min(trap_free_space[k]-1, req_free_space)
                req_free_space -= offer
                demand[m.traps[k]] = offer #This trap accepts ions
        #print("Demands")
        #for item in demand:
        #    print("T"+str(item.id), demand[item])
        nx.set_node_attributes(graph, demand, 'demand')
        for u, v in graph.edges:
            weight[(u,v)] = 1
            capacity[(u,v)] = 100
        nx.set_edge_attributes(graph, weight, 'weight')
        nx.set_edge_attributes(graph, capacity, 'capacity')

        flowCost, flowDict = nx.network_simplex(graph) 
        return flowDict

    def clear_route(self, trap_list, route):
        #Set up node demands
        #Negative demand means node wants to send flow 
        #heuristic: For each blocked node on a path from i1 to i2, create negative demand
        #for free nodes outside this path if available, create positive demand
        assert 0 

