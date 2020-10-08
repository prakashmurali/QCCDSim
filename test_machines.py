from machine import Machine, Trap, Segment, MachineParams

#ISCA Test machines Begin
def test_trap_2x3(capacity, mparams):
    m = Machine(mparams)
    t = [m.add_trap(i, capacity) for i in range(6)]
    j = [m.add_junction(i) for i in range(3)]
    m.add_segment(0, t[0], j[0], 'R')
    m.add_segment(1, t[1], j[1], 'R')
    m.add_segment(2, t[2], j[2], 'R')
    m.add_segment(3, t[3], j[2], 'L')
    m.add_segment(4, t[4], j[1], 'L')
    m.add_segment(5, t[5], j[0], 'L')
    m.add_segment(6, j[0], j[1])
    m.add_segment(6, j[1], j[2])
    return m

def make_linear_machine(zones, capacity, mparams):
    m = Machine(mparams)
    traps = []
    junctions = []
    for i in range(zones):
        traps.append(m.add_trap(i, capacity))
    for i in range(zones-1):
        junctions.append(m.add_junction(i))
    for i in range(zones-1):
        m.add_segment(2*i,   traps[i], junctions[i], 'R') #t_i ---- j_i ---- t_i+1
        m.add_segment(2*i+1, traps[i+1], junctions[i], 'L')
    return m

def make_single_hexagon_machine(capacity, mparams):
    m = Machine(mparams)
    t = [m.add_trap(i, capacity) for i in range(6)]
    j = [m.add_junction(i) for i in range(6)]
    m.add_segment(0, t[0], j[0], 'R')
    m.add_segment(1, t[1], j[1], 'R')
    m.add_segment(2, t[2], j[2], 'R')
    m.add_segment(3, t[3], j[3], 'R')
    m.add_segment(4, t[4], j[4], 'R')
    m.add_segment(5, t[5], j[5], 'R')
    m.add_segment(6, t[0], j[5], 'L')
    m.add_segment(7, t[1], j[0], 'L')
    m.add_segment(8, t[2], j[1], 'L')
    m.add_segment(9, t[3], j[2], 'L')
    m.add_segment(10, t[4], j[3], 'L')
    m.add_segment(11, t[5], j[4], 'L')
    return m

#ISCA Test machines End

def mktrap4x2(capacity):
    m = Machine()
    t0 = m.add_trap(0, capacity)
    t1 = m.add_trap(1, capacity)
    t2 = m.add_trap(2, capacity)
    t3 = m.add_trap(3, capacity)
    j0 = m.add_junction(0)
    j1 = m.add_junction(1)
    m.add_segment(0, t0, j0)
    m.add_segment(1, t1, j0)
    m.add_segment(2, t2, j1)
    m.add_segment(3, t3, j1)
    m.add_segment(4, j0, j1)
    return m

def mktrap_4star(capacity):
    m = Machine()
    t0 = m.add_trap(0, capacity)
    t1 = m.add_trap(1, capacity)
    t2 = m.add_trap(2, capacity)
    t3 = m.add_trap(3, capacity)
    j0 = m.add_junction(0)
    m.add_segment(0, t0, j0)
    m.add_segment(1, t1, j0)
    m.add_segment(2, t2, j0)
    m.add_segment(3, t3, j0)
    return m

def mktrap6x3(capacity):
    m = Machine()
    t0 = m.add_trap(0, capacity)
    t1 = m.add_trap(1, capacity)
    t2 = m.add_trap(2, capacity)
    t3 = m.add_trap(3, capacity)
    t4 = m.add_trap(4, capacity)
    t5 = m.add_trap(5, capacity)
    j0 = m.add_junction(0)
    j1 = m.add_junction(1)
    j2 = m.add_junction(2)
    m.add_segment(0, t0, j0)
    m.add_segment(1, t1, j0)
    m.add_segment(2, t2, j1)
    m.add_segment(3, t3, j1)
    m.add_segment(4, t4, j2)
    m.add_segment(5, t5, j2)
    m.add_segment(6, j0, j1)
    m.add_segment(7, j1, j2)
    return m

def mktrap8x4(capacity):
    m = Machine()
    t0 = m.add_trap(0, capacity)
    t1 = m.add_trap(1, capacity)
    t2 = m.add_trap(2, capacity)
    t3 = m.add_trap(3, capacity)
    t4 = m.add_trap(4, capacity)
    t5 = m.add_trap(5, capacity)
    t6 = m.add_trap(6, capacity)
    t7 = m.add_trap(7, capacity)

    j0 = m.add_junction(0)
    j1 = m.add_junction(1)
    j2 = m.add_junction(2)
    j3 = m.add_junction(3)

    m.add_segment(0, t0, j0)
    m.add_segment(1, t1, j0)
    m.add_segment(2, t2, j1)
    m.add_segment(3, t3, j1)
    m.add_segment(4, t4, j2)
    m.add_segment(5, t5, j2)
    m.add_segment(6, t6, j3)
    m.add_segment(7, t7, j3)

    m.add_segment(8, j0, j1)
    m.add_segment(9, j1, j2)
    m.add_segment(10, j2, j3)
    return m



def make_3x3_grid(capacity):
    m = Machine()
    t = [m.add_trap(i, capacity) for i in range(9)]
    j = [m.add_junction(i) for i in range(6)]
    m.add_segment(0, t[0], j[0])
    m.add_segment(1, t[1], j[1])
    m.add_segment(2, t[2], j[2])
    m.add_segment(3, t[3], j[3])
    m.add_segment(4, t[4], j[4])
    m.add_segment(5, t[5], j[5])
    m.add_segment(6, t[3], j[0])
    m.add_segment(7, t[4], j[1])
    m.add_segment(8, t[5], j[2])
    m.add_segment(9,  t[6], j[3])
    m.add_segment(10, t[7], j[4])
    m.add_segment(11, t[8], j[5])
    m.add_segment(12, j[0], j[1])
    m.add_segment(13, j[1], j[2])
    m.add_segment(14, j[3], j[4])
    m.add_segment(15, j[4], j[5])
    return m

def make_9trap(capacity):
    m = Machine(alpha=0.005, inter_ion_dist=1, split_factor=5.0, move_factor=1.0)
    t = [m.add_trap(i, capacity) for i in range(9)]
    j = [m.add_junction(i) for i in range(9)]

    m.add_segment(0, t[0], j[0])
    m.add_segment(1, t[1], j[1])
    m.add_segment(2, t[2], j[2])

    m.add_segment(3, t[3], j[2])
    m.add_segment(4, t[4], j[5])
    m.add_segment(5, t[5], j[8])

    m.add_segment(6, t[6], j[8])
    m.add_segment(7, t[7], j[7])
    m.add_segment(8, t[8], j[6])

    m.add_segment(9, j[0], j[1])
    m.add_segment(10, j[0], j[3])
    m.add_segment(11, j[3], j[6])
    m.add_segment(12, j[3], j[4])
    m.add_segment(13, j[6], j[7])
    m.add_segment(14, j[1], j[4])
    m.add_segment(15, j[1], j[2])
    m.add_segment(16, j[4], j[7])
    m.add_segment(17, j[4], j[5])
    m.add_segment(18, j[7], j[8])
    m.add_segment(19, j[2], j[5])
    m.add_segment(20, j[5], j[8])
    return m
