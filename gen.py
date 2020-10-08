from qcg.generators import gen_uccsd, gen_hwea, gen_qwalk, gen_supremacy, gen_BV, gen_adder

#circ = gen_BV(secret = "1111111111111111111111111111111111111111111111111111111111111111")
#print(circ.qasm())

circ = gen_adder(nbits=32)
print(circ.qasm())
#sup = gen_supremacy(8, 8, 40, order=None, singlegates=False, mirror=True, barriers=False, measure=False, regname=None)

#print(sup.qasm())

#vqe_5 = gen_uccsd(5, seed=1, barriers=False, regname=None)
#print(vqe_5.count_ops())
#print(vqe_5)

#hwea = gen_hwea(6, 3, parameters='optimal', seed=1234)
#print(hwea.count_ops())
#print(hwea.qasm())
#print(hwea)
