import sys
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import sys
import pandas as pd
import matplotlib.lines as Line2D
from pylab import rcParams

def geo_mean(iterable):
    a = np.array(iterable)
    return a.prod()**(1.0/len(a))

def plot_ion_sizing_comm_output(fname, metric, out_fname):
    plt.rc('text', usetex=True)
    plt.rc('text.latex', preamble=r'\usepackage{amsmath}\usepackage{amssymb}')
    f = open(fname, 'r')
    l = f.readlines()
    all_records = {}
    idx=-1
    unique_ions = []
    unique_machines = []
    for line in l:
        line = line.rstrip('\n')
        if line.startswith("Simulation"):
            idx += 1
            all_records[idx] = {}
        elif line.startswith("Program:"):
            all_records[idx]['program'] = line.split(' ')[-1].split('/')[-1]
        elif line.startswith("Machine:"):
            all_records[idx]['machine'] = line.split(' ')[-1]
            unique_machines.append(all_records[idx]['machine'])
        elif line.startswith('Ions:'):
            all_records[idx]['ions'] = int(line.split(' ')[-1])
            unique_ions.append(all_records[idx]['ions'])
        elif line.startswith('Program Finish:'):
            all_records[idx]['time'] = int(line.split(':')[-1])
        elif line.startswith('Fidelity:'):
            all_records[idx]['fidelity'] = float(line.split(' ')[-1])
    #xaxis range - ions
    xaxis_cnt = len(list(set(unique_ions)))
    x = np.arange(0, xaxis_cnt)

    for m in list(set(unique_machines)):
        y_vals = []
        for idx in all_records:
            if all_records[idx]['machine'] == m:
                y_vals.append(all_records[idx][metric])
        plt.plot(x,y_vals, label=m)
        #print(m)
        #print(y_vals)
    label_font = 26
    tick_font = 22
    #locs, labels = plt.xticks()            # Get locations and labels
    plt.xticks(x, sorted(list(set(unique_ions))))  # Set locations and labels

    plt.xlabel("Ions per region", fontsize=label_font)
    plt.ylabel("Estimated fidelity", fontsize=label_font)
    plt.tick_params(labelsize=tick_font)
    plt.rc('text', usetex=True)
    #plt.yscale('log')
    plt.legend(loc='upper center', fontsize=22, bbox_to_anchor=(0.5,1.2), ncol=3)
    plt.savefig(out_fname, bbox_inches='tight')
    plt.clf()
'''
plot_ion_sizing_comm_output("logs/new_model/qft_ion_comm_var.log", "fidelity", "qft_fidelity.pdf")
plot_ion_sizing_comm_output("logs/new_model/qaoa_ion_comm_var.log", "fidelity", "qaoa_fidelity.pdf")
plot_ion_sizing_comm_output("logs/new_model/sqrt_ion_comm_var.log", "fidelity", "sqrt_fidelity.pdf")
plot_ion_sizing_comm_output("logs/new_model/sup_ion_comm_var.log", "fidelity", "sup_fidelity.pdf")
plot_ion_sizing_comm_output("logs/new_model/qft_ion_comm_var.log", "time", "qft_time.pdf")
plot_ion_sizing_comm_output("logs/new_model/qaoa_ion_comm_var.log", "time", "qaoa_time.pdf")
plot_ion_sizing_comm_output("logs/new_model/sqrt_ion_comm_var.log", "time", "sqrt_time.pdf")
plot_ion_sizing_comm_output("logs/new_model/sup_ion_comm_var.log", "time", "sup_time.pdf")
'''


