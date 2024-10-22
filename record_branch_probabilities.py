import racetrack

#get runname as input
import sys
import re

runname=sys.argv[1]

#Read first and last address of main from the main.txt
mainfile=open("main.txt","r")
first_address=int(mainfile.readline().strip(),16)
max_address=int(mainfile.readline().strip(),16)
mainfile.close()

branch_targets={}

analyze_limit=1000000

#Iterate over the tracefile and record branch targets
tracefile=open(runname+".csv","r")

skip_first_line=True

evaluate=False

found_branch=None

linecounter=0

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

        #clean up mnemonic
        mneomonic=mneomonic.replace(" ","")

        if instr_address==first_address:
            evaluate=True
            # print("First address reached, disassembly: "+disassembly)

        if instr_address==max_address:
            # print("Last address reached, stopping")
            break

        if evaluate==False:
            continue

        linecounter+=1

        if linecounter>analyze_limit:
            break

        #Check if the current instruction is a branch
        if found_branch is not None:
            btarget=instr_address
            if found_branch not in branch_targets:
                branch_targets[found_branch]={}
            if btarget not in branch_targets[found_branch]:
                branch_targets[found_branch][btarget]=0
                
            branch_targets[found_branch][btarget]+=1

            found_branch=None
        if re.match("b.*", mneomonic) != None or re.match("ret", mneomonic) != None:
            # print("Found branch "+mneomonic)
            found_branch=instr_address

#normalize distribution in branch targets
for branch in branch_targets:
    total=0
    for target in branch_targets[branch]:
        total+=branch_targets[branch][target]
    for target in branch_targets[branch]:
        branch_targets[branch][target]=branch_targets[branch][target]/total

#export branch targets as pickle
import pickle

pickle.dump(branch_targets, open("branch_targets.p", "wb"))

#also export as reafable csv
branch_targets_file=open("branch_targets.csv","w")
branch_targets_file.write("Branch,Target,Probability\n")
for branch in branch_targets:
    for target in branch_targets[branch]:
        branch_targets_file.write(hex(branch)+","+hex(target)+","+str(branch_targets[branch][target])+"\n")
branch_targets_file.close()
        
tracefile.close()