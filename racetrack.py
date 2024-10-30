import racetrack_params

execution_window=racetrack_params.execution_window

last_reg=0

v1_counter=0
v2_counter=0

rt_v1_energy=0
rt_v2_energy=0

num_access_ports=racetrack_params.nap

def reset():
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

    #simulate store and restore overhead, basically one shift of all nanotracks to the next access head
    migrate_ov=((racetrack_params.W/num_access_ports)-1)*racetrack_params.N*2
    v1_counter+=migrate_ov
    v2_counter+=migrate_ov


def get_version_counters():
    return v1_counter, v2_counter

def next_access(next_reg):
    global last_reg

    global v1_counter
    global v2_counter
    
    #V1: horizontal allocation
    v1_counter+=int( (64/num_access_ports) -1 )*2
    #V2 vertical allocation
    v2_counter+= abs( int( (next_reg*64) / (racetrack_params.N*num_access_ports) )- int( (last_reg*64) / (racetrack_params.N*num_access_ports) ) )*racetrack_params.N

    last_reg=next_reg

    #update energy and latency?

#parameters
Es=10
Ed=10
Ei=10
Er=10
Regwidth=32

def read_raceteack_reg(reg_nr):
    global rt_v1_energy
    global rt_v2_energy

    rt_v1_energy+=Regwidth*Ed
    rt_v2_energy+=Regwidth*Ed
def write_raceteack_reg(reg_nr, old_value, new_value):
    global rt_v1_energy
    global rt_v2_energy

    new_num_bits=int.bit_count(new_value)
    old_num_bits=int.bit_count(old_value)

    k=0
    j=0
    if new_num_bits>old_num_bits:
        k=new_num_bits-old_num_bits
    else:
        j=old_num_bits-new_num_bits

    rt_v1_energy+=Regwidth*Ed+k*Ei+j*(Er+Es)
    rt_v2_energy+=Regwidth*Ed + new_num_bits*Ei
def get_rw_energy():
    global rt_v1_energy
    global rt_v2_energy
    return rt_v1_energy, rt_v2_energy

def get_total_energy():
    global rt_v1_energy
    global rt_v2_energy

    global v1_counter
    global v2_counter

    total_v1_energy=rt_v1_energy+v1_counter*Es*num_access_ports
    total_v2_energy=rt_v2_energy+v2_counter*Es*num_access_ports