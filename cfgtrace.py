#This tool uses gdb calls to build up a control flow graph and analyze source and destination registers

import subprocess
import sys
import re
import os

import racetrack

filename = sys.argv[1]

text_start = 0
text_end = 0

def is_in_text(addr):

    global text_start
    global text_end

    if text_start == 0 and text_end == 0:
        result=subprocess.check_output("size -x -A "+filename+" | grep .text", shell=True)
        result = result.decode("utf-8")
        linematch=re.findall("0x[0-9a-f]*",result)
        start=linematch[0]
        size=linematch[1]

        text_start=int(start, 16)
        text_end=int(start,16)+int(size,16)


    return int(addr,16) >= text_start and int(addr,16) <= text_end

def query_gdb(sect):
    result = ""
    try:
        result = subprocess.check_output("gdb -batch -ex 'disas "+sect+",+1' "+filename, shell=True)
    except subprocess.CalledProcessError as e:
        return None
    #convert result to string
    result = result.decode("utf-8")
    linematch=re.search("0x[0-9a-fA-F]*( <[^<>]*>)?:[^\n]+", str(result))
    linematch=linematch.group()
    linematch=linematch.replace("\n","")
    return(str(linematch))

def split_gdb_line(line):
    linematch=re.match("(0x[0-9a-fA-F]*)( <[^<>]*>)?:(.*)", str(line))
    return linematch.group(1),linematch.group(2),linematch.group(3)

def label_to_address(label):
    gdb_o=query_gdb(label)
    if(gdb_o == None):
        return None
    addr,lab,insn=split_gdb_line(gdb_o)
    return addr

class Instruction:
    address = 0
    disassembly = ""
    mnemonic = ""
    src_regs=[]
    dst_regs=[]
    recommendation_miss=0

    def __init__(self, addr):
        self.address = addr
        gdb_s=query_gdb(addr)
        naddr,lab,insn=split_gdb_line(gdb_s)
        self.disassembly = insn.replace("\t"," ")
        self.parse_disassembly()

    def parse_disassembly(self):
        #parse the disassembly to get the source and destination registers
        linematch=re.match(" *([a-z\.]*)", self.disassembly)
        self.mnemonic=linematch.group(1).replace(" ","")

        #get registers
        linematch=re.findall("[^0]([xwd][0-9]+)", self.disassembly)
        #Unless the instruction is not a load or store, the first register is the destination
        num_dest_regs=1
        #If we are anything related to store, all registers are source
        if self.is_memory_store():
            num_dest_regs=0
        #If we are a load pair, first two registers are dest
        if self.mnemonic == "ldp":
            num_dest_regs=2

        self.src_regs=[]
        self.dst_regs=[]

        for i in range(0,num_dest_regs):
            if len(linematch) > i:
                self.dst_regs.append(linematch[i])
        for i in range(num_dest_regs,len(linematch)):
            self.src_regs.append(linematch[i])

    def is_branch(self):
        #check if the instruction is a branch
        # return re.search("<[^<>]*>", self.disassembly) != None
        return re.match("b.*", self.mnemonic) != None and re.search("<[^<>]*>", self.disassembly) != None
    def is_cond_branch(self):
        #check if the instruction is a conditional branch
        return re.search("b\.", self.mnemonic) != None
    def branch_target(self):
        #return the target of the branch
        linematch=re.match(".*<([^<>]*)>.*", self.disassembly)
        return linematch.group(1)
    def is_return(self):
        #check if the instruction is a return
        return self.mnemonic == "ret"
    def is_linked_branch(self):
        #check if the instruction is a linked branch
        return self.mnemonic == "bl"
    def is_memory_access(self):
        #check if the instruction is a memory access
        return re.search("ld|st", self.mnemonic) != None
    def is_memory_load(self):
        #check if the instruction is a memory access
        return re.search("ld", self.mnemonic) != None
    def is_memory_store(self):
        #check if the instruction is a memory access
        return re.search("st", self.mnemonic) != None
    
    def __str__(self):
        labeltext=self.disassembly+" s "+str(self.src_regs)+" d "+str(self.dst_regs)+" m "+str(self.recommendation_miss)
        if self.recommendation_miss > 0:
            labeltext="**"+labeltext+"**"
        return labeltext

address_bb_map = {}
dotfile_map = {}

populate_list=[]
jr_target_list=[]

