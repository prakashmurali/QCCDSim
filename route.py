import networkx as nx
from sorted_collection import SortedCollection
from operator import itemgetter
import numpy as np
from utils import *
from machine_state import MachineState
from machine import Trap, Segment, Junction

class BasicRoute:
    def __init__(self, machine):
        self.machine = machine

    def find_route(self, source_trap, dest_trap):
        graph = self.machine.graph
        tsrc = self.machine.traps[source_trap]
        tdest = self.machine.traps[dest_trap]
        path = nx.shortest_path(graph, source=tsrc, target=tdest)
        return path

class FreeTrapRoute:
    def __init__(self, machine, sys_state):
        self.machine = machine
        self.ss = sys_state

    def find_route(self, source_trap, dest_trap):
        #print("Check route:", source_trap, dest_trap)
        m = self.machine
        ss = self.ss
        edge_states = {}
        trap_free_space = {}
        for k in self.ss.trap_ions:
            trap_free_space[k] = m.traps[k].capacity - len(ss.trap_ions[k])
        for u, v in m.graph.edges:
            if type(u) == Trap and type(v) == Junction:
                e0 = u
                e1 = v
            elif type(u) == Junction and type(v) == Trap:
                e0 = v
                e1 = u
            elif type(u) == Junction and type(v) == Junction:
                #TODO: set zero weight
                edge_states[(u, v)] = 0
                edge_states[(v, u)] = 0
                continue

            if trap_free_space[e0.id] == 0 and e0.id != source_trap:
                edge_states[(e0, e1)] = 10**9
                edge_states[(e1, e0)] = 10**9
            else:
                edge_states[(e0, e1)] = 0
                edge_states[(e1, e0)] = 0

        nx.set_edge_attributes(m.graph, edge_states, 'block_status')
        ret = nx.shortest_path(m.graph, source=m.traps[source_trap], target=m.traps[dest_trap], weight='block_status')
        cost = 0
        for i in range(len(ret)-1):
            u = ret[i]
            v = ret[i+1]
            if (u,v) in edge_states:
                cost += edge_states[(u, v)]
            elif (v,u) in edge_states:
                cost += edge_states[(v, u)]
        if cost > 1:
            '''
            for item in edge_states:
                u = item[0]
                v = item[1]
                if type(u) == Trap and type(v) == Junction:
                    print("T"+str(u.id), "J"+str(v.id), edge_states[item])
                elif type(u) == Junction and type(v) == Trap:
                    print("T"+str(v.id), "J"+str(u.id), edge_states[item])
                elif type(u) == Junction and type(v) == Junction:
                    print("J"+str(u.id), "J"+str(v.id), edge_states[item])
                else:
                    print(item)
            print("")
            '''
            return 1, ret
        else:
            return 0, ret

class RouteAlgorithm:
    def __init__(self, machine):
        self.machine = machine
        self.setup_routing()

    def create_routing_graph(self):
        machine_obj = self.machine
        routing_graph = self.routing_graph
        for t in machine_obj.traps:
            routing_graph.add_node(trap_name(t.id))
        for s in machine_obj.segments:
            routing_graph.add_node(seg_name(s.id))
        for t in machine_obj.traps:
            if t.end1_segment != None:
                routing_graph.add_edge(trap_name(t.id), seg_name(t.end1_segment))
            if t.end2_segment != None:
                routing_graph.add_edge(trap_name(t.id), seg_name(t.end2_segment))
        for s in machine_obj.segments:
            for s2 in s.seg_edges:
                routing_graph.add_edge(seg_name(s.id), seg_name(s2))

    def add_routing_graph_weights(self):
        machine_obj = self.machine
        routing_graph = self.routing_graph
        for t in machine_obj.traps:
            if t.end1_segment != None:
                my_weight = (machine_obj.segments[t.end1_segment].length)/2
                routing_graph[trap_name(t.id)][seg_name(t.end1_segment)]['weight'] = my_weight
            if t.end2_segment != None:
                my_weight = (machine_obj.segments[t.end2_segment].length)/2
                routing_graph[trap_name(t.id)][seg_name(t.end2_segment)]['weight'] = my_weight
        for s in machine_obj.segments:
            for s2 in s.seg_edges:
                my_weight = (s.length + machine_obj.segments[s2].length)/2
                routing_graph[seg_name(s.id)][seg_name(s2)]['weight'] = my_weight

    def setup_routing(self):
        #if self.machine_state.check_ion_in_a_trap(self.ion1) == 0 or self.machine_state.check_ion_in_a_trap(self.ion2) == 0:
        #    return -1
        self.routing_graph = nx.Graph()
        self.create_routing_graph()
        self.add_routing_graph_weights()
        #source_trap = self.machine_state.find_trap_id_by_ion(self.ion1)
        #dest_trap = self.machine_state.find_trap_id_by_ion(self.ion2)

    def find_route(self, source_trap, dest_trap):
        path = nx.shortest_path(self.routing_graph, source=trap_name(source_trap), target=trap_name(dest_trap), weight='weight')
        return path