def plt_gate_impln(fname, out_fname, app_name, metric):
    plt.rc('text', usetex=True)
    plt.rc('text.latex', preamble=r'\usepackage{amsmath}\usepackage{amssymb}')
    f = open(fname, 'r')
    l = f.readlines()
    all_records = {}
    idx=-1
    unique_ions = []
    unique_machines = []
    for line in l:
        line = line.rstrip('\n')
        if line.startswith("Simulation"):
            idx += 1
            all_records[idx] = {}
        elif line.startswith("Program:"):
            all_records[idx]['program'] = line.split(' ')[-1].split('/')[-1]
        elif line.startswith("Machine:"):
            all_records[idx]['machine'] = line.split(' ')[-1]
            unique_machines.append(all_records[idx]['machine'])
        elif line.startswith('Ions:'):
            all_records[idx]['ions'] = int(line.split(' ')[-1])
            unique_ions.append(all_records[idx]['ions'])
        elif line.startswith('Program Finish:'):
            all_records[idx]['time'] = int(line.split(':')[-1])/10**6
        elif line.startswith('Fidelity:'):
            all_records[idx]['fidelity'] = float(line.split(' ')[-1])
        elif line.startswith('Gatetype:'):
            all_records[idx]['gate_type'] = line.split(' ')[-1]
        elif line.startswith('Swaptype:'):
            all_records[idx]['swap_type'] = line.split(' ')[-1]

    #xaxis range - ions
    xaxis_cnt = len(list(set(unique_ions)))
    x = np.arange(0, xaxis_cnt)

    duan_gswap = []
    trout_gswap = []
    fm_gswap = []
    pm_gswap = []

    duan_iswap = []
    trout_iswap = []
    fm_iswap = []
    pm_iswap = []

    for idx in all_records:
        if not app_name in all_records[idx]['program']:
            continue
        if all_records[idx]['gate_type'] == "Duan" and all_records[idx]['swap_type'] == "GateSwap":
            duan_gswap.append(all_records[idx][metric])
        elif all_records[idx]['gate_type'] == "Duan" and all_records[idx]['swap_type'] == "IonSwap":
            duan_iswap.append(all_records[idx][metric])
        if all_records[idx]['gate_type'] == "Trout" and all_records[idx]['swap_type'] == "GateSwap":
            trout_gswap.append(all_records[idx][metric])
        elif all_records[idx]['gate_type'] == "Trout" and all_records[idx]['swap_type'] == "IonSwap":
            trout_iswap.append(all_records[idx][metric])
        if all_records[idx]['gate_type'] == "FM" and all_records[idx]['swap_type'] == "GateSwap":
            fm_gswap.append(all_records[idx][metric])
        elif all_records[idx]['gate_type'] == "FM" and all_records[idx]['swap_type'] == "IonSwap":
            fm_iswap.append(all_records[idx][metric])
        if all_records[idx]['gate_type'] == "PM" and all_records[idx]['swap_type'] == "GateSwap":
            pm_gswap.append(all_records[idx][metric])
        elif all_records[idx]['gate_type'] == "PM" and all_records[idx]['swap_type'] == "IonSwap":
            pm_iswap.append(all_records[idx][metric])
    if 0:
        plt.plot(x,duan_iswap, label="AM1-IS", marker='s', linestyle='--', markersize=12)
        plt.plot(x,duan_gswap, label="AM1-GS", marker='o', markersize=12)

        plt.plot(x,trout_iswap, label="AM2-IS", marker='*', linestyle='--', markersize=12)
        plt.plot(x,trout_gswap, label="AM2-GS", marker='^', markersize=12)

        plt.plot(x,pm_iswap, label="PM-IS", marker='d', linestyle='--', markersize=10)
        plt.plot(x,pm_gswap, label="PM-GS", marker='.', markersize=12)


        plt.plot(x,fm_iswap, label="FM-IS", marker='x', linestyle='--', markersize=12)
        plt.plot(x,fm_gswap, label="FM-GS", marker='v', markersize=12)

        data_fname = "Fig8/" + app_name.split('.')[0] + "_" + metric + ".csv"
        outf = open(data_fname, 'w')
        outf.write('ions,am1_is,am2_is,pm_is,fm_is,am1_gs,am2_gs,pm_gs,fm_gs\n')
        ion_list = sorted(list(set(unique_ions)))
        for i in range(len(x)):
            outf.write(str(ion_list[i]) + \
            ',' + str(duan_iswap[i]) + \
            ',' + str(trout_iswap[i]) + \
            ',' + str(pm_iswap[i]) + \
            ',' + str(fm_iswap[i]) + \
            ',' + str(duan_gswap[i]) + \
            ',' + str(trout_gswap[i]) + \
            ',' + str(pm_gswap[i]) + \
            ',' + str(fm_gswap[i]) + '\n')
        outf.close()

    else:
        data_fname = "honeywell/" + app_name.split('.')[0] + "_fid.csv"
        outf = open(data_fname, 'w')
        outf.write('ions,fidelity\n')
        ion_list = sorted(list(set(unique_ions)))
        for i in range(len(x)):
            outf.write(str(ion_list[i])+','+str(fm_gswap[i]) + '\n')
        outf.close()
        plt.plot(x,fm_gswap, marker='v', markersize=12)
        #print(app_name, max(fm_gswap)/min(fm_gswap))

    #print(app_name, duan_gswap[2], trout_gswap[2], fm_gswap[2])

    label_font = 26
    tick_font = 22
    #locs, labels = plt.xticks()            # Get locations and labels
    plt.xticks(x, sorted(list(set(unique_ions))))  # Set locations and labels

    plt.xlabel("Trap capacity (ions)", fontsize=label_font)
    if metric == "time":
        plt.ylabel("Time (s)", fontsize=label_font)
        #plt.axhline(y=2)
        plt.ylim([0,3])
    else:
        plt.ylabel("Fidelity", fontsize=label_font)


    plt.tick_params(labelsize=tick_font)
    plt.rc('text', usetex=True)
    plt.legend(loc='upper center', fontsize=14, bbox_to_anchor=(0.5,1.2), ncol=4)
    #plt.yscale('log')
    plt.savefig(out_fname, bbox_inches='tight')
    plt.clf()
    print("Done")

if 0:
    #fname = "E3_UARCH_PO.log"
    fname = "R7_Fig8_expts.log"
    plt_gate_impln(fname, "qft_gate_varL6PO_fid.pdf", "qft64.qasm", "fidelity")
    plt_gate_impln(fname, "qaoa_gate_varL6PO_fid.pdf", "qaoa6420.qasm", "fidelity")
    plt_gate_impln(fname, "sqrt_gate_varL6PO_fid.pdf", "square_root_clean.qasm", "fidelity")
    plt_gate_impln(fname, "sup_gate_varL6PO_fid.pdf", "sup64.qasm", "fidelity")
    plt_gate_impln(fname, "bv_gate_varL6PO_fid.pdf", "bv64.qasm", "fidelity")
    plt_gate_impln(fname, "adder_gate_varL6PO_fid.pdf", "adder.qasm", "fidelity")

    plt_gate_impln(fname, "qft_gate_varL6PO_time.pdf", "qft64.qasm", "time")
    plt_gate_impln(fname, "qaoa_gate_varL6PO_time.pdf", "qaoa6420.qasm", "time")
    plt_gate_impln(fname, "sqrt_gate_varL6PO_time.pdf", "square_root_clean.qasm", "time")
    plt_gate_impln(fname, "sup_gate_varL6PO_time.pdf", "sup64.qasm", "time")
    plt_gate_impln(fname, "bv_gate_varL6PO_time.pdf", "bv64.qasm", "time")
    plt_gate_impln(fname, "adder_gate_varL6PO_time.pdf", "adder.qasm", "time")

