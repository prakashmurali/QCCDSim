import sys
from parse import InputParse
from mappers import *
from machine import Machine, MachineParams, Trap, Segment
from ejf_schedule import Schedule, EJFSchedule
from analyzer import *
from test_machines import *
import numpy as np
from qiskit import QuantumCircuit
from qiskit.converters import circuit_to_dag
from qiskit.visualization import dag_drawer

np.random.seed(12345)

#Command line args
#Machine attributes
openqasm_file_name = sys.argv[1]
machine_type = sys.argv[2]
num_ions_per_region = int(sys.argv[3])
mapper_choice = sys.argv[4]
reorder_choice = sys.argv[5]
serial_trap_ops = int(sys.argv[6])
serial_comm = int(sys.argv[7])
serial_all = int(sys.argv[8])
gate_type = sys.argv[9]
swap_type = sys.argv[10]

##########################################################
mpar_model1 = MachineParams()
mpar_model1.alpha = 0.003680029
mpar_model1.beta = 39.996319971
mpar_model1.split_merge_time = 80
mpar_model1.shuttle_time = 5
mpar_model1.junction2_cross_time = 5
mpar_model1.junction3_cross_time = 100
mpar_model1.junction4_cross_time = 120
mpar_model1.gate_type = gate_type
mpar_model1.swap_type = swap_type
mpar_model1.ion_swap_time = 42
machine_model = "MPar1"

'''
mpar_model2 = MachineParams()
mpar_model2.alpha = 0.003680029
mpar_model2.beta = 39.996319971
mpar_model2.split_merge_time = 80
mpar_model2.shuttle_time = 5
mpar_model2.junction2_cross_time = 5
mpar_model2.junction3_cross_time = 100
mpar_model2.junction4_cross_time = 120
mpar_model2.alpha
machine_model = "MPar2"
'''

print("Simulation")
print("Program:", openqasm_file_name)
print("Machine:", machine_type)
print("Model:", machine_model)
print("Ions:", num_ions_per_region)
print("Mapper:", mapper_choice)
print("Reorder:", reorder_choice)
print("SerialTrap:", serial_trap_ops)
print("SerialComm:", serial_comm)
print("SerialAll:", serial_all)
print("Gatetype:", gate_type)
print("Swaptype:", swap_type)

#Create a test machine
if machine_type == "G2x3":
    m = test_trap_2x3(num_ions_per_region, mpar_model1)
elif machine_type == "L6":
    m = make_linear_machine(6, num_ions_per_region, mpar_model1)
elif machine_type == "H6":
    m = make_single_hexagon_machine(num_ions_per_region, mpar_model1)
else:
    assert 0

#Parse the input program DAG
ip = InputParse()
ip.parse_ir(openqasm_file_name)
ip.visualize_graph("visualize_graph_2.gexf") # dumps parser graph into file

qc = QuantumCircuit.from_qasm_file(openqasm_file_name)
dag = circuit_to_dag(qc)
dag_drawer(dag)

print("parse object map:")
print(ip.cx_gate_map)
print("parse object graph:")
print(ip.gate_graph)

#Map the program onto the machine regions
#For every program qubit, this gives a region id
if mapper_choice == "LPFS":
    qm = QubitMapLPFS(ip,m)
elif mapper_choice == "Agg":
    qm = QubitMapAgg(ip, m)
elif mapper_choice == "Random":
    qm = QubitMapRandom(ip, m)
elif mapper_choice == "PO":
    qm = QubitMapPO(ip, m)
elif mapper_choice == "Greedy":
    qm = QubitMapGreedy(ip, m)
else:
    assert 0
mapping = qm.compute_mapping()

#Reorder qubits within a region to increse the use of high fidelity operations
if mapper_choice == "Greedy":
    init_qubit_layout = mapping
else:
    qo = QubitOrdering(ip, m, mapping)
    if reorder_choice == "Naive":
        init_qubit_layout = qo.reorder_naive()
    elif reorder_choice == "Fidelity":
        init_qubit_layout = qo.reorder_fidelity()
    else:
        assert 0

print(init_qubit_layout)

#Schedule gates in the prorgam in topological sorted order
#EJF = earliest job first, here it refers to earliest gate first
#This step performs the shuttling
ejfs = EJFSchedule(ip.gate_graph, ip.cx_gate_map, m, init_qubit_layout, serial_trap_ops, serial_comm, serial_all)
ejfs.run()

#Analyze the output schedule and print statistics
analyzer = Analyzer(ejfs.schedule, m, init_qubit_layout)
analyzer.move_check()
print("SplitSWAP:", ejfs.split_swap_counter)
#analyzer.print_events()
print("----------------")
