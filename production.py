from z3 import *
from files import readNFM
import re
# import time
# start = time.time()

modelname = "model"
f = open(f"{modelname}.dimacs", "w")

initvars = 1
constraints = Goal()

##### Input model NFs initialisation #####
file_vars = []
file_cts = []
filepath = 'complmodel.txt'
##### Parse, adjust and optimise NFM #####
(file_vars, file_cts) = readNFM(filepath, file_vars, file_cts)
print(f'Defined variables (Name, Adjusted_width, Type) = {file_vars}')
print(f'Adjusted constraints = {file_cts}')

##### Define NFM variables in Z3py format #####
for file_var in file_vars:
    exec(f"{file_var[0]} = BitVec('{file_var[0]}', {file_var[1]})")

##### Define NFM constraints in Z3py format #####
for file_ct in file_cts:
    exec(f'constraints.add({file_ct})')

##### constraints == Constraints array || subgoal[0] == CNF PF #####
t = Then('simplify', 'bit-blast', 'tseitin-cnf')
subgoal = t(constraints)
assert len(subgoal) == 1
#print(subgoal[0])

##### Traverse each clause of the first subgoal #####
maxrange = len(subgoal[0])

bitvarsmap = []
##### If the model contain constraints ... #####
for constraint in constraints:
    #print(constraint)
    ##### Remove parenthesis #####
    strconstraint = str(constraint).replace('(', '')
    strconstraint = strconstraint.replace(')', '')

    if "ULT" in strconstraint or "UGE" in strconstraint:
        ##### Reverse Order #####
        found_ops = strconstraint[4:-1].split(', ')[::-1]
    elif "<" in strconstraint:
        ##### Reverse Order #####
        found_ops = strconstraint.split(' < ')[::-1]
    elif ">=" in strconstraint:
        ##### Reverse Order #####
        found_ops = strconstraint.split(' >= ')[::-1]
    elif "<=" in strconstraint:
        ##### Sequential Order #####
        found_ops = strconstraint.split(' <= ')
    elif ">" in strconstraint:
        ##### Sequential Order #####
        found_ops = strconstraint.split(' > ')
    elif "==" in strconstraint:
        ##### Sequential Order #####
        found_ops = strconstraint.split(' == ')
    elif "!=" in strconstraint:
        ##### Sequential Order #####
        found_ops = strconstraint.split(' !=' )
    elif "ULE" in strconstraint or "UGT" in strconstraint or "UDiv" in strconstraint or "URem" in strconstraint:
        ##### Sequential Order #####
        found_ops = strconstraint[4:-1].split(', ')
    equation_vars = re.split(' \+ | - |\*|/|%|UDiv|URem',found_ops[0])
    equation_vars += re.split(' \+ | - |\*|/|%|UDiv|URem',found_ops[1])
    for found_var in equation_vars:
        if not found_var.isnumeric() and found_var not in bitvarsmap: bitvarsmap.append(found_var)

##### Identify true variables #####
varcounter = 1
for bitvar in bitvarsmap:
    for bit in range (1, 4):
        #print(f"c {varcounter} {bitvar}_{bit}")
        f.write(f"c {varcounter} {bitvar}_{bit}")
        f.write("\n")
        varcounter += 1

numvars = len(z3util.get_vars(subgoal.as_expr()))

##### Followed by Tseitin variables #####
tseitincounter = 1
for auxvarsid in range (varcounter, numvars+1):
    #print(f"c {auxvarsid} Tseitin_Variable_{tseitincounter}")
    f.write(f"c {auxvarsid} Tseitin_Variable_{tseitincounter}")
    f.write("\n")
    tseitincounter += 1

##### Transform Z3 output to DIMACS CNF NFM #####
#print(f"p cnf {numvars} {maxrange}")
f.write(f"p cnf {numvars} {maxrange}")
f.write("\n")
for c in range (maxrange):
    aux = str(subgoal[0][c]).replace("Or(", "")
    aux = aux.replace("k!", "")
    aux = aux.replace("Not(", "-")
    aux = aux.replace("))", "")
    aux = aux.replace(")", "")
    aux = aux.replace(",", "")
    ##### UPDATING THE NUMBER OF VARIABLE (VAR_ID) #####
    auxarray = aux.split(' ')
    updatedaux = ''
    for literalvar in auxarray:
        numliteralvar = int(literalvar)
        if numliteralvar < 0:
            updatedaux += str(numliteralvar - initvars) + ' '
        else:
            updatedaux += str(numliteralvar + initvars) + ' '
    #print(updatedaux+'0')
    f.write(updatedaux+'0')
    if(c < maxrange-1): f.write("\n")
f.close()