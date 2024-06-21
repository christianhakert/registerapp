import racetrack


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
        recmap[int(parts[0],16)] = 1 if parts[1]<parts[2] else 2
rstatsfile.close()

#Now irerare over the trace until the first address is reached
tracefile=open("regtrace.csv","r")

resultfile=open("shiftresults.csv","w")

skip_first_line=True
evaluate=False

curr_blk_start=first_address
curr_blk_len=0

v1_total_shifts=0
v2_total_shifts=0
opt_total_shifts=0
recommended_total_shifts=0

for line in tracefile:
    line=line.strip()
    if line:

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

        if instr_address==first_address:
            evaluate=True
            print("First address reached, disassembly: "+disassembly)

        if instr_address==max_address:
            print("Last address reached, stopping")
            break

        if evaluate==False:
            continue

        if curr_blk_len==racetrack.execution_window:
            #get the results from racetrack versions
            v1_counter,v2_counter=racetrack.get_version_counters()

            v1_total_shifts+=v1_counter
            v2_total_shifts+=v2_counter
            opt_total_shifts+=min(v1_counter,v2_counter)

            #Write block statistics to results file
            resultfile.write(hex(curr_blk_start)+","+str(v1_counter)+","+str(v2_counter))
            if curr_blk_start in recmap:
                resultfile.write(","+str(recmap[curr_blk_start]))
                recommended_total_shifts+=v1_counter if recmap[curr_blk_start]==1 else v2_counter
            else:
                resultfile.write(",0")
                recommended_total_shifts+=v2_counter
            resultfile.write("\n")

            resultfile.flush()
            #reset the counters
            racetrack.reset()
            curr_blk_start=instr_address
            curr_blk_len=0

            print(str(v1_total_shifts)+","+str(v2_total_shifts)+","+str(opt_total_shifts)+","+str(recommended_total_shifts))
        else:
            curr_blk_len+=1
            if type_sr1==" integer" and sr1 < 32:
                racetrack.next_access(sr1)
            if type_sr2==" integer" and sr2 < 32:
                racetrack.next_access(sr2)
            if type_sr3==" integer" and sr3 < 32:
                racetrack.next_access(sr3)
            if type_dr1==" integer" and dr1 < 32:
                racetrack.next_access(dr1)
            if type_dr2==" integer" and dr2 < 32:
                racetrack.next_access(dr2)
            if type_dr3==" integer" and dr3 < 32:
                racetrack.next_access(dr3)
            
#When the file is ended, write the last block statistics

v1_counter,v2_counter=racetrack.get_version_counters()
resultfile.write(hex(curr_blk_start)+","+str(v1_counter)+","+str(v2_counter))
if curr_blk_start in recmap:
    resultfile.write(","+str(recmap[curr_blk_start]))
else:
    resultfile.write(",0")
resultfile.write("\n")
        
tracefile.close()

resultfile.close()