if 1:
    fname = "R8_honeywell_expts.log"
    plt_gate_impln(fname, "bv_gate_varL6PO_fid.pdf", "bv64.qasm", "fidelity")
    plt_gate_impln(fname, "adder_gate_varL6PO_fid.pdf", "adder.qasm", "fidelity")
    plt_gate_impln(fname, "qft_gate_varL6PO_fid.pdf", "qft64.qasm", "fidelity")
    plt_gate_impln(fname, "qaoa_gate_varL6PO_fid.pdf", "qaoa6420.qasm", "fidelity")
    plt_gate_impln(fname, "sqrt_gate_varL6PO_fid.pdf", "square_root_clean.qasm", "fidelity")
    plt_gate_impln(fname, "sup_gate_varL6PO_fid.pdf", "sup64.qasm", "fidelity")
    #plt_gate_impln(fname, "qft_gate_varL6PO_time.pdf", "qft64.qasm", "time")
    #plt_gate_impln(fname, "qaoa_gate_varL6PO_time.pdf", "qaoa6420.qasm", "time")
    #plt_gate_impln(fname, "sqrt_gate_varL6PO_time.pdf", "square_root_clean.qasm", "time")
    #plt_gate_impln(fname, "sup_gate_varL6PO_time.pdf", "sup64.qasm", "time")

if 0:
    fname = "R4_Fig6_expts.log"
    plt_gate_impln(fname, "bv_gate_varL6PO_fid.pdf", "bv64.qasm", "fidelity")
    plt_gate_impln(fname, "adder_gate_varL6PO_fid.pdf", "adder.qasm", "fidelity")
    plt_gate_impln(fname, "qft_gate_varL6PO_fid.pdf", "qft64.qasm", "fidelity")
    plt_gate_impln(fname, "qaoa_gate_varL6PO_fid.pdf", "qaoa6420.qasm", "fidelity")
    plt_gate_impln(fname, "sqrt_gate_varL6PO_fid.pdf", "square_root_clean.qasm", "fidelity")
    plt_gate_impln(fname, "sup_gate_varL6PO_fid.pdf", "sup64.qasm", "fidelity")
    #plt_gate_impln(fname, "qft_gate_varL6PO_time.pdf", "qft64.qasm", "time")
    #plt_gate_impln(fname, "qaoa_gate_varL6PO_time.pdf", "qaoa6420.qasm", "time")
    #plt_gate_impln(fname, "sqrt_gate_varL6PO_time.pdf", "square_root_clean.qasm", "time")
    #plt_gate_impln(fname, "sup_gate_varL6PO_time.pdf", "sup64.qasm", "time")

if 0:
    fname = "E1_UARCH_2QGATE_L6_PO.log"
    plt_gate_impln(fname, "qft_gate_varL6PO_fid.pdf", "qft64.qasm", "fidelity")
    plt_gate_impln(fname, "qaoa_gate_varL6PO_fid.pdf", "qaoa6420.qasm", "fidelity")
    plt_gate_impln(fname, "sqrt_gate_varL6PO_fid.pdf", "square_root_clean.qasm", "fidelity")
    plt_gate_impln(fname, "sup_gate_varL6PO_fid.pdf", "sup64.qasm", "fidelity")

    #plt_gate_impln(fname, "qft_gate_varL6PO_time.pdf", "qft64.qasm", "time")
    #plt_gate_impln(fname, "qaoa_gate_varL6PO_time.pdf", "qaoa6420.qasm", "time")
    #plt_gate_impln(fname, "sqrt_gate_varL6PO_time.pdf", "square_root_clean.qasm", "time")
    #plt_gate_impln(fname, "sup_gate_varL6PO_time.pdf", "sup64.qasm", "time")


if 0:
    fname = "E1_UARCH_2QGATE_G2x3_LPFS.log"
    plt_gate_impln(fname, "qft_gate_varG2x3LPFS_N_fid.pdf", "qft64.qasm", "fidelity")
    plt_gate_impln(fname, "qaoa_gate_varG2x3LPFS_N_fid.pdf", "qaoa6420.qasm", "fidelity")
    plt_gate_impln(fname, "sqrt_gate_varG2x3LPFS_N_fid.pdf", "square_root_clean.qasm", "fidelity")
    plt_gate_impln(fname, "sup_gate_varG2x3LPFS_N_fid.pdf", "sup64.qasm", "fidelity")

    #plt_gate_impln(fname, "qft_gate_varG2x3LPFS_N_time.pdf", "qft64.qasm", "time")
    #plt_gate_impln(fname, "qaoa_gate_varG2x3LPFS_N_time.pdf", "qaoa6420.qasm", "time")
    #plt_gate_impln(fname, "sqrt_gate_varG2x3LPFS_N_time.pdf", "square_root_clean.qasm", "time")
    #plt_gate_impln(fname, "sup_gate_varG2x3LPFS_N_time.pdf", "sup64.qasm", "time")



if 0:
    fname = "E1_UARCH_2QGATE_G2x3_PO.log"
    plt_gate_impln(fname, "qft_gate_varG2x3PO_N_fid.pdf", "qft64.qasm", "fidelity")
    plt_gate_impln(fname, "qaoa_gate_varG2x3PO_N_fid.pdf", "qaoa6420.qasm", "fidelity")
    plt_gate_impln(fname, "sqrt_gate_varG2x3PO_N_fid.pdf", "square_root_clean.qasm", "fidelity")
    plt_gate_impln(fname, "sup_gate_varG2x3PO_N_fid.pdf", "sup64.qasm", "fidelity")

    plt_gate_impln(fname, "qft_gate_varG2x3PO_N_time.pdf", "qft64.qasm", "time")
    plt_gate_impln(fname, "qaoa_gate_varG2x3PO_N_time.pdf", "qaoa6420.qasm", "time")
    plt_gate_impln(fname, "sqrt_gate_varG2x3PO_N_time.pdf", "square_root_clean.qasm", "time")
    plt_gate_impln(fname, "sup_gate_varG2x3PO_N_time.pdf", "sup64.qasm", "time")




