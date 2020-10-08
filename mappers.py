'''
Generates an initial qubit mapping
Three mappers:
    QubitMapPO - Program Order based
    QubitMapMetis - Metis clustering
    QubitMapAgg - Agglomerative cluster

Metis mapping didnt work very well, use either PO or Agg mappers

Output of this step is a partitioning of the qubits into regions given by a dictionary
prog_qubit -> region id

TODO mrm suggested comparing to lpfs. Need to check if its feasible to implement the comparison
'''

import sys
import networkx as nx
#import metis as mt
import numpy as np
from sklearn.cluster import AgglomerativeClustering as AggClus
import copy
from route import BasicRoute

class QubitMapGreedy:
    def __init__(self, parse_obj, machine_obj):
        self.parse_obj = parse_obj
        self.machine_obj = machine_obj
        self.build_program_graph()
        self.pending_program_edges = []
        self.mapping = []
        self.remaining_capacity = []
        trap_capacity = self.machine_obj.traps[0].capacity
        for i in range(len(machine_obj.traps)):
            self.mapping.append([])
            self.remaining_capacity.append(trap_capacity)
        self.router = BasicRoute(machine_obj)

    def gate_tuple(self, g):
        return (min(g), max(g))

    def build_program_graph(self):
        self.prog_graph = nx.Graph()
        edge_weights = {}
        for g in self.parse_obj.gate_graph:
            g_qubits = self.parse_obj.cx_gate_map[g]
            tup = self.gate_tuple(g_qubits)
            if tup in edge_weights:
                edge_weights[tup] += 1
            else:
                edge_weights[tup] = 1
        #print(edge_weights)
        for key in edge_weights:
            self.prog_graph.add_edge(*key, weight=edge_weights[key])
        #print(prog_graph.edges)

    def _is_mapped(self, qubit):
        for item in self.mapping:
            if qubit in item:
                return True
        return False

    def _trap(self, qubit):
        for i, item in enumerate(self.mapping):
            if qubit in item:
                return i
        assert 0

    def _select_next_edge(self):
        """Select the next edge.
        If there is an edge with one endpoint mapped, return it.
        Else return in the first edge
        """
        for edge in self.pending_program_edges:
            q1_mapped = self._is_mapped(edge[0])
            q2_mapped = self._is_mapped(edge[1])
            assert not (q1_mapped and q2_mapped)
            if q1_mapped or q2_mapped:
                return edge
        return self.pending_program_edges[0]

    def _map_qubit(self, qubit):
        #Iterate through traps and pick the best one
        all_dist = []
        for target_trap in range(len(self.machine_obj.traps)):
            if self.remaining_capacity[target_trap] == 0:
                all_dist.append(float('inf'))
            else:
                sum_distances = 0
                for n in self.prog_graph.neighbors(qubit):
                    if self._is_mapped(n):
                        src_trap = self._trap(n)
                        path = self.router.find_route(src_trap, target_trap)
                        sum_distances += len(path)
                all_dist.append(sum_distances)
        if all_dist:
            return all_dist.index(min(all_dist))
        else:
            for i, val in enumerate(self.remaining_capacity):
                if val > 0:
                    return i
        assert 0

    def compute_mapping(self):
        for end1, end2, _ in sorted(self.prog_graph.edges(data=True),
                                    key=lambda x: x[2]['weight'], reverse=True):
            self.pending_program_edges.append((end1, end2))
        while self.pending_program_edges:
            edge = self._select_next_edge()
            q1_mapped = self._is_mapped(edge[0])
            q2_mapped = self._is_mapped(edge[1])
            if not q1_mapped:
                q1_trap = self._map_qubit(edge[0])
                self.mapping[q1_trap].append(edge[0])
                self.remaining_capacity[q1_trap] -= 1
            if not q2_mapped:
                q2_trap = self._map_qubit(edge[1])
                self.mapping[q2_trap].append(edge[1])
                self.remaining_capacity[q2_trap] -= 1
            tmplist = [x for x in self.pending_program_edges if not (self._is_mapped(x[0]) and self._is_mapped(x[1]))]
            self.pending_program_edges = tmplist
        output_partition = {}
        for i in range(len(self.mapping)):
            output_partition[i] = self.mapping[i]
        return output_partition

