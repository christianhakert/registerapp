execution_window=100

last_reg=0

v1_counter=0
v2_counter=0

rt_energy=0

num_access_ports=2

def reset():
    global last_reg
    last_reg=0
    global v1_counter
    global v2_counter
    v1_counter=0
    v2_counter=0

def get_version_counters():
    return v1_counter, v2_counter

def next_access(next_reg):
    global last_reg

    global v1_counter
    global v2_counter
    
    #V1: Each register is a nanotrack
    v1_counter+=int((64*2)/num_access_ports)
    # v1_counter+=32
    #V2 each register is a position in all nanotracks
    # v2_counter+=(64*abs(next_reg-last_reg))
    # v2_counter+=int(abs(next_reg-last_reg)/num_access_ports)*64
    v2_counter+=abs( int(2*next_reg/(num_access_ports)) - int(2*last_reg/(num_access_ports))  )*64

    last_reg=next_reg

def read_raceteack_reg(reg_nr):
    global rt_energy
    rt_energy+=20*64
def write_raceteack_reg(reg_nr, old_value, new_value):
    global rt_energy
    num_insert_bits=int.bit_count(new_value& (~old_value))
    num_delete_bits=int.bit_count((~new_value)& old_value)

    rt_energy+=num_insert_bits*200
    rt_energy+=num_delete_bits*20
def get_energy():
    global rt_energy
    return rt_energy