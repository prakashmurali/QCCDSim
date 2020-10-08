'''
This class is used to represent a snapshot of machine state and manipulate that state
Machine state at a given point is
which qubits are sitting in which traps --> self.trap_ions
which qubits are sitting in which segments --> self.seg_ions
'''
from utils import *

class MachineState:
    def __init__(self, ts, trap_ions, seg_ions):
        self.ts = ts #timestamp
        self.trap_ions = trap_ions
        self.seg_ions = seg_ions

    #Given a trap and a connected segment, and a set of ions in this trap,
    #remove ions from the trap and add it to the segment
    #analogous operations in merge and move
    def process_split(self, trap, seg, ions):
        if not seg in self.seg_ions:
            self.seg_ions[seg] = []
        for ion in ions:
            self.trap_ions[trap].remove(ion)
            self.seg_ions[seg].append(ion)

    def process_merge(self, trap, seg, ions):
        if not trap in self.trap_ions:
            self.trap_ions[trap] = []
        for ion in ions:
            self.trap_ions[trap].append(ion)
            self.seg_ions[seg].remove(ion)

    def process_move(self, seg1, seg2, ions):
        if not seg2 in self.seg_ions:
            self.seg_ions[seg2] = []
        for ion in ions:
            self.seg_ions[seg1].remove(ion)
            self.seg_ions[seg2].append(ion)

    def find_trap_id_by_ion(self, ion_id):
        for trap_id in self.trap_ions.keys():
            if ion_id in self.trap_ions[trap_id]:
                return trap_id
        return -1

    def check_ion_in_a_trap(self, ion_id):
        if self.find_trap_id_by_ion(ion_id) != -1:
            return 1
        else:
            return 0

    def print_state(self):
        print("Machine State")
        for t in self.trap_ions.keys():
            print(trap_name(t), len(self.trap_ions[t]), self.trap_ions[t])
        #for s in self.seg_ions.keys():
        #    print(seg_name(s), len(self.seg_ions[s]), self.seg_ions[s])
