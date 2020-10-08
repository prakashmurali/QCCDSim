import subprocess as sp
import os

PROG=["programs/bv64.qasm"]

output_file = open('output.log','w')

MACHINE=["L6"]

IONS = []
for i in range(14, 35, 2):
    IONS.append(str(i))
print(IONS)

mapper = "Greedy"
reorder = "Naive"
  
for p in PROG:
    for m in MACHINE:
        for i in IONS:
           sp.call(["python", "run.py", p, m, i, mapper, reorder, "1", "0", "0", "FM", "GateSwap"], stdout=output_file)
