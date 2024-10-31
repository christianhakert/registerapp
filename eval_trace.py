import racetrack

#get runname as input
import sys

runname=sys.argv[1]

recmap={}



#Read first and last address of main from the main.txt
mainfile=open("main.txt","r")
first_address=int(mainfile.readline().strip(),16)
max_address=int(mainfile.readline().strip(),16)
mainfile.close()

#read the recommendations file and build a map
rstatsfile=open("rtstats.csv","r")
skip_first_line=True
for line in rstatsfile:
    line=line.strip()
    if line:
        if skip_first_line:
            skip_first_line=False
            continue
        parts=line.split(",")
        recmap[int(parts[0],16)] = 1 if float(parts[1])<float(parts[2]) else 2
rstatsfile.close()

#Now irerare over the trace until the first address is reached
tracefile=open(runname+".csv","r")

resultfile=open("shiftresults.csv","w")

skip_first_line=True
evaluate=False

curr_blk_start=first_address
curr_blk_len=0

v1_total_shifts=0
v2_total_shifts=0
opt_total_shifts=0
recommended_total_shifts=0

v1_total_energy=0
v2_total_energy=0
opt_total_energy=0
recommended_total_energy=0

v1_total_latency=0
v2_total_latency=0
opt_total_latency=0
recommended_total_latency=0

last_rec=1

last_alloc="V1"
last_opt_alloc="V1"

for line in tracefile:
    line=line.strip()
    if line:

        # print(line)

        if skip_first_line:
            skip_first_line=False
            continue

        parts=line.split(",")
        instr_address=int(parts[0],16)
        instr_address=instr_address+0x400000
        mneomonic=parts[1]
        num_src_regs=int(parts[2])
        num_dst_regs=int(parts[3])
        type_sr1=parts[4]
        sr1=int(parts[5])
        type_sr2=parts[6]
        sr2=int(parts[7])
        type_sr3=parts[8]
        sr3=int(parts[9])
        type_dr1=parts[10]
        dr1=int(parts[11])
        type_dr2=parts[12]
        dr2=int(parts[13])
        type_dr3=parts[14]
        dr3=int(parts[15])
        disassembly=parts[16]
        prev_cnt_sr1=int(parts[17],16)
        prev_cnt_sr2=int(parts[18],16)
        prev_cnt_sr3=int(parts[19],16)
        prev_cnt_dr1=int(parts[20],16)
        prev_cnt_dr2=int(parts[21],16)
        prev_cnt_dr3=int(parts[22],16)
        new_cnt_sr1=int(parts[23],16)
        new_cnt_sr2=int(parts[24],16)
        new_cnt_sr3=int(parts[25],16)
        new_cnt_dr1=int(parts[26],16)
        new_cnt_dr2=int(parts[27],16)
        new_cnt_dr3=int(parts[28],16)

        if instr_address not in recmap:
            continue

        if instr_address==first_address:
            evaluate=True
            # print("First address reached, disassembly: "+disassembly)

        if instr_address==max_address:
            # print("Last address reached, stopping")
            break

        if evaluate==False:
            continue

        new_alloc=None
        new_opt_alloc=None

        if curr_blk_len==racetrack.execution_window:
            #get the results from racetrack versions
            v1_counter,v2_counter=racetrack.get_version_counters()
            v1_en_counter,v2_en_counter=racetrack.get_total_energy()
            v1_lt_counter,v2_lt_counter=racetrack.get_total_latency()

            v1_total_shifts+=v1_counter
            v2_total_shifts+=v2_counter
            opt_total_shifts+=min(v1_counter,v2_counter)

            v1_total_energy+=v1_en_counter
            v2_total_energy+=v2_en_counter
            opt_total_energy+=v1_en_counter if v1_counter<v2_counter else v2_en_counter

            v1_total_latency+=v1_lt_counter
            v2_total_latency+=v2_lt_counter
            opt_total_latency+=v1_lt_counter if v1_counter<v2_counter else v2_lt_counter

            new_opt_alloc="V1" if v1_counter<v2_counter else "V2"

            migrate_shifts,migrate_energy,migrate_latency=racetrack.get_migration_counters()
            recommended_total_shifts+=migrate_shifts
            recommended_total_energy+=migrate_energy
            recommended_total_latency+=migrate_latency

            migrate_opt_shifts,migrate_opt_energy,migrate_opt_latency=racetrack.get_migration_opt_counters()
            opt_total_shifts+=migrate_opt_shifts
            opt_total_energy+=migrate_opt_energy
            opt_total_latency+=migrate_opt_latency

            #Write block statistics to results file
            resultfile.write(hex(curr_blk_start)+","+str(v1_counter)+","+str(v2_counter))
            if curr_blk_start in recmap:
                last_rec=recmap[curr_blk_start]
                resultfile.write(","+str(recmap[curr_blk_start]))
                recommended_total_shifts+=v1_counter if recmap[curr_blk_start]==1 else v2_counter
                recommended_total_energy+=v1_en_counter if recmap[curr_blk_start]==1 else v2_en_counter
                recommended_total_latency+=v1_lt_counter if recmap[curr_blk_start]==1 else v2_lt_counter
                new_alloc="V1" if recmap[curr_blk_start]==1 else "V2"
            else:
                resultfile.write(",0")
                # recommended_total_shifts+=v2_counter
                recommended_total_shifts+=v1_counter if last_rec==1 else v2_counter
                recommended_total_energy+=v1_en_counter if last_rec==1 else v2_en_counter
                recommended_total_latency+=v1_lt_counter if last_rec==1 else v2_lt_counter
                new_alloc="V1" if last_rec==1 else "V2"
            resultfile.write("\n")

            resultfile.flush()
            #reset the counters
            racetrack.reset(last_alloc,new_alloc,last_opt_alloc,new_opt_alloc)
            last_alloc=new_alloc
            last_opt_alloc=new_opt_alloc
            curr_blk_start=instr_address
            curr_blk_len=0

            # print(str(v1_total_shifts)+","+str(v2_total_shifts)+","+str(opt_total_shifts)+","+str(recommended_total_shifts)+ ","+str(racetrack.get_energy()))
        
        curr_blk_len+=1
        if type_sr1==" integer" and sr1 < 32:
            racetrack.next_access(sr1)
        if type_sr2==" integer" and sr2 < 32:
            racetrack.next_access(sr2)
        if type_sr3==" integer" and sr3 < 32:
            racetrack.next_access(sr3)
        if type_dr1==" integer" and dr1 < 32:
            racetrack.next_access(dr1, is_write=True)
        if type_dr2==" integer" and dr2 < 32:
            racetrack.next_access(dr2, is_write=True)
        if type_dr3==" integer" and dr3 < 32:
            racetrack.next_access(dr3, is_write=True)

        #process bit statistics
        if type_sr1==" integer" and sr1 < 32:
            racetrack.read_raceteack_reg(sr1)
        if type_sr2==" integer" and sr2 < 32:
            racetrack.read_raceteack_reg(sr2)
        if type_sr3==" integer" and sr3 < 32:
            racetrack.read_raceteack_reg(sr3)
        
        if type_dr1==" integer" and dr1 < 32:
            racetrack.write_raceteack_reg(dr1,prev_cnt_dr1,new_cnt_dr1)
        if type_dr2==" integer" and dr2 < 32:
            racetrack.write_raceteack_reg(dr2,prev_cnt_dr2,new_cnt_dr2)
        if type_dr3==" integer" and dr3 < 32:
            racetrack.write_raceteack_reg(dr3,prev_cnt_dr3,new_cnt_dr3)
            