def plt_all_apps_performance(fname, out_fname, metric):
    plt.rc('text', usetex=True)
    plt.rc('text.latex', preamble=r'\usepackage{amsmath}\usepackage{amssymb}')
    f = open(fname, 'r')
    l = f.readlines()
    all_records = {}
    idx=-1
    unique_ions = []
    unique_machines = []
    for line in l:
        line = line.rstrip('\n')
        if line.startswith("Simulation"):
            idx += 1
            all_records[idx] = {}
        elif line.startswith("Program:"):
            all_records[idx]['program'] = line.split(' ')[-1].split('/')[-1]
        elif line.startswith("Machine:"):
            all_records[idx]['machine'] = line.split(' ')[-1]
            unique_machines.append(all_records[idx]['machine'])
        elif line.startswith('Ions:'):
            all_records[idx]['ions'] = int(line.split(' ')[-1])
            unique_ions.append(all_records[idx]['ions'])
        elif line.startswith('Program Finish:'):
            all_records[idx]['time'] = int(line.split(':')[-1])/10**6
        elif line.startswith('Fidelity:'):
            all_records[idx]['fidelity'] = float(line.split(' ')[-1])
        elif line.startswith('Gatetype:'):
            all_records[idx]['gate_type'] = line.split(' ')[-1]
        elif line.startswith('Swaptype:'):
            all_records[idx]['swap_type'] = line.split(' ')[-1]
        elif "HeatingSum:" in line:
            all_records[idx]['heat_max'] = int(line.split(' ')[1])
    #xaxis range - ions
    xaxis_cnt = len(list(set(unique_ions)))
    x = np.arange(0, xaxis_cnt)

    perf = {}
    for idx in all_records:
        app_name = all_records[idx]['program']
        if not app_name in perf.keys():
            perf[app_name] = []
        if all_records[idx]['gate_type'] == "FM" and all_records[idx]['swap_type'] == "GateSwap":
            perf[app_name].append(all_records[idx][metric])

    appnames = ["qft64.qasm", "square_root_clean.qasm","qaoa6420.qasm", "sup64.qasm", "adder.qasm", "bv64.qasm"]
    label_names = ["QFT", "SquareRoot", "QAOA", "Supremacy", "Adder", "BV"]
    markerlist=['o', 'v', 'x', '^', "D", "."]
    for i,app in enumerate(appnames):
        plt.plot(x, perf[app], label=label_names[i],marker=markerlist[i], markersize=10)

    for i,app in enumerate(appnames):
        data_fname = "Fig6/" + app.split('.')[0] + "_motional_mode.csv"
        outf = open(data_fname, 'w')
        outf.write('ions,mode\n')
        ion_list = sorted(list(set(unique_ions)))
        for i in range(len(x)):
            outf.write(str(ion_list[i])+','+str(perf[app][i]) + '\n')
        outf.close()
    label_font = 26
    tick_font = 22
    plt.xticks(x, sorted(list(set(unique_ions))))  # Set locations and labels
    plt.xlabel("Trap capacity (ions)", fontsize=label_font)
    if metric == "time":
        plt.ylabel("Time (s)", fontsize=label_font)
        #plt.axhline(y=2)
        #plt.ylim([0,3])
    elif metric == "heat_max":
        plt.ylabel("Motional quanta", fontsize=label_font)

    plt.tick_params(labelsize=tick_font)
    plt.rc('text', usetex=True)
    plt.legend(loc='upper center', fontsize=16, ncol=2)
    #plt.yscale('log')
    plt.savefig(out_fname, bbox_inches='tight')
    plt.clf()


#plt_all_apps_performance("R4_Fig6_expts.log", "perf.pdf", "time")
#plt_all_apps_performance("R4_Fig6_expts.log", "heat_max.pdf", "heat_max")

