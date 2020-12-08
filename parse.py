'''
Parser for an extremely simplified version of OpenQASM
Extracts only two-qubit gates
Creates two objects:
    cx_graph: a network graph which has two qubit gates as nodes and edges denote among between the gates
              each cx gate in the program has a unique id (tracked using global_gate_id)
    cx_gate_map: gate id of a cx gate -> [ctrl_qubit, target_qubit]
'''

import sys
import networkx as nx

gset1 = ['x', 'y', 'z', 'h', 's', 'sdg', 't', 'tdg', 'measure']
gset2 = ['rx', 'ry', 'rz']
gset3 = ['cx']

class InputParse:
    def __init__(self):
        self.cx_graph = nx.Graph()
        self.cx_graph.graph['edge_weight_attr'] = 'weight'
        self.cx_graph.graph['node_weight_attr'] = 'node_weight'
        self.edge_weights = {}
        self.prev_gate = {}
        self.global_gate_id = 0
        self.cx_gate_map = {}
        self.gate_graph = nx.DiGraph()
        self.gset = []
        self.gset.extend(gset1)
        self.gset.extend(gset2)
        self.gset.extend(gset3)
        self.qbit_count = 0
        # make note of every two qubit gate's global gate id
        # even so, how will the mapper know the ids of the gates it receives from
        # InputParse?
        self.two_qubit_gate_list = []
 
    def find_dep_gate(self, qbit):
        if qbit in self.prev_gate.keys():
            return [self.prev_gate[qbit]]
        else:
            return []

    def update_dep_gate(self, qbit, gate_id):
        self.prev_gate[qbit] = gate_id

    def check_valid_gate(self, line):
        flag = 0
        for g in self.gset:
            if line.startswith(g):
                flag = 1
                break
        return flag

    def add_edge_pair(self, q1, q2):
        c = min(q1, q2)
        t = max(q1, q2)
        if not c in self.edge_weights.keys():
            self.edge_weights[c] = {}
        if not t in self.edge_weights[c].keys():
            self.edge_weights[c][t] = 0
        self.edge_weights[c][t] += 1
        self.cx_graph.add_edge(c, t)
        self.cx_graph.adj[c][t]['weight'] = self.edge_weights[c][t]
        self.cx_graph.nodes[c]['node_weight'] = 1
        self.cx_graph.nodes[t]['node_weight'] = 1

    def process_gate(self, line):
        for g in gset1:
            if line.startswith(g):
                qbit = int(line.split('[')[1].split(']')[0])
                if not self.check_valid_qbit(qbit):
                    sys.exit("qbit " + str(qbit) + " not in range")

                dep_gates = self.find_dep_gate(qbit)
                self.update_dep_gate(qbit, self.global_gate_id)
                for dgate in dep_gates:
                    print("qbit " + str(qbit) + " dep gates: " + str(dgate))
                    self.gate_graph.add_edge(dgate, self.global_gate_id)
                self.global_gate_id += 1
        for g in gset2:
            if line.startswith(g):
                qbit = int(line.split('[')[1].split(']')[0])
                if not self.check_valid_qbit(qbit):
                    sys.exit("qbit " + str(qbit) + " not in range")
                # theta = float(line.split('(')[1].split(')')[0])

                dep_gates = self.find_dep_gate(qbit)
                self.update_dep_gate(qbit, self.global_gate_id)
                for dgate in dep_gates:
                    print("qbit " + str(qbit) + " dep gates: " + str(dgate))
                    self.gate_graph.add_edge(dgate, self.global_gate_id)
                self.global_gate_id += 1
        for g in gset3:
             if line.startswith(g):
                base = ''.join(line.split()).split(',')
                qbit1 = int(base[0].split('[')[1].split(']')[0])
                qbit2 = int(base[1].split('[')[1].split(']')[0])
                self.add_edge_pair(qbit1, qbit2)
                dep_gates1 = self.find_dep_gate(qbit1)
                dep_gates2 = self.find_dep_gate(qbit2)
                dep_gates1.extend(dep_gates2)
                self.update_dep_gate(qbit1, self.global_gate_id)
                self.update_dep_gate(qbit2, self.global_gate_id)
                self.cx_gate_map[self.global_gate_id] = [qbit1, qbit2]
                for dgate in dep_gates1:
                    print("qbit 1: " + str(qbit1) + " qbit 2: " + str(qbit2) + " dep gates: " + str(dgate))
                    self.gate_graph.add_edge(dgate, self.global_gate_id)
                self.global_gate_id += 1
         
    def parse_ir(self, fname):
        f = open(fname, 'r')
        l = f.readlines()
        for line in l:
            line = ' '.join(line.split())
            if line.startswith("OPENQASM"):
                continue
            elif line.startswith("include"):
                continue
            elif line.startswith("qreg"):
                self.qbit_count = int(line.split('[')[1].split(']')[0])
            elif line.startswith("creg"):
                continue
            else:
                if self.check_valid_gate(line):
                    self.process_gate(line)
    
    def print_gates(self):
        for edge in self.gate_graph.edges:
            print(edge)

    def get_ir(self):
        return self.cx_gate_map, self.gate_graph

    def visualize_graph(self, fname):
        nx.write_gexf(self.cx_graph, fname)

    def check_valid_qbit(self, qbit):
        return qbit >= 0 and qbit < self.qbit_count
