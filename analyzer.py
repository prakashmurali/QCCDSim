from utils import *
from machine_state import *
from schedule import *
from queue import PriorityQueue
import numpy as np
import math

class Analyzer:
    def __init__(self, schedule_obj, machine_obj, init_mapping):
        self.schedule = schedule_obj
        self.machine = machine_obj
        self.init_map = init_mapping

        self.honeywell_mode = True
        self.chain_heating = []
        self.qubit_heating_quantas = {}
        capacity = self.machine.traps[0].capacity
        for k in range(len(self.machine.traps)):
            self.chain_heating.append(0)

        for k in range(len(self.machine.traps)*capacity):
            self.qubit_heating_quantas[k] = 0

        self.f_background_term = []
        self.f_mode_term = []
        self.gate_fidelities = []

    def gate_fidelity(self, sys_state, trap_id, ion1, ion2):
        assert ion1 != ion2
        chain_size = len(sys_state.trap_ions[trap_id])
        A = max(0.0001, 0.0001*chain_size/math.log(chain_size) - 0.00053)
        gate_time_est = self.machine.gate_time(sys_state, trap_id, ion1, ion2)
        radial_heating_rate = 1
        if self.honeywell_mode == True:
            fidelity = 0.992
        else:
            fidelity = 1
        x1 = float(radial_heating_rate*gate_time_est/10**6)
        x2 = float(A*(2*self.chain_heating[trap_id] + 1))
        fidelity = max(0.0001, fidelity - x1 - x2)

        self.f_background_term.append(x1)
        self.f_mode_term.append(x2)
        self.gate_fidelities.append(1-fidelity)
        fidelity_upper_bound = math.log(fidelity)
        return fidelity_upper_bound

    #(id, event_type, start_time, end_time, event_info_dict)
    def move_check(self):
        op_count = {}
        op_count[Schedule.Gate] = 0
        op_count[Schedule.Split] = 0
        op_count[Schedule.Move] = 0
        op_count[Schedule.Merge] = 0
        op_times = {}
        op_times[Schedule.Gate] = 0
        op_times[Schedule.Split] = 0
        op_times[Schedule.Move] = 0
        op_times[Schedule.Merge] = 0

        sys_state = MachineState(0, self.init_map, {})
        q = PriorityQueue()
        #self.schedule.print_events()
        prog_fin_time = 0
        log_fidelity = 0.0
        for event in self.schedule.events:
            #print(event)
            start_time = event[2]
            prog_fin_time = max(prog_fin_time, event[3])
            q.put((start_time, event))
        print("Program Finish:", prog_fin_time)
        while not q.empty():
            item = q.get()
            event = item[1]
            if event[1] == Schedule.Gate:
                ions = event[4]['ions']
                trap = event[4]['trap']
                op_count[Schedule.Gate] += 1
                op_times[Schedule.Gate] += event[3]-event[2]
                assert sys_state.find_trap_id_by_ion(ions[0]) == trap
                assert sys_state.find_trap_id_by_ion(ions[1]) == trap
                log_g_fidelity = self.gate_fidelity(sys_state, trap, ions[0], ions[1])
                log_fidelity = log_fidelity + log_g_fidelity
            elif event[1] == Schedule.Split:
                ions = event[4]['ions']
                trap = event[4]['trap']
                seg = event[4]['seg']
                swap_cnt = event[4]['swap_cnt']
                ion_swap_hops = event[4]['ion_hops']
                gate_swap_hops = event[4]['swap_hops']
                i1 = event[4]['i1']
                i2 = event[4]['i2']
                op_count[Schedule.Split] += 1
                op_times[Schedule.Split] += event[3]-event[2]

                chain_size = len(sys_state.trap_ions[trap])
                quanta = float(self.chain_heating[trap])/chain_size

                if ion_swap_hops != 0:
                    #print("IS:",ion_swap_hops)
                    self.chain_heating[trap] += 0.1*ion_swap_hops + 0.1*(ion_swap_hops-1) #(one per split, merge)
                    self.chain_heating[trap] += 0.01*ion_swap_hops #(one per move)
                    self.qubit_heating_quantas[ions[0]] = quanta + 0.1

                if gate_swap_hops != 0:
                    #swap of distance gate_swap_gops
                    if i1 != i2:
                        log_swap_fid = self.gate_fidelity(sys_state, trap, i1, i2)*3
                        log_fidelity = log_fidelity + log_swap_fid
                    if self.honeywell_mode == True:
                        val = 2
                    else:
                        val = 0.1
                    self.chain_heating[trap] = self.chain_heating[trap]-quanta + val
                    self.qubit_heating_quantas[ions[0]] = quanta + val

                sys_state.process_split(trap, seg, ions)

            elif event[1] == Schedule.Move:
                ions = event[4]['ions']
                seg1 = event[4]['source_seg']
                seg2 = event[4]['dest_seg']
                op_count[Schedule.Move] += 1
                op_times[Schedule.Move] += event[3]-event[2]
                sys_state.process_move(seg1, seg2, ions)
                for i in ions:
                    if self.honeywell_mode == True:
                        val = 2
                    else:
                        val = 0.01
                    self.qubit_heating_quantas[i] += val
            elif event[1] == Schedule.Merge:
                ions = event[4]['ions']
                trap = event[4]['trap']
                seg = event[4]['seg']
                op_count[Schedule.Merge] += 1
                op_times[Schedule.Merge] += event[3]-event[2]
                sys_state.process_merge(trap, seg, ions)
                #print("Pre-Merge", self.chain_heating, self.qubit_heating_quantas[ions[0]])
                if self.honeywell_mode == True:
                    val = 2
                else:
                    val = 0.1
                self.chain_heating[trap] += self.qubit_heating_quantas[ions[0]] + val
                self.qubit_heating_quantas[ions[0]] = 0
                #print("Post-Merge", self.chain_heating, self.qubit_heating_quantas[ions[0]])

            else:
                assert 0
        print("OPCOUNTS Gate:", op_count[Schedule.Gate], "Split:", op_count[Schedule.Split], "Move:", op_count[Schedule.Move], "Merge:", op_count[Schedule.Merge])
        print("Gate:", op_times[Schedule.Gate], "Split:", op_times[Schedule.Split], "Move:", op_times[Schedule.Move], "Merge:", op_times[Schedule.Merge])
        print("Fidelity:", math.exp(log_fidelity))
        heating_sum = sum(self.chain_heating)
        print("Heating:", int(heating_sum))