def plt_gate_impln_time_split(fname, out_fname, app_name, metric):
    plt.rc('text', usetex=True)
    plt.rc('text.latex', preamble=r'\usepackage{amsmath}\usepackage{amssymb}')
    f = open(fname, 'r')
    l = f.readlines()
    all_records = {}
    idx=-1
    unique_ions = []
    unique_machines = []
    for line in l:
        line = line.rstrip('\n')
        if line.startswith("Simulation"):
            idx += 1
            all_records[idx] = {}
        elif line.startswith("Program:"):
            all_records[idx]['program'] = line.split(' ')[-1].split('/')[-1]
        elif line.startswith("Machine:"):
            all_records[idx]['machine'] = line.split(' ')[-1]
            unique_machines.append(all_records[idx]['machine'])
        elif line.startswith('Ions:'):
            all_records[idx]['ions'] = int(line.split(' ')[-1])
            unique_ions.append(all_records[idx]['ions'])
        elif line.startswith('Program Finish:'):
            all_records[idx]['time'] = int(line.split(':')[-1])/10**6
        elif line.startswith('Fidelity:'):
            all_records[idx]['fidelity'] = float(line.split(' ')[-1])
        elif line.startswith('Gatetype:'):
            all_records[idx]['gate_type'] = line.split(' ')[-1]
        elif line.startswith('Swaptype:'):
            all_records[idx]['swap_type'] = line.split(' ')[-1]
        elif "Split:" in line and "OPCOUNTS" not in line:
            sline = line.split(' ')
            all_records[idx]['gate_time'] = int(sline[1])
            all_records[idx]['split_time'] = int(sline[3])
            all_records[idx]['move_time'] = int(sline[5])
            all_records[idx]['merge_time'] = int(sline[7])
        elif "HeatingMax:" in line:
            all_records[idx]['heat_max'] = int(line.split(' ')[1])

    #xaxis range - ions
    xaxis_cnt = len(list(set(unique_ions)))
    x = np.arange(0, xaxis_cnt)

    duan_gswap_gate_time = []
    trout_gswap_gate_time = []
    fm_gswap_gate_time = []

    duan_gswap_comm_time = []
    trout_gswap_comm_time = []
    fm_gswap_comm_time = []

    duan_heat = []
    trout_heat = []
    fm_heat = []

    for idx in all_records:
        if not app_name in all_records[idx]['program']:
            continue
        print(all_records[idx]['program'])
        if all_records[idx]['gate_type'] == "Duan" and all_records[idx]['swap_type'] == "GateSwap":
            duan_gswap_gate_time.append(float(all_records[idx]['gate_time'])/10**6)
            duan_gswap_comm_time.append(float(all_records[idx]['split_time'] + all_records[idx]['move_time'] + all_records[idx]['merge_time'])/10**6)
        if all_records[idx]['gate_type'] == "Trout" and all_records[idx]['swap_type'] == "GateSwap":
            trout_gswap_gate_time.append(float(all_records[idx]['gate_time'])/10**6)
            out_fname, trout_gswap_comm_time.append(float(all_records[idx]['split_time'] + all_records[idx]['move_time'] + all_records[idx]['merge_time'])/10**6)
            trout_heat.append(all_records[idx]['heat_max'])
        if all_records[idx]['gate_type'] == "FM" and all_records[idx]['swap_type'] == "GateSwap":
            fm_gswap_gate_time.append(float(all_records[idx]['gate_time'])/10**6)
            fm_gswap_comm_time.append(float(all_records[idx]['split_time'] + all_records[idx]['move_time'] + all_records[idx]['merge_time'])/10**6)
            print(all_records[idx])
            fm_heat.append(all_records[idx]['heat_max'])
    #plt.plot(x,duan_gswap_gate_time, label="AM1-Comp", marker='o')
    #plt.plot(x,duan_gswap_comm_time, label="AM1-Comm", marker='o', linestyle='--')
    #plt.plot(x,trout_gswap_gate_time, label="AM2-Comp", marker='^')
    #plt.plot(x,trout_gswap_comm_time, label="AM2-Comm", marker='^', linestyle='--')
    plt.plot(x,fm_gswap_gate_time, label="Compute", marker='^', markersize=12)
    plt.plot(x,fm_gswap_comm_time, label="Communication", marker='v', linestyle='--', markersize=12)

    data_fname = "Fig6/" + "qft_split.csv"
    outf = open(data_fname, 'w')
    outf.write('ions,comp,comm\n')
    ion_list = sorted(list(set(unique_ions)))
    for i in range(len(x)):
        outf.write(str(ion_list[i])+','+str(fm_gswap_gate_time[i]) +','+str(fm_gswap_comm_time[i]) +  '\n')
    outf.close()
    #print("AM2:Heat", trout_heat)
    #print("FM:Heat", fm_heat)
    label_font = 26
    tick_font = 22
    #locs, labels = plt.xticks()            # Get locations and labels
    plt.xticks(x, sorted(list(set(unique_ions))))  # Set locations and labels

    plt.xlabel("Trap capacity (ions)", fontsize=label_font)
    if metric == "time":
        plt.ylabel("Time (s)", fontsize=label_font)
        #plt.ylim([0,2])
    else:
        plt.ylabel("Fidelity", fontsize=label_font)
        #plt.ylim([0,1])
        #plt.ticklabel_format(axis='y', style='sci')
    plt.tick_params(labelsize=16)
    plt.rc('text', usetex=True)
    plt.legend(loc='upper center', fontsize=18, ncol=3)
    #plt.yscale('log')
    plt.savefig(out_fname, bbox_inches='tight')
    plt.clf()

    '''
    plt.plot(x,trout_heat, label="AM2-Heat")
    plt.plot(x,fm_heat, label="FM-Heat")

    plt.tick_params(labelsize=tick_font)
    plt.rc('text', usetex=True)
    plt.legend(loc='upper center', fontsize=18, bbox_to_anchor=(0.5,1.2), ncol=3)
    #plt.yscale('log')
    plt.savefig("heat"+out_fname, bbox_inches='tight')
    print("Done")
    '''

#fname = "E1_UARCH_2QGATE_G2x3_PO.log"
#fname = "E1_UARCH_2QGATE_L6_PO.log"
fname = "R4_Fig6_expts.log"
#plt_gate_impln_time_split(fname, "qft_splitup.pdf", "qft64.qasm", "time")
#plt_gate_impln_time_split(fname, "qaoa_splitup.pdf", "qaoa6420.qasm", "time")
#plt_gate_impln_time_split(fname, "adder_split.pdf", "adder.qasm", "time")
#plt_gate_impln_time_split(fname, "sqrt_splitup.pdf", "square_root_clean.qasm", "time")
#plt_gate_impln_time_split(fname, "sup_splitup.pdf", "sup64.qasm", "time")

