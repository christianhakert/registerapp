import bap

proj = bap.run('main')
main = proj.program.subs.find('main')
entry = main.blks[0]

#Print the basic block
for definition in main.blks[0].defs:

    o_reg_1=""

    i_reg_1=""
    i_reg_2=""

    address=definition.attrs['address']
    insn=definition.attrs['insn']
    output_reg=definition.lhs
    if isinstance(output_reg,bap.bil.Var):
        o_reg_1=output_reg.name
    operation=definition.rhs
    if isinstance(operation,bap.bil.Exp):
        
    print(definition.attrs['address'] + " " + definition.attrs['insn'])

next = main.blks.find(entry.jmps[0].target.arg)