class QubitMapLPFS:
    def __init__(self, parse_obj, machine_obj, excess_capacity=0):
        self.parse_obj = parse_obj
        self.machine_obj = machine_obj
        self.excess_capacity = excess_capacity

    def compute_mapping(self):
        gate_graph = copy.deepcopy(self.parse_obj.gate_graph)
        k = len(self.machine_obj.traps)
        cap = self.machine_obj.traps[0].capacity
        already_mapped = []
        mapping = []
        for i in range(k):
            path = nx.algorithms.dag.dag_longest_path(gate_graph)
            qubit_set = []
            used_gates = []
            for g in path:
                if len(qubit_set) >= cap-1:
                    break
                g_qubits = self.parse_obj.cx_gate_map[g]
                if g == 992:
                    print(g_qubits)
                for qubit in g_qubits:
                    if qubit in already_mapped:
                        continue
                    qubit_set.append(qubit)
                    already_mapped.append(qubit)
                    if not g in used_gates:
                        used_gates.append(g)
            mapping.append(qubit_set)
            for g in used_gates:
                gate_graph.remove_node(g)
        num_qubits = len(list(self.parse_obj.cx_graph.nodes))
        output_partition = {}
        for i, qubit_set in enumerate(mapping):
            for q in qubit_set:
                output_partition[q] = i
        num_qubits = len(list(self.parse_obj.cx_graph.nodes))
        for i in range(num_qubits):
            if not i in output_partition:
                output_partition[i] = k-1
        return(output_partition)

class QubitMapRandom:
    def __init__(self, parse_obj, machine_obj, excess_capacity=0):
        self.parse_obj = parse_obj
        self.machine_obj = machine_obj
        self.excess_capacity = excess_capacity

    def compute_mapping(self):
        num_qubits = len(list(self.parse_obj.cx_graph.nodes))
        partition = []
        trap_sizes = []
        for t in self.machine_obj.traps:
            trap_sizes.append(t.capacity-self.excess_capacity)
        for i in range(len(trap_sizes)):
            partition.extend([i]*trap_sizes[i])
        partition = partition[:num_qubits]
        np.random.shuffle(partition)
        output_partition = {}
        for i in range(len(partition)):
            output_partition[i] = partition[i]
        return output_partition

class QubitMapPO:
    def __init__(self, parse_obj, machine_obj, excess_capacity=0):
        self.parse_obj = parse_obj
        self.machine_obj = machine_obj
        self.excess_capacity = excess_capacity

    def compute_mapping(self):
        num_qubits = len(list(self.parse_obj.cx_graph.nodes))
        partition = []
        trap_sizes = []
        for t in self.machine_obj.traps:
            trap_sizes.append(t.capacity-self.excess_capacity)
        for i in range(len(trap_sizes)):
            partition.extend([i]*trap_sizes[i])
        partition = partition[:num_qubits]
        output_partition = {}
        for i in range(len(partition)):
            output_partition[i] = partition[i]
        return output_partition

class QubitMapMetis:
    def __init__(self, parse_obj, machine_obj):
        self.parse_obj = parse_obj
        self.machine_obj = machine_obj

    def partition_graph(self, parts, cx_graph):
        tpwgts = []
        ubvec = [1.1]
        for i in range(parts):
            tpwgts.append((1.0/parts))
        out = mt.part_graph(cx_graph, nparts=parts, tpwgts=tpwgts, ubvec=ubvec)
        return out

    def compute_mapping(self):
        num_parts = len(self.machine_obj.traps)
        parts = self.partition_graph(num_parts, self.parse_obj.cx_graph)
        #TODO: can we partition with lesser parts?
        #TODO: initial mapping may exceed bounds
        #TODO: init mapping not aware of cluster distances
        #TODO: adjust mapping partition: full set of clusters with tail cluster
        tot_wt = 0
        for c in self.parse_obj.edge_weights.keys():
            for t in self.parse_obj.edge_weights[c].keys():
                tot_wt += self.parse_obj.edge_weights[c][t]
        output_partition = {}
        for i in range(len(parts[1])):
            output_partition[i] = parts[1][i]
        return output_partition