def plt_comm(fname, out_fname, app_name, metric):
    plt.rc('text', usetex=True)
    plt.rc('text.latex', preamble=r'\usepackage{amsmath}\usepackage{amssymb}')
    f = open(fname, 'r')
    l = f.readlines()
    all_records = {}
    idx=-1
    unique_ions = []
    unique_machines = []
    for line in l:
        line = line.rstrip('\n')
        if line.startswith("Simulation"):
            idx += 1
            all_records[idx] = {}
        elif line.startswith("Program:"):
            all_records[idx]['program'] = line.split(' ')[-1].split('/')[-1]
        elif line.startswith("Machine:"):
            all_records[idx]['machine'] = line.split(' ')[-1]
            unique_machines.append(all_records[idx]['machine'])
        elif line.startswith('Ions:'):
            all_records[idx]['ions'] = int(line.split(' ')[-1])
            unique_ions.append(all_records[idx]['ions'])
        elif line.startswith('Program Finish:'):
            all_records[idx]['time'] = int(line.split(':')[-1])/10**6
        elif line.startswith('Fidelity:'):
            all_records[idx]['fidelity'] = float(line.split(' ')[-1])
        elif line.startswith('Gatetype:'):
            all_records[idx]['gate_type'] = line.split(' ')[-1]
        elif line.startswith('Swaptype:'):
            all_records[idx]['swap_type'] = line.split(' ')[-1]
        elif "HeatingSum:" in line:
            all_records[idx]['heat_max'] = int(line.split(' ')[1])
    #xaxis range - ions
    xaxis_cnt = len(list(set(unique_ions)))
    x = np.arange(0, xaxis_cnt)

    l6_vals = []
    g2x3_vals = []
    h6_vals = []

    for idx in all_records:
        if not app_name in all_records[idx]['program']:
            continue
        if all_records[idx]['machine'] == "L6":
            l6_vals.append(all_records[idx][metric])
        elif all_records[idx]['machine'] == "G2x3":
            g2x3_vals.append(all_records[idx][metric])
        elif all_records[idx]['machine'] == "H6":
            h6_vals.append(all_records[idx][metric])

    plt.plot(x,l6_vals, label="L6", marker='o', markersize=12)
    plt.plot(x,g2x3_vals, label="G2X3", marker='s', linestyle='--', markersize=12)
    #print(app_name, l6_vals, g2x3_vals)
    #print(app_name, "grid over linear:", max(g2x3_vals)/max(l6_vals))
    #print(app_name, "linear over grid:", max(l6_vals)/max(g2x3_vals))
    #plt.plot(x,h6_vals, label="H6", marker='v')

    print("Vals:", app_name, l6_vals[0],  g2x3_vals[0])
    data_fname = "Fig7/" + app_name.split('.')[0] + "_" + metric + ".csv"
    outf = open(data_fname, 'w')
    outf.write('ions,l6,g2x3\n')
    ion_list = sorted(list(set(unique_ions)))
    for i in range(len(x)):
        outf.write(str(ion_list[i])+','+str(l6_vals[i]) + ',' + str(g2x3_vals[i]) + '\n')

    outf.close()
    label_font = 26
    tick_font = 26
    #locs, labels = plt.xticks()            # Get locations and labels
    plt.xticks(x, sorted(list(set(unique_ions))))  # Set locations and labels

    plt.xlabel("Ions per region", fontsize=label_font)
    if metric == "time":
        plt.ylabel("Time (s)", fontsize=label_font)
    elif metric == "fidelity":
        plt.ylabel("Fidelity", fontsize=label_font)
        #plt.yscale('log')
    elif metric == "heat_max":
        plt.ylabel("Motional quanta", fontsize=label_font)

    plt.tick_params(labelsize=tick_font)
    plt.rc('text', usetex=True)
    plt.legend(loc='upper center', fontsize=24, ncol=2)
    #plt.yscale('log')
    #plt.axhline(y=2)
    plt.savefig(out_fname, bbox_inches='tight')
    plt.clf()
    max_val = max(max(l6_vals), max(g2x3_vals))
    min_val = min(min(l6_vals), min(g2x3_vals))
    #print(metric, app_name, max_val, min_val, max_val/min_val)
    print("Done")

if 0:
    fname = "R5_Fig7_expts.log"
    plt_comm(fname, "qft_comm_var_fid.pdf", "qft64.qasm", "fidelity")
    plt_comm(fname, "sqrt_comm_var_fid.pdf", "square_root_clean.qasm", "fidelity")
    plt_comm(fname, "qaoa_comm_var_fid.pdf", "qaoa6420.qasm", "fidelity")
    plt_comm(fname, "sup_comm_var_fid.pdf", "sup64.qasm", "fidelity")
    plt_comm(fname, "bv_comm_var_fid.pdf", "bv64.qasm", "fidelity")
    plt_comm(fname, "adder_comm_var_fid.pdf", "adder.qasm", "fidelity")


    plt_comm(fname, "qft_comm_var_heat.pdf", "qft64.qasm", "heat_max")
    plt_comm(fname, "sqrt_comm_var_heat.pdf", "square_root_clean.qasm", "heat_max")
    plt_comm(fname, "qaoa_comm_var_heat.pdf", "qaoa6420.qasm", "heat_max")
    plt_comm(fname, "sup_comm_var_heat.pdf", "sup64.qasm", "heat_max")
    plt_comm(fname, "bv_comm_var_heat.pdf", "bv64.qasm", "heat_max")
    plt_comm(fname, "adder_comm_var_heat.pdf", "adder.qasm", "heat_max")

    plt_comm(fname, "qft_comm_var_time.pdf", "qft64.qasm", "time")
    plt_comm(fname, "sqrt_comm_var_time.pdf", "square_root_clean.qasm", "time")
    plt_comm(fname, "qaoa_comm_var_time.pdf", "qaoa6420.qasm", "time")
    plt_comm(fname, "sup_comm_var_time.pdf", "sup64.qasm", "time")
    plt_comm(fname, "bv_comm_var_time.pdf", "bv64.qasm", "time")
    plt_comm(fname, "adder_comm_var_time.pdf", "adder.qasm", "time")


#plt_comm("comm_var_PO.log", "qft_comm_var_fid.pdf", "qft64.qasm", "fidelity")
#plt_comm("comm_var_PO.log", "sqrt_comm_var_fid.pdf", "square_root_clean.qasm", "fidelity")
#plt_comm("comm_var_qaoa_PO.log", "qaoa_comm_var_fid.pdf", "qaoa6420.qasm", "fidelity")




