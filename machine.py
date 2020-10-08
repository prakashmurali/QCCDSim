'''
Machine class definition
'''
import networkx as nx
import numpy as np

'''
Each trap has a capacity
PM: I believe the ions object of a trap is not currently used, I use a separate class called MachineState to track state
'''
class Trap:
    def __init__(self, idx, capacity):
        self.id = idx
        self.capacity = capacity
        self.ions = []
        self.orientation = {}

    def show(self):
        return "T"+str(self.id)

class Segment:
    def __init__(self, idx, capacity, length):
        self.id = idx
        self.capacity = capacity
        self.length = length
        self.ions = []

class Junction:
    def __init__(self, idx):
        self.id = idx
        self.objs = []

    def show(self):
        return "J"+str(self.id)

'''
Machine has a set of traps, segmenents and junctions
graph object represents the machine topology
'''

class MachineParams:
    def __init__(self):
        return

class Machine:
    def __init__(self, mparams):
        self.graph = nx.Graph()
        self.traps = []
        self.segments = []
        self.junctions = []
        self.mparams = mparams

    def add_trap(self, idx, capacity):
        new_trap = Trap(idx, capacity)
        self.traps.append(new_trap)
        self.graph.add_node(new_trap)
        return new_trap

    def add_junction(self, idx):
        new_junct = Junction(idx)
        self.junctions.append(new_junct)
        self.graph.add_node(new_junct)
        return new_junct

    def add_segment(self, idx, obj1, obj2, orientation='L'):
        new_seg = Segment(idx, 16, 10)
        self.segments.append(new_seg)
        if type(obj1) == Trap:
            obj1.orientation[new_seg.id] = orientation
            #Note: orientation is indexed by the segment object, not junction
        if type(obj1) == Junction and type(obj2) == Trap:
            print("Unsupported API: add_segment junction,trap not allowed")
            assert(0)
        self.graph.add_edge(obj1, obj2, seg=new_seg)

    def add_comm_capacity(self, val):
        for item in self.traps:
            item.capacity += val

    def print_machine_stats(self):
        trap_id = 0
        trap_capacity = self.traps[trap_id].capacity
        #max_gate_time = self.alpha*((trap_capacity*self.inter_ion_dist)**3)
        #print("cap, max_gate_time:",trap_capacity, max_gate_time)
        #print("split_time:", self.split_time(0))
        #print("move_time:", self.move_time(0, 1)) #Seg id's are currently not used

    #Gate time is computed according to the model suggested by Ken
    #gate time between two ions at distance ion-dist is alpha*ion_dist^3 +  beta
    def gate_time(self, sys_state, trap_id, ion1, ion2):
        assert ion1 != ion2
        mp = self.mparams
        p1 = sys_state.trap_ions[trap_id].index(ion1)
        p2 = sys_state.trap_ions[trap_id].index(ion2)
        d_const = 1 #um
        ion_dist = abs(p1-p2)*d_const
        #t = mp.alpha*(ion_dist**3) + mp.beta #Ken ditched this model
        if mp.gate_type == "Duan":
            t = -22 + 100*ion_dist
        elif mp.gate_type == "Trout":
            t = 10 + 38*ion_dist
        elif mp.gate_type == "FM":
            trap_capacity = self.traps[0].capacity
            t = max(100, 13.33*trap_capacity-54)
        elif mp.gate_type == "PM":
            t = 160 + 5*ion_dist
        else:
            assert 0
        t = max(t, 1)
        return int(t)

    def split_time(self, sys_state, trap_id, seg_id, ion1):
        t = self.traps[trap_id]
        split_estimate = 0
        split_swap_count = 0
        ion_swap_hops = 0
        split_swap_hops = 0
        i1 = 0
        i2 = 0
        if t.orientation[seg_id] == 'L':
            ion2 = sys_state.trap_ions[trap_id][0] #Swap to left end
        else:
            ion2 = sys_state.trap_ions[trap_id][-1] #Swap to right end
        if ion1 == ion2:
            split_estimate = self.mparams.split_merge_time
            split_swap_count = 0
            split_swap_hops = 0
        else:
            mp = self.mparams
            if mp.swap_type == "GateSwap":
                swap_est = 3*self.gate_time(sys_state, trap_id, ion1, ion2)
                split_estimate = swap_est + self.mparams.split_merge_time
                p1 = sys_state.trap_ions[trap_id].index(ion1)
                p2 = sys_state.trap_ions[trap_id].index(ion2)
                split_swap_count = 1
                split_swap_hops = abs(p1-p2)
                i1 = ion1
                i2 = ion2
            elif mp.swap_type == "IonSwap":
                p1 = sys_state.trap_ions[trap_id].index(ion1)
                p2 = sys_state.trap_ions[trap_id].index(ion2)
                num_hops = abs(p1-p2)
                swap_est = num_hops*self.mparams.split_merge_time #n splits
                swap_est += (num_hops-1)*self.mparams.split_merge_time #n-1 merges
                swap_est += self.mparams.ion_swap_time*num_hops #n moves
                split_estimate = swap_est
                ion_swap_hops = num_hops
        #print("SWAP", trap_id, seg_id, sys_state.trap_ions[trap_id], ion1, ion2, t.orientation, swap_est)
        return int(split_estimate), split_swap_count, split_swap_hops, i1, i2, ion_swap_hops

    def merge_time(self, trap_id):
        return int(self.mparams.split_merge_time)

    def move_time(self, seg1, seg2):
        return int(self.mparams.shuttle_time)

    def junction_cross_time(self, junct):
        #find junction type
        deg = self.graph.degree(junct)
        if deg == 2:
            return self.mparams.junction2_cross_time
        elif deg == 3:
            return self.mparams.junction3_cross_time
        elif deg == 4:
            return self.mparams.junction4_cross_time
        else:
            print("Junction degree", deg, " not supported.")
            assert 0
        return 0