class BasicBlock:
    start_label=""
    start_address=0
    instructions=[]
    jmp_targets=[]
    #Need to keep track of possible jr allocations
    jr_targets=[]

    def __init__(self, label):
        self.start_label=label
        self.start_address=label_to_address(label)
        self.instructions=[]
        self.jmp_targets=[]
        self.jr_targets=[]
        self.link_targets=[]
        self.to_map()

    def populate_block(self):
        #populate the block with instructions
        self.instructions.append(Instruction(self.start_address))
        while not (self.instructions[-1].is_branch() or self.instructions[-1].is_return()):
            nextaddr=label_to_address(self.instructions[-1].address+"+4")
            nexti=Instruction(nextaddr)
            self.instructions.append(nexti)
        if(self.instructions[-1].is_branch()):
            target_lab=self.instructions[-1].branch_target()
            target_addr=label_to_address(target_lab)
            if target_addr != None and is_in_text(target_addr):
                self.jmp_targets.append(target_addr)
            if self.instructions[-1].is_cond_branch():
                #add the fall through target
                if is_in_text(label_to_address(self.instructions[-1].address+"+4")):
                    self.jmp_targets.append(label_to_address(self.instructions[-1].address+"+4"))
            for jmp_target in self.jmp_targets:
                if jmp_target not in address_bb_map:
                    jblock=BasicBlock(jmp_target)
                    # jblock.populate_block()
                    populate_list.append(jblock)
            if self.instructions[-1].is_linked_branch():
                #add the return address as a jr target
                link_address=label_to_address(self.instructions[-1].address+"+4")
                # print("Linked branch at "+self.instructions[-1].address+" to "+label_to_address(self.instructions[-1].branch_target())+" with link address "+link_address)
                if link_address not in address_bb_map:
                    jblock=BasicBlock(link_address)
                    # jblock.populate_block()
                    populate_list.append(jblock)
                self.link_targets.append(link_address)
                
                if target_addr != None and is_in_text(target_addr):
                    address_bb_map[target_addr].push_jr_target(link_address)
                else:
                    self.jmp_targets.append(link_address)

    def to_map(self):
        address_bb_map[self.start_address]=self

    def push_jr_target(self, jr_target):
        # print("pushing jr target "+jr_target+" to "+self.start_address)
        #Only cash the target here
        if jr_target not in self.jr_targets:
            self.jr_targets.append(jr_target)

    def finalize_jr_targets(self, visitlist=[]):
        #populate jr targets
        if len(self.jr_targets) == 0:
            return
        if self in visitlist:
            #Already called this note, cycles are not needed
            return
        if not self.instructions[-1].is_return():
            #A return consumes jr targets, if we do not end with a return, push through, to all jump targets and to all link targets
            visitlist.append(self)
            for jmp_target in self.jmp_targets:
                # Do not push through to other jumps
                if address_bb_map[jmp_target].instructions[-1].is_linked_branch():
                    #A link will overvwrite the return addresses, therefore no push. The link address, will consume the return
                    for link_target in address_bb_map[jmp_target].link_targets:
                        for jr_target in self.jr_targets:
                            address_bb_map[link_target].push_jr_target(jr_target)
                        address_bb_map[link_target].finalize_jr_targets(visitlist)
                    continue
                #Move all jr targets to the lower blocks
                if address_bb_map[jmp_target] not in visitlist:
                    for jr_target in self.jr_targets:
                            address_bb_map[jmp_target].push_jr_target(jr_target)
                    address_bb_map[jmp_target].finalize_jr_targets(visitlist)
            self.jr_targets=[]


    def populate_dotfile(self):
        codeblock=""
        for ins in self.instructions:
            codeblock+=str(ins)+"\\l"
        mycode="\""+self.start_address+"\" [label=\"" +self.start_label + ":\\n"+codeblock+"\" shape=box];\n"
        for jmp_target in self.jmp_targets:
            mycode+="\""+self.start_address+"\" -> \""+jmp_target + "\" [color=red];\n"
        for jr_target in self.jr_targets:
            mycode+="\""+self.start_address+"\" -> \""+jr_target + "\" [color=green];\n"
        dotfile_map[self.start_address]=mycode
        for jmp_target in self.jmp_targets:
            if jmp_target not in dotfile_map:
                address_bb_map[jmp_target].populate_dotfile()
        for jr_target in self.jr_targets:
            if jr_target not in dotfile_map:
                address_bb_map[jr_target].populate_dotfile()

bb_m=BasicBlock("main")
populate_list=[bb_m]
print("Populating basic blocks")
while len(populate_list) > 0:
    populate_list.pop(0).populate_block()
print("Finalizing jr targets")
for bb in address_bb_map:
    address_bb_map[bb].finalize_jr_targets()

# print("Writing dotfile")
# bb_m.populate_dotfile()

# dotfile=open("cfg.dot","w")
# dotfile.write("digraph G {\n")
# for addr in dotfile_map:
#     dotfile.write(dotfile_map[addr])
# dotfile.write("}")
# dotfile.close()

# os.system("dot -Tpdf cfg.dot -o cfg.pdf")

print("Done with CFG")

