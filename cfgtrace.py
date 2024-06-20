#This tool uses gdb calls to build up a control flow graph and analyze source and destination registers

import subprocess
import sys
import re

filename = sys.argv[1]

def query_gdb(sect):
    result = subprocess.check_output("gdb -batch -ex 'disas "+sect+",+1' "+filename, shell=True)
    #convert result to string
    result = result.decode("utf-8")
    linematch=re.findall("0x[0-9a-fA-F]* <[^<>]*>:[^\n]*", str(result))
    linematch=linematch[0]
    return(str(linematch))

def split_gdb_line(line):
    linematch=re.match("(0x[0-9a-fA-F]*) (<[^<>]*>):(.*)", str(line))
    return linematch.group(1),linematch.group(2),linematch.group(3)

def label_to_address(label):
    addr,lab,insn=split_gdb_line(query_gdb(label))
    return addr

class Instruction:
    address = 0
    disassembly = ""
    mnemonic = ""
    src_regs=[]
    dst_regs=[]

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

    def is_branch(self):
        #check if the instruction is a branch
        return re.search("<[^<>]*>", self.disassembly) != None
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
    
    def __str__(self):
        return self.disassembly

address_bb_map = {}
dotfile_map = {}

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
            self.jmp_targets.append(target_addr)
            if self.instructions[-1].is_cond_branch():
                #add the fall through target
                self.jmp_targets.append(label_to_address(self.instructions[-1].address+"+4"))
            for jmp_target in self.jmp_targets:
                if jmp_target not in address_bb_map:
                    jblock=BasicBlock(jmp_target)
                    jblock.populate_block()
            if self.instructions[-1].is_linked_branch():
                #add the return address as a jr target
                print("pushing jr target to "+target_addr)
                link_address=label_to_address(self.instructions[-1].address+"+4")
                if link_address not in address_bb_map:
                    jblock=BasicBlock(link_address)
                    jblock.populate_block()
                address_bb_map[target_addr].push_jr_target(link_address)

    def to_map(self):
        address_bb_map[self.start_address]=self

    def push_jr_target(self, jr_target):
        #populate jr targets
        if not self.instructions[-1].is_return():
            #A return consumes jr targets, if we do not end with a return, push through
            for jmp_target in self.jmp_targets:
                address_bb_map[jmp_target].push_jr_target(jr_target)
        else:
            self.jr_targets.append(jr_target)

    def populate_dotfile(self):
        codeblock=""
        for ins in self.instructions:
            codeblock+=ins.disassembly+"\\n"
        mycode="\""+self.start_address+"\" [label=\"" +self.start_label + ":\\n"+codeblock+"\"];\n"
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
bb_m.populate_block()

for addr in address_bb_map:
    print(address_bb_map[addr].start_label)
    for ins in address_bb_map[addr].instructions:
        print(ins)
    for jmp in address_bb_map[addr].jmp_targets:
        print("->"+jmp)
    for jmp in address_bb_map[addr].jr_targets:
        print("-->"+jmp)
    print("")

bb_m.populate_dotfile()

dotfile=open("cfg.dot","w")
dotfile.write("digraph G {\n")
for addr in dotfile_map:
    dotfile.write(dotfile_map[addr])
dotfile.write("}")
dotfile.close()

# main_addr=label_to_address("0x400710")
# ins=Instruction(main_addr)
# ins.is_branch()

# print(address_bb_map)
# print(main_addr)
# print(query_gdb(main_addr))