import subprocess as sp
import os

PROG=["programs/bv64_cut.qasm"]

output_file = open('output.log','w')

MACHINE=["L6"]

IONS = ["14"]
# for i in range(14, 35, 2):
#     IONS.append(str(i))
# print(IONS)

mapper = "Greedy"
reorder = "Naive"
  
for p in PROG:
    for m in MACHINE:
        for i in IONS:
           sp.call(["python", "run.py", p, m, i, mapper, reorder, "1", "0", "0", "FM", "GateSwap"], stdout=output_file)
