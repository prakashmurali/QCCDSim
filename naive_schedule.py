#Not used as of now

import networkx as nx
import numpy as np

routing_graph = nx.Graph()

def trap_name(i):
    return "T"+str(i)
def seg_name(i):
    return "S"+str(i)

def create_routing_graph(machine_obj):
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
    print(routing_graph.edges)

def update_routing_graph_weights(machine_obj, source_trap):
     for t in machine_obj.traps:
        if t.id == source_trap:
            if t.end1_segment != None:
                routing_graph[trap_name(t.id)][seg_name(t.end1_segment)]['weight'] = 0
            elif t.end2_segment != None:
                routing_graph[trap_name(t.id)][seg_name(t.end2_segment)]['weight'] = 0
        else:
            if t.end1_segment != None:
                if len(t.ions) < t.capacity:
                    my_weight = 0
                else:
                    my_weight = 100000
                routing_graph[trap_name(t.id)][seg_name(t.end1_segment)]['weight'] = my_weight
            if t.end2_segment != None:
                if len(t.ions) < t.capacity:
                    my_weight = 0
                else:
                    my_weight = 100000
                routing_graph[trap_name(t.id)][seg_name(t.end2_segment)]['weight'] = my_weight
     for s in machine_obj.segments:
        for s2 in s.seg_edges:
            if len(s.ions) != 0:
                my_weight = 100000
            else:
                my_weight = (s.length + machine_obj.segments[s2].length)/2 #replace by length of this path?
            routing_graph[seg_name(s.id)][seg_name(s2)]['weight'] = my_weight
def print_partition_sizes(machine_obj):
    sizes = []
    for t in machine_obj.traps:
        sizes.append(len(t.ions))
    print(sizes)
def load_ions(machine_obj, initial_map):
    print(initial_map)
    for i in range(len(initial_map)):
        machine_obj.traps[initial_map[i]].ions.append(i)

def naive_schedule(ir, initial_map, cx_gate_map):
    sorted_gates = nx.topological_sort(ir)
    qmap = initial_map[:]
    cnt = 0
    for g in sorted_gates:
        #print(g, cx_gate_map[g])
        part1 = qmap[cx_gate_map[g][0]]
        part2 = qmap[cx_gate_map[g][1]]
        if part1 != part2:
            #print("needs shuttling")
            cnt += 1
            if np.random.random() < 0.5:
                qmap[cx_gate_map[g][1]] = part1
            else:
                qmap[cx_gate_map[g][0]] = part2
    print("Shuttled", cnt)

def compute_weight(path):
    wt = 0
    for i in range(len(path)-1):
        wt += routing_graph[path[i]][path[i+1]]['weight']
    return wt

def find_trap_id(machine_obj, ion_id):
    for t in machine_obj.traps:
        if ion_id in t.ions:
            return t.id

def schedule_one_by_one(ir, initial_map, cx_gate_map, machine_obj):
    sorted_gates = nx.topological_sort(ir)
    qmap = initial_map[:]
    load_ions(machine_obj, initial_map)
    cnt = 0
    cnt_other = 0
    print_partition_sizes(machine_obj)
    for g in sorted_gates:
        ctrl = cx_gate_map[g][0]
        targ = cx_gate_map[g][1]
        part1 = find_trap_id(machine_obj, ctrl)
        part2 = find_trap_id(machine_obj, targ)
        if part1 != part2:
            print("needs shuttling ", ctrl, targ)
            update_routing_graph_weights(machine_obj, part1)
            sp1 = nx.shortest_path(routing_graph, source=trap_name(part1), target=trap_name(part2), weight='weight')
            weight_sp1 = compute_weight(sp1)
            #print(sp1, compute_weight(sp1))
            update_routing_graph_weights(machine_obj, part2)
            sp2 = nx.shortest_path(routing_graph, source=trap_name(part2), target=trap_name(part1), weight='weight')
            #print(sp2, compute_weight(sp2))
            weight_sp2 = compute_weight(sp2)
            print(part1, part2)
            print_partition_sizes(machine_obj)

            if weight_sp1 <= weight_sp2:
                machine_obj.traps[part1].ions.remove(ctrl)
                machine_obj.traps[part2].ions.append(ctrl)
            else:
                machine_obj.traps[part1].ions.append(targ)
                machine_obj.traps[part2].ions.remove(targ)
            print_partition_sizes(machine_obj)
            cnt += 1
        else:
            cnt_other += 1
    print_partition_sizes(machine_obj)
    print("Shuttled", cnt)
    print("Free", cnt_other)