def plt_heating_rates(fname, out_fname, app_name, metric):
    plt.rc('text', usetex=True)
    plt.rc('text.latex', preamble=r'\usepackage{amsmath}\usepackage{amssymb}')
    f = open(fname, 'r')
    l = f.readlines()
    all_records = {}
    idx=-1
    unique_ions = []
    unique_machines = []
    for line in l:
        line = line.rstrip('\n')
        if line.startswith("Simulation"):
            idx += 1
            all_records[idx] = {}
        elif line.startswith("Program:"):
            all_records[idx]['program'] = line.split(' ')[-1].split('/')[-1]
        elif line.startswith("Machine:"):
            all_records[idx]['machine'] = line.split(' ')[-1]
            unique_machines.append(all_records[idx]['machine'])
        elif line.startswith('Ions:'):
            all_records[idx]['ions'] = int(line.split(' ')[-1])
            unique_ions.append(all_records[idx]['ions'])
        elif line.startswith('Program Finish:'):
            all_records[idx]['time'] = int(line.split(':')[-1])/10**6
        elif line.startswith('Fidelity:'):
            all_records[idx]['fidelity'] = float(line.split(' ')[-1])
        elif line.startswith('Gatetype:'):
            all_records[idx]['gate_type'] = line.split(' ')[-1]
        elif line.startswith('Swaptype:'):
            all_records[idx]['swap_type'] = line.split(' ')[-1]
        elif "HeatingSum:" in line:
            all_records[idx]['heat_max'] = int(line.split(' ')[1])
        elif "Infidback:" in line:
            all_records[idx]['infidback'] = float(line.split(' ')[1])
            all_records[idx]['infidback_std'] = float(line.split(' ')[2])

        elif "Infidheat:" in line:
            all_records[idx]['infidheat'] = float(line.split(' ')[1])
            all_records[idx]['infidheat_std'] = float(line.split(' ')[2])

        elif "Minfid:" in line:
            all_records[idx]['minfid'] = float(line.split(' ')[1])
            all_records[idx]['minfid_std'] = float(line.split(' ')[2])

    #xaxis range - ions
    xaxis_cnt = len(list(set(unique_ions)))
    x = np.arange(0, xaxis_cnt)

    infid_back = []
    infid_heat = []
    min_fid = []

    infid_back_err = []
    infid_heat_err = []
    min_fid_err = []

    for idx in all_records:
        if not app_name in all_records[idx]['program']:
            continue
        infid_back.append(all_records[idx]['infidback'])
        infid_back_err.append(all_records[idx]['infidback_std'])
        infid_heat.append(all_records[idx]['infidheat'])
        infid_heat_err.append(all_records[idx]['infidheat_std'])
        min_fid.append(all_records[idx]['minfid'])
        min_fid_err.append(all_records[idx]['minfid_std'])



    plt.errorbar(x,infid_back, yerr=infid_back_err, label="Background heating", marker='o')
    plt.errorbar(x,infid_heat, yerr=infid_heat_err, label="Motional mode", marker='v', elinewidth=0.5, capsize=5, capthick=0.5)
    plt.errorbar(x,min_fid, yerr=min_fid_err, label="Two-qubit gate", marker='^',  elinewidth=0.5, capsize=10, capthick=0.5)
    #plt.yscale('log')
    label_font = 26
    tick_font = 22
    #locs, labels = plt.xticks()            # Get locations and labels
    plt.xticks(x, sorted(list(set(unique_ions))))  # Set locations and labels

    plt.xlabel("Ions per region", fontsize=label_font)
    plt.ylabel("Error Rate", fontsize=label_font)

    plt.tick_params(labelsize=tick_font)
    plt.rc('text', usetex=True)
    plt.legend(loc='upper left', fontsize=16, ncol=1) #bbox_to_anchor=(0.5,1.3))
    #plt.yscale('log')
    #plt.axhline(y=2)
    plt.savefig(out_fname, bbox_inches='tight')
    plt.clf()
    print(fname, max(infid_heat_err)/min(infid_heat_err))
    print("Done")
#plt_heating_rates("E1_SquareRoot.log", "sqaurerootheat.pdf", "square_root_clean.qasm", "junk")
#plt_heating_rates("R4_fig6_expts.log", "supremacyheat.pdf", "sup64.qasm", "junk")




def plt_heating_rates_isca(fname, out_fname, app_name, metric):
    plt.rc('text', usetex=True)
    plt.rc('text.latex', preamble=r'\usepackage{amsmath}\usepackage{amssymb}')
    f = open(fname, 'r')
    l = f.readlines()
    all_records = {}
    idx=-1
    unique_ions = []
    unique_machines = []
    for line in l:
        line = line.rstrip('\n')
        if line.startswith("Simulation"):
            idx += 1
            all_records[idx] = {}
        elif line.startswith("Program:"):
            all_records[idx]['program'] = line.split(' ')[-1].split('/')[-1]
        elif line.startswith("Machine:"):
            all_records[idx]['machine'] = line.split(' ')[-1]
            unique_machines.append(all_records[idx]['machine'])
        elif line.startswith('Ions:'):
            all_records[idx]['ions'] = int(line.split(' ')[-1])
            unique_ions.append(all_records[idx]['ions'])
        elif line.startswith('Program Finish:'):
            all_records[idx]['time'] = int(line.split(':')[-1])/10**6
        elif line.startswith('Fidelity:'):
            all_records[idx]['fidelity'] = float(line.split(' ')[-1])
        elif line.startswith('Gatetype:'):
            all_records[idx]['gate_type'] = line.split(' ')[-1]
        elif line.startswith('Swaptype:'):
            all_records[idx]['swap_type'] = line.split(' ')[-1]
        elif "HeatingSum:" in line:
            all_records[idx]['heat_max'] = int(line.split(' ')[1])
        elif "Infidback:" in line:
            all_records[idx]['infidback'] = float(line.split(' ')[1])
            all_records[idx]['infidback_std'] = float(line.split(' ')[2])

        elif "Infidheat:" in line:
            all_records[idx]['infidheat'] = float(line.split(' ')[1])
            all_records[idx]['infidheat_std'] = float(line.split(' ')[2])

        elif "Minfid:" in line:
            all_records[idx]['minfid'] = float(line.split(' ')[1])
            all_records[idx]['minfid_std'] = float(line.split(' ')[2])

    #xaxis range - ions
    xaxis_cnt = len(list(set(unique_ions)))
    x = np.arange(0, xaxis_cnt)
    width = 0.35

    infid_back = []
    infid_heat = []
    min_fid = []

    infid_back_err = []
    infid_heat_err = []
    min_fid_err = []

    for idx in all_records:
        if not app_name in all_records[idx]['program']:
            continue
        infid_back.append(all_records[idx]['infidback'])
        infid_back_err.append(all_records[idx]['infidback_std'])
        infid_heat.append(all_records[idx]['infidheat'])
        infid_heat_err.append(all_records[idx]['infidheat_std'])
        min_fid.append(all_records[idx]['minfid'])
        min_fid_err.append(all_records[idx]['minfid_std'])


    bottom_for_ge = []
    for i in range(len(infid_back)):
        bottom_for_ge.append(infid_back[i] + infid_heat[i])

    #plt.bar(x,min_fid, yerr=min_fid_err,label="Two-qubit gate") #elinewidth=0.5, capsize=10, capthick=0.5)
    plt.bar(x,infid_back, yerr=infid_back_err, label="Background heating")
    plt.bar(x,infid_heat, yerr=infid_heat_err, bottom=infid_back, label="Motional mode energy"),# elinewidth=0.5, capsize=5, capthick=0.5)


    data_fname = "Fig6/" + "sup_error_analysis.csv"
    outf = open(data_fname, 'w')
    outf.write('ions,background,background_var,motional,motional_var\n')
    ion_list = sorted(list(set(unique_ions)))
    for i in range(len(x)):
        outf.write(str(ion_list[i])+','+str(infid_back[i]) +','+str(infid_back_err[i]) + ','+str(infid_heat[i]) +  ','+str(infid_heat_err[i]) + '\n')
    outf.close()

    #plt.yscale('log')
    label_font = 26
    tick_font = 22
    #locs, labels = plt.xticks()            # Get locations and labels
    plt.xticks(x, sorted(list(set(unique_ions))))  # Set locations and labels

    plt.xlabel("Ions per region", fontsize=label_font)
    plt.ylabel("Two-qubit Gate Error Rate", fontsize=label_font)

    plt.tick_params(labelsize=tick_font)
    plt.rc('text', usetex=True)
    plt.legend(loc='upper left', fontsize=16, ncol=1) #bbox_to_anchor=(0.5,1.3))
    #plt.yscale('log')
    #plt.axhline(y=2)
    plt.savefig(out_fname, bbox_inches='tight')
    plt.clf()
    print(fname, max(infid_heat_err)/min(infid_heat_err))
    print("Done")