#Output first and last instuction address of main in a seperate file
mainfile=open("main.txt","w")
mainfile.write(bb_m.start_address+"\n")

#Get the last insztruction from main from readelf
result=subprocess.check_output("readelf -s "+filename+" | grep main", shell=True)
result = result.decode("utf-8")
result=result.replace("\t"," ")
linematch=re.search("[^:]: [0-9a-f]* *([0-9]*) [A-Za-z0-9 ]* main\n",result)
main_len=int(linematch.group(1))
main_last_address=int(bb_m.start_address,16)+main_len-4
mainfile.write(hex(main_last_address)+"\n")

mainfile.close()

#Now provide the RT mapping recommendations

def racetrack_stats(bb,iidx):
    #Create the possible paths
    paths=[[(bb,iidx)]]
    full_paths=[]

    total_v1_rating=0
    total_v2_rating=0

    #Enumerate all paths with defined length
    while len(paths) > 0:
        path=paths.pop(0)
        #Fill up until end of basic block
        nextidx=path[-1][1]+1
        mybb=path[-1][0]
        while nextidx < len(mybb.instructions) and len(path) < racetrack.execution_window:
            path.append((path[-1][0],nextidx))
            nextidx+=1
        #Check if we aborted due to full window
        if len(path) == racetrack.execution_window:
            full_paths.append(path)
            continue
        #We are at the end of the block, spawn all possible continuations
        for jmp_target in mybb.jmp_targets:
            if jmp_target in address_bb_map:
                #Ecldue cycle
                if address_bb_map[jmp_target] in [x[0] for x in path]:
                    full_paths.append(path)
                    continue
                paths.append(path+[(address_bb_map[jmp_target],0)])
        for jr_target in mybb.jr_targets:
            if jr_target in address_bb_map:
                #Ecldue cycle
                if address_bb_map[jr_target] in [x[0] for x in path]:
                    full_paths.append(path)
                    continue
                paths.append(path+[(address_bb_map[jr_target],0)])
        #If there is no continuation, this is a full path
        if len(bb.jmp_targets) == 0 and len(mybb.jr_targets) == 0:
            full_paths.append(path)

    #Now evaluate the rating for all paths
    for path in full_paths:
        #Reset the racetrack
        racetrack.reset()
        for bb,iidx in path:
            isn=bb.instructions[iidx]
            for src in isn.src_regs:
                if src.find("x") == 0 or src.find("w") == 0:
                    racetrack.next_access( int(src.replace("x","").replace("w","")) )
            for dst in isn.dst_regs:
                if dst.find("x") == 0 or dst.find("w") == 0:
                    racetrack.next_access( int(dst.replace("x","").replace("w","")) )

        v1,v2=racetrack.get_version_counters()
        total_v1_rating+=v1
        total_v2_rating+=v2
    return total_v1_rating, total_v2_rating

rtstatfile=open("rtstats.csv","w")
rtstatfile.write("Address,V1,V2\n")

missmap=None

#Check if a shiftresults.csv file exists
if os.path.exists("shiftresults.csv"):
    missmap={}
    #read the recommendations file and build a map
    rstatsfile=open("shiftresults.csv","r")
    skip_first_line=True
    for line in rstatsfile:
        line=line.strip()
        if line:
            if skip_first_line:
                skip_first_line=False
                continue
            parts=line.split(",")
            #Check if the address is in the miss map already
            prev_val=0
            if int(parts[0],16) in missmap:
                prev_val=missmap[int(parts[0],16)]
            missmap[int(parts[0],16)] = prev_val+(1 if int(parts[1])<int(parts[2]) and int(parts[3])==2 else 0)

#Iterate over all instructions and write a statistics table
for bb in address_bb_map:
    for iidx in range(0,len(address_bb_map[bb].instructions)):
        v1,v2=racetrack_stats(address_bb_map[bb],iidx)
        rtstatfile.write(address_bb_map[bb].instructions[iidx].address+","+str(v1)+","+str(v2)+"\n")
        if missmap != None:
            if int(address_bb_map[bb].instructions[iidx].address,16) in missmap:
                print("Found recommendation for "+address_bb_map[bb].instructions[iidx].address+" with "+str(missmap[int(address_bb_map[bb].instructions[iidx].address,16)]))
                address_bb_map[bb].instructions[iidx].recommendation_miss=missmap[int(address_bb_map[bb].instructions[iidx].address,16)]

#Draw CFG
print("Writing dotfile")
bb_m.populate_dotfile()

dotfile=open("cfg.dot","w")
dotfile.write("digraph G {\n")
for addr in dotfile_map:
    dotfile.write(dotfile_map[addr])
dotfile.write("}")
dotfile.close()

os.system("dot -Tpdf cfg.dot -o cfg.pdf")
        
rtstatfile.close()

print(racetrack_stats(bb_m,0))