#When the file is ended, write the last block statistics

v1_counter,v2_counter=racetrack.get_version_counters()
v1_en_counter,v2_en_counter=racetrack.get_total_energy()
v1_lt_counter,v2_lt_counter=racetrack.get_total_latency()

v1_total_shifts+=v1_counter
v2_total_shifts+=v2_counter
opt_total_shifts+=min(v1_counter,v2_counter)

v1_total_energy+=v1_en_counter
v2_total_energy+=v2_en_counter
opt_total_energy+=v1_en_counter if v1_counter<v2_counter else v2_en_counter

v1_total_latency+=v1_lt_counter
v2_total_latency+=v2_lt_counter
opt_total_latency+=v1_lt_counter if v1_counter<v2_counter else v2_lt_counter

migrate_shifts,migrate_energy,migrate_latency=racetrack.get_migration_counters()
recommended_total_shifts+=migrate_shifts
recommended_total_energy+=migrate_energy
recommended_total_latency+=migrate_latency

migrate_opt_shifts,migrate_opt_energy,migrate_opt_latency=racetrack.get_migration_opt_counters()
opt_total_shifts+=migrate_opt_shifts
opt_total_energy+=migrate_opt_energy
opt_total_latency+=migrate_opt_latency

resultfile.write(hex(curr_blk_start)+","+str(v1_counter)+","+str(v2_counter))
if curr_blk_start in recmap:
    resultfile.write(","+str(recmap[curr_blk_start]))
    recommended_total_shifts+=v1_counter if recmap[curr_blk_start]==1 else v2_counter
    recommended_total_energy+=v1_en_counter if recmap[curr_blk_start]==1 else v2_en_counter
    recommended_total_latency+=v1_lt_counter if recmap[curr_blk_start]==1 else v2_lt_counter
else:
    resultfile.write(",0")
    recommended_total_shifts+=v1_counter if last_rec==1 else v2_counter
    recommended_total_energy+=v1_en_counter if last_rec==1 else v2_en_counter
    recommended_total_latency+=v1_lt_counter if last_rec==1 else v2_lt_counter
resultfile.write("\n")
        
tracefile.close()

resultfile.close()

print(str(v1_total_shifts)+","+str(v2_total_shifts)+","+str(opt_total_shifts)+","+str(recommended_total_shifts)+ ","+str(v1_total_energy)+","+str(v2_total_energy)+","+str(opt_total_energy)+","+str(recommended_total_energy)+","+str(v1_total_latency)+","+str(v2_total_latency)+","+str(opt_total_latency)+","+str(recommended_total_latency))