class QubitMapAgg():
    def __init__(self, parse_obj, machine_obj):
        self.parse_obj = parse_obj
        self.machine_obj = machine_obj
        self.num_traps = len(self.machine_obj.traps)
        self.num_nodes = len(self.parse_obj.cx_graph.nodes)
        print(self.num_nodes)
        self.trap_capacity = self.machine_obj.traps[0].capacity
        self.occupied_traps = 0
        self.qubit_mapping = {}
        self.trap_empty_space = {}
        for i in range(self.num_traps):
            self.trap_empty_space[i] = self.trap_capacity
    #
    def select_from_clusters(self, u, nclusters):
        curr_clusters = []
        for i in range(nclusters):
            curr_clusters.append([])

        for i in range(len(u)):
            curr_clusters[u[i]].append(i)
        bad_cluster = False
        for clus in curr_clusters:
            if len(clus) > self.trap_capacity:
                bad_cluster = True
        if bad_cluster:
            return 0

        curr_clusters.sort(key=len, reverse=True)
        top_k = min(3, self.num_traps)
        top_k = min(top_k, nclusters)
        for i in range(top_k):
            clus = curr_clusters[i]
            #print("Map", clus, "trap", i)
            for pq in clus:
                self.qubit_mapping[pq] = i
            self.trap_empty_space[i] -= len(clus)

        #print("unmapped")
        #print("caps:", self.trap_empty_space)
        for clus in curr_clusters[top_k:]:
            #if clus fits fully in some trap, assign it there
            is_assigned = False
            for i in range(self.num_traps):
                if self.trap_empty_space[i] >= len(clus):
                    #print("Map", clus, "trap", i)
                    for pq in clus:
                        self.qubit_mapping[pq] = i
                    self.trap_empty_space[i] -= len(clus)
                    is_assigned = True
                    break
            if not is_assigned:
                for i in range(self.num_traps):
                    available_capacity = self.trap_empty_space[i]
                    #print("Map", clus, "trap", i)
                    for pq in clus[:available_capacity]:
                        self.qubit_mapping[pq] = i
                    self.trap_empty_space[i] -= available_capacity
                    new_clus = clus[available_capacity:]

        return 1

    def compute_mapping(self):
        #compute affinity matrix of distances
        #distance function 1 - f/T
        affinity_matrix = np.ones([self.num_nodes, self.num_nodes])
        T = 0
        for u, v, d in self.parse_obj.cx_graph.edges(data=True):
            T = max(T, d['weight'])
        for u, v, d in self.parse_obj.cx_graph.edges(data=True):
            f = d['weight']
            factor = float(f)/T
            affinity_matrix[u][v] = 1.0 - (factor)
            affinity_matrix[v][u] = 1.0 - (factor)
        for i in range(1, self.num_nodes):
            agg = AggClus(n_clusters = i, affinity='precomputed', linkage='average')
            u = agg.fit_predict(affinity_matrix)
            #print("Clustering level", i)
            done = self.select_from_clusters(u, i)
            if done == 1:
                break
        return self.qubit_mapping

'''
Reorders qubits within a region according to fidelity
Simple heuristic for now: places qubits with lot of gates
around the the center of the chain
'''
class QubitOrdering():
    def __init__(self, parse_obj, machine_obj, qubit_mapping):
        self.parse_obj = parse_obj
        self.machine_obj = machine_obj
        self.mapping = qubit_mapping
        self.trap_capacity = self.machine_obj.traps[0].capacity
        self.num_traps = len(self.machine_obj.traps)

    def reorder_naive(self):
        output_layout = {}
        for i in range(self.num_traps):
            this_layout = []
            for q in self.mapping.keys():
                if self.mapping[q] == i: # q belongs to trap i
                    this_layout.append(q)
            output_layout[i] = this_layout
        return output_layout

    def reorder_fidelity(self):
        output_layout = {}
        for i in range(self.num_traps):
            this_layout = []
            candidates = []
            for q in self.mapping.keys():
                if self.mapping[q] == i: # q belongs to trap i
                    candidates.append(q)

            candidates_with_wt = []
            for c in candidates:
                wt = 0
                for u, v, d in self.parse_obj.cx_graph.edges(data=True):
                    if u == c or v == c:
                        wt += d['weight']
                candidates_with_wt.append((c, wt))
            #Find weight of each qubit as the no. of gates using the qubits
            #Sort qubits according to descending order of weight
            candidates_with_wt.sort(key=lambda tup: tup[1], reverse=True)
            coin = 0
            #Places qubits in an odd-even fashion around the center of the chain
            for item in candidates_with_wt:
                if coin == 0:
                    this_layout.append(item[0])
                    coin = 1
                elif coin == 1:
                    this_layout.insert(0, item[0])
                    coin = 0
            output_layout[i] = this_layout
        return output_layout
