from z3 import *
import re
# import time
# start = time.time()

modelname = "model"
f = open(f"{modelname}.cnf", "w")

initvars = 1
constraints = Goal()

vars = []
bitvecsvars = ""

##### Input model NFs initialisation #####
stringvars = ['a', 'b', 'c', 'd']
for modelnamevar in stringvars:
    bitvecsvars += modelnamevar+' '
vars =  BitVecs(bitvecsvars[:-1], 3)


##### NFM Constraints #####
# If var >= 0 (often the case) we should use unsigned, otherwise signed
# g.add(ULE(vars[0], vars[1]), UGE(vars[0], vars[1]), vars[0] == 0)
# g.add(UGT(vars[1], vars[0]), ULE(vars[0], vars[1]))
constraints.add(vars[0] * (vars[1] + vars[2]) == vars[3], vars[0] == 1)

##### constraints == Constraints array || subgoal[0] == CNF PF #####
t = Then('simplify', 'bit-blast', 'tseitin-cnf')
subgoal = t(constraints)
assert len(subgoal) == 1
# print(subgoal[0])

##### Traverse each clause of the first subgoal #####
maxrange = len(subgoal[0])

bitvarsmap = []
# If the model contain constraints...
for constraint in constraints:
    print(constraint)
    # Remove parenthesis
    strconstraint = str(constraint).replace('(', '')
    strconstraint = strconstraint.replace(')', '')

    if "ULT" in strconstraint or "UGE" in strconstraint:
        # Reverse Order
        found_ops = strconstraint[4:-1].split(', ')[::-1]
    elif "<" in strconstraint:
        # Reverse Order
        found_ops = strconstraint.split(' < ')[::-1]
    elif ">=" in strconstraint:
        # Reverse Order
        found_ops = strconstraint.split(' >= ')[::-1]
    elif "<=" in strconstraint:
        # Sequential Order
        found_ops = strconstraint.split(' <= ')
    elif ">" in strconstraint:
        # Sequential Order
        found_ops = strconstraint.split(' > ')
    elif "==" in strconstraint:
        # Sequential Order
        found_ops = strconstraint.split(' == ')
    elif "!=" in strconstraint:
        # Sequential Order
        found_ops = strconstraint.split(' !=' )
    elif "ULE" in strconstraint or "UGT" in strconstraint or "UDiv" in strconstraint or "URem" in strconstraint:
        # Sequential Order
        found_ops = strconstraint[4:-1].split(', ')
    equation_vars = re.split(' \+ | - |\*|/|%|UDiv|URem',found_ops[0])
    equation_vars += re.split(' \+ | - |\*|/|%|UDiv|URem',found_ops[1])
    for found_var in equation_vars:
        if not found_var.isnumeric() and found_var not in bitvarsmap: bitvarsmap.append(found_var)

# Identify true variables
varcounter = 1
for bitvar in bitvarsmap:
    for bit in range (1, 4):
        print(f"c {varcounter} {bitvar}_{bit}")
        f.write(f"c {varcounter} {bitvar}_{bit}")
        f.write("\n")
        varcounter += 1

numvars = len(z3util.get_vars(subgoal.as_expr()))

# Followed by Tseitin variables
tseitincounter = 1
for auxvarsid in range (varcounter, numvars+1):
    print(f"c {auxvarsid} Tseitin_Variable_{tseitincounter}")
    f.write(f"c {auxvarsid} Tseitin_Variable_{tseitincounter}")
    f.write("\n")
    tseitincounter += 1

# Transform Z3 output to DIMACS CNF NFM
print(f"p cnf {numvars} {maxrange}")
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
    print(updatedaux+'0')
    f.write(updatedaux+'0')
    f.write("\n")
f.close()

# Some OPS are just twisted operations=> Some variables will be declared in reverse order