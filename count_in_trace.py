
#read csv file from first argument

import sys
import csv

tracefilename=sys.argv[1]

tracefile=open(tracefilename,"r")

skip_first_line=True

count_num_read_regs=0
count_num_write_regs=0

for line in tracefile:
    line=line.strip()
    if line:

        # print(line)

        if skip_first_line:
            skip_first_line=False
            continue

        parts=line.split(",")
        num_src_regs=int(parts[2])
        num_dst_regs=int(parts[3])


        count_num_read_regs+=num_src_regs
        count_num_write_regs+=num_dst_regs

print("Number of read registers: "+str(count_num_read_regs))
print("Number of write registers: "+str(count_num_write_regs))

tracefile.close()