#plt_heating_rates_isca("R4_Fig6_expts.log", "supremacyheat.pdf", "sup64.qasm", "junk")



def plt_compiler_validate(fname, out_fname, app_name, metric):
    plt.rc('text', usetex=True)
    plt.rc('text.latex', preamble=r'\usepackage{amsmath}\usepackage{amssymb}')
    f = open(fname, 'r')
    l = f.readlines()
    all_records = {}
    idx=-1
    unique_ions = []
    unique_machines = []
    for line in l:
        line = line.rstrip('\n')
        if line.startswith("Simulation"):
            idx += 1
            all_records[idx] = {}
        elif line.startswith("Program:"):
            all_records[idx]['program'] = line.split(' ')[-1].split('/')[-1]
        elif line.startswith("Machine:"):
            all_records[idx]['machine'] = line.split(' ')[-1]
            unique_machines.append(all_records[idx]['machine'])
        elif line.startswith('Ions:'):
            all_records[idx]['ions'] = int(line.split(' ')[-1])
            unique_ions.append(all_records[idx]['ions'])
        elif line.startswith('Program Finish:'):
            all_records[idx]['time'] = int(line.split(':')[-1])/10**6
        elif line.startswith('Fidelity:'):
            all_records[idx]['fidelity'] = float(line.split(' ')[-1])
        elif line.startswith('Gatetype:'):
            all_records[idx]['gate_type'] = line.split(' ')[-1]
        elif line.startswith('Swaptype:'):
            all_records[idx]['swap_type'] = line.split(' ')[-1]
        elif "HeatingSum:" in line:
            all_records[idx]['heat_max'] = int(line.split(' ')[1])
        elif line.startswith('Mapper'):
            all_records[idx]['mapper'] = line.split(' ')[-1]
        elif line.startswith('SplitSWAP'):
            all_records[idx]['swap_count'] = int(line.split(' ')[-1])
        elif line.startswith("OPCOUNTS"):
            all_records[idx]['split_count'] = int(line.split()[4])
    rand_vals = []
    po_vals = []
    lpfs_vals = []
    greedy_vals = []
    agg_vals = []
    for idx in all_records:
        if not app_name in all_records[idx]['program']:
            continue

        #print(all_records[idx]['mapper'], all_records[idx]['ions'], all_records[idx][metric])
        if all_records[idx]['mapper'] == "Random":
            rand_vals.append(all_records[idx][metric])
        elif all_records[idx]['mapper'] == "PO":
            po_vals.append(all_records[idx][metric])
        elif all_records[idx]['mapper'] == "LPFS":
            lpfs_vals.append(all_records[idx][metric])
        elif all_records[idx]['mapper'] == "Greedy":
            greedy_vals.append(all_records[idx][metric])
        elif all_records[idx]['mapper'] == "Agg":
            if metric not in all_records[idx]:
                continue
            agg_vals.append(all_records[idx][metric])

    print(app_name)
    print(np.mean(rand_vals))
    print(np.mean(po_vals))
    print(np.mean(lpfs_vals))
    print(np.mean(greedy_vals))
    print(np.mean(agg_vals))

#plt_compiler_validate("R1_CompilerTestv2.log", "junk", "qft64.qasm", "split_count")
#print("")
#plt_compiler_validate("R1_CompilerTestv2.log", "junk", "sup64.qasm", "split_count")
#print("")
#plt_compiler_validate("R1_CompilerTestv2.log", "junk", "square_root_clean.qasm", "split_count")
#print("")
#plt_compiler_validate("R1_CompilerTestv2.log", "junk", "qaoa6420.qasm", "split_count")
