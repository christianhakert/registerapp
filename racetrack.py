import racetrack_params

execution_window=racetrack_params.execution_window

last_reg=0

v1_counter=0
v2_counter=0

rt_v1_energy=0
rt_v2_energy=0

rt_v1_latency=0
rt_v2_latency=0

migrate_shifts=0
migrate_energy=0
migrate_latency=0

migrate_opt_shifts=0
migrate_opt_energy=0
migrate_opt_latency=0

num_access_ports=racetrack_params.nap

#parameters
Es=20
Ed=2
Ei=200
Er=20
Regwidth=32
Numregs=64

Ls=0.5
Ld=0.1
Li=1
Lr=0.8

def reset(migrate_from="V1",migrate_to="V2",migrate_opt_from="V1",migrate_opt_to="V2"):
    global last_reg
    last_reg=0
    global v1_counter
    global v2_counter
    v1_counter=0
    v2_counter=0

    global rt_v1_energy
    global rt_v2_energy
    rt_v1_energy=0
    rt_v2_energy=0

    global rt_v1_latency
    global rt_v2_latency

    rt_v1_latency=0
    rt_v2_latency=0

    global migrate_shifts
    global migrate_energy
    global migrate_latency

    migrate_shifts=0
    migrate_energy=0
    migrate_latency=0

    global migrate_opt_shifts
    global migrate_opt_energy
    global migrate_opt_latency

    migrate_opt_shifts=0
    migrate_opt_energy=0
    migrate_opt_latency=0

    #simulate overhead for migration: reading old registers
    prev_reg=0
    for i in range(Numregs):
        tmp_v1_counter,tmp_v2_counter=next_access(i,local_last_reg=prev_reg,add_to_global=False)
        tmp_v1_energy,tmp_v2_energy,tmp_v1_latency,tmp_v2_latency=read_raceteack_reg(i,add_to_global=False)
        if migrate_from=="V1":
            migrate_energy+=tmp_v1_energy
            migrate_latency+=tmp_v1_latency
            migrate_shifts+=tmp_v1_counter
        else:
            migrate_energy+=tmp_v2_energy
            migrate_latency+=tmp_v2_latency
            migrate_shifts+=tmp_v2_counter
        if migrate_opt_from=="V1":
            migrate_opt_energy+=tmp_v1_energy
            migrate_opt_latency+=tmp_v1_latency
            migrate_opt_shifts+=tmp_v1_counter
        else:
            migrate_opt_energy+=tmp_v2_energy
            migrate_opt_latency+=tmp_v2_latency
            migrate_opt_shifts+=tmp_v2_counter

    #simulate restore of registers
    prev_reg=0
    for i in range(Numregs):
        tmp_v1_counter,tmp_v2_counter=next_access(i,local_last_reg=prev_reg,add_to_global=False)
        tmp_v1_energy,tmp_v2_energy,tmp_v1_latency,tmp_v2_latency=write_raceteack_reg(i,old_value=0x00000000,new_value=0xFFFFFFFF,add_to_global=False)
        if migrate_to=="V1":
            migrate_energy+=tmp_v1_energy
            migrate_latency+=tmp_v1_latency
            migrate_shifts+=tmp_v1_counter
        else:
            migrate_energy+=tmp_v2_energy
            migrate_latency+=tmp_v2_latency
            migrate_shifts+=tmp_v2_counter
        if migrate_opt_to=="V1":
            migrate_opt_energy+=tmp_v1_energy
            migrate_opt_latency+=tmp_v1_latency
            migrate_opt_shifts+=tmp_v1_counter
        else:
            migrate_opt_energy+=tmp_v2_energy
            migrate_opt_latency+=tmp_v2_latency
            migrate_opt_shifts+=tmp_v2_counter


def get_version_counters():
    return v1_counter, v2_counter

def get_migration_counters():
    global migrate_shifts
    global migrate_energy
    global migrate_latency
    return migrate_shifts, migrate_energy, migrate_latency

def get_migration_opt_counters():
    global migrate_opt_shifts
    global migrate_opt_energy
    global migrate_opt_latency
    return migrate_opt_shifts, migrate_opt_energy, migrate_opt_latency

def next_access(next_reg, local_last_reg=None, add_to_global=True):
    global last_reg

    if local_last_reg is None:
        local_last_reg=last_reg
    
    #V1: horizontal allocation
    tmp_v1_counter=int( (64/num_access_ports) -1 )*2
    #V2 vertical allocation
    tmp_v2_counter= abs( int( (next_reg*64) / (racetrack_params.N*num_access_ports) )- int( (local_last_reg*64) / (racetrack_params.N*num_access_ports) ) )*racetrack_params.N

    if add_to_global:
        global v1_counter
        global v2_counter
        v1_counter+=tmp_v1_counter
        v2_counter+=tmp_v2_counter

        last_reg=next_reg

    return tmp_v1_counter, tmp_v2_counter

def read_raceteack_reg(reg_nr, add_to_global=True):
    tmp_v1_energy =Regwidth*Ed
    tmp_v2_energy =Regwidth*Ed

    tmp_v1_latency = Regwidth*Ld
    tmp_v2_latency = Ld

    if add_to_global:
        global rt_v1_energy
        global rt_v2_energy

        rt_v1_energy += tmp_v1_energy
        rt_v2_energy += tmp_v2_energy

        global rt_v1_latency
        global rt_v2_latency

        rt_v1_latency += tmp_v1_latency
        rt_v2_latency += tmp_v2_latency

    return tmp_v1_energy, tmp_v2_energy, tmp_v1_latency, tmp_v2_latency


def write_raceteack_reg(reg_nr, old_value, new_value, add_to_global=True):
    new_num_bits=int.bit_count(new_value)
    old_num_bits=int.bit_count(old_value)

    k=0
    j=0
    if new_num_bits>old_num_bits:
        k=new_num_bits-old_num_bits
    else:
        j=old_num_bits-new_num_bits

    tmp_v1_energy =Regwidth*Ed+k*Ei+j*(Er+Es)
    tmp_v2_energy =Regwidth*Ed + new_num_bits*Er

    tmp_v1_latency = Regwidth*Ld + k*Li + j*(Lr+Ls)
    tmp_v2_latency = Lr + Li

    if add_to_global:
        global rt_v1_energy
        global rt_v2_energy

        rt_v1_energy += tmp_v1_energy
        rt_v2_energy += tmp_v2_energy

        global rt_v1_latency
        global rt_v2_latency

        rt_v1_latency += tmp_v1_latency
        rt_v2_latency += tmp_v2_latency

    return tmp_v1_energy, tmp_v2_energy, tmp_v1_latency, tmp_v2_latency

def get_rw_energy():
    global rt_v1_energy
    global rt_v2_energy
    return rt_v1_energy, rt_v2_energy

def get_rw_latency():
    global rt_v1_latency
    global rt_v2_latency
    return rt_v1_latency, rt_v2_latency

def get_total_energy():
    global rt_v1_energy
    global rt_v2_energy

    global v1_counter
    global v2_counter

    total_v1_energy=rt_v1_energy+v1_counter*Es*num_access_ports
    total_v2_energy=rt_v2_energy+v2_counter*Es*num_access_ports

    return total_v1_energy, total_v2_energy

def get_total_latency():
    global rt_v1_latency
    global rt_v2_latency

    global v1_counter
    global v2_counter

    total_v1_latency=rt_v1_latency+v1_counter*Ls
    total_v2_latency=rt_v2_latency+v2_counter*Ls

    return total_v1_latency, total_v2_latency