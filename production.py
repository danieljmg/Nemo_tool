from z3 import *
from files import readNFM
import re
# import time
# start = time.time()

modelname = "model"
f = open(f"{modelname}.dimacs", "w")

booleanmodelname = "" #"modeltest.dimacs"

constraints = Goal()

##### Input model NFs initialisation #####
file_vars = []
file_cts = []
filepath = 'testmodel.txt'
##### Parse, adjust and optimise NFM #####
(file_vars, file_cts) = readNFM(filepath, file_vars, file_cts)
print(f'Defined variables (Name, Adjusted_width, Type) = {file_vars}')
print(f'Adjusted constraints = {file_cts}')

auxf= open("auxdefs.py","w+")
auxf.write("from z3 import *\n")
auxf.write("def embeed(constraints):")
##### Define NFM variables in Z3py format #####
for file_var in file_vars:
    if file_var[2] == 'boolean':
        auxf.write(f"\n    {file_var[0]} = Bool('{file_var[0]}')")
    else:
        auxf.write(f"\n    {file_var[0]} = BitVec('{file_var[0]}', {file_var[1]})")

##### Define NFM constraints in Z3py format #####
for file_ct in file_cts:
    auxf.write(f"\n    constraints.add({file_ct})")
##### Close the file and execute the dinamically generated code #####
auxf.close()
from auxdefs import embeed
embeed(constraints)

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
    complexstrconstraint = str(constraint).replace('Not(', '')
    complexstrconstraint = str(constraint).replace('(', '')
    complexstrconstraint = complexstrconstraint.replace(')', '')

    if 'Implies' in complexstrconstraint:
        ##### Sequential Order #####
        found_complex_ops = complexstrconstraint[7:].split(', ')
    elif 'Or' in complexstrconstraint:
        ##### Sequential Order #####
        found_complex_ops = complexstrconstraint[2:].split(', ')
    elif 'And' in complexstrconstraint:
        ##### Sequential Order #####
        found_complex_ops = complexstrconstraint[2:].split(', ')
    else:
        found_complex_ops = [complexstrconstraint]

    for strconstraint in found_complex_ops:
        if any(op in ['ULT', 'UGE'] for op in strconstraint):
            ##### Reverse Order #####
            found_ops = strconstraint[4:-1].split(', ')[::-1]
        elif " < " in strconstraint:
            ##### Reverse Order #####
            found_ops = strconstraint.split(' < ')[::-1]
        elif " >= " in strconstraint:
            ##### Reverse Order #####
            found_ops = strconstraint.split(' >= ')[::-1]
        elif " <= " in strconstraint:
            ##### Sequential Order #####
            found_ops = strconstraint.split(' <= ')
        elif " > " in strconstraint:
            ##### Sequential Order #####
            found_ops = strconstraint.split(' > ')
        elif " == " in strconstraint:
            ##### Sequential Order #####
            found_ops = strconstraint.split(' == ')
        elif " != " in strconstraint:
            ##### Sequential Order #####
            found_ops = strconstraint.split(' !=')
        elif any(op in ['ULE', 'UGT'] for op in strconstraint):
            ##### Sequential Order #####
            found_ops = strconstraint[4:-1].split(', ')
        elif any(op in ['UDiv', 'URem'] for op in strconstraint):
            ##### Sequential Order #####
            found_ops = strconstraint[5:-1].split(', ')
        else:
            found_ops = [strconstraint]

        equation_vars = re.split(' \+ | - |\*|/|%', found_ops[0])
        if len(found_ops) > 1:
            equation_vars += re.split(' \+ | - |\*|/|%', found_ops[1])
        for found_var in equation_vars:
            if not found_var.isnumeric() and found_var not in bitvarsmap: bitvarsmap.append(found_var)

##### Initialise var and clauses counters, and write variables of the second model depending on its existence #####
initconstraints = 0
if(booleanmodelname):
    with open(booleanmodelname) as input_file:
        input_file_content = input_file.read().splitlines()
        for input_line in input_file_content:
            if 'c ' == input_line[0:2]:
                f.write(input_line)
                f.write("\n")
            elif 'p cnf ' == input_line[0:6]:
                vars_and_constraints = input_line[6:].split(' ')
                initvars = int(vars_and_constraints[0])+1
                initconstraints = int(vars_and_constraints[1])
else: initvars = 1

##### Identify true variables #####
varcounter = initvars
##### Mapping of Boolean vars and their ids #####
booleanvarsids = []
num_predifined_booleans = 0
for bitvar in bitvarsmap:
    # si es booleano 1, si no el bit width
    ##### Look for type and width #####
    for auxvardefs in file_vars:
        if auxvardefs[0] == bitvar:
            auxvardef = auxvardefs

    if auxvardef[2] == 'boolean':
        if auxvardef[1] == 0:
            f.write(f"c {varcounter} {bitvar} boolean")
            f.write("\n")
            booleanvarsids.append([bitvar, varcounter])
            varcounter += 1
        else:
            f.write(f"c {auxvardef[1]} {bitvar} boolean")
            f.write("\n")
            num_predifined_booleans += 1
            booleanvarsids.append([bitvar, auxvardef[1]])
    else:
        for bit in range(1, auxvardef[1] + 1):
            # print(f"c {varcounter} {bitvar}_{bit}")
            f.write(f"c {varcounter} {bitvar}_{bit}")
            f.write("\n")
            varcounter += 1

numvars = len(z3util.get_vars(subgoal.as_expr())) - num_predifined_booleans

##### Followed by Tseitin variables #####
tseitincounter = 1
for totalvarsid in range (varcounter, numvars+initvars):
    #print(f"c {auxvarsid} Tseitin_Variable_{tseitincounter}")
    f.write(f"c {totalvarsid} Tseitin_Variable_{tseitincounter}")
    f.write("\n")
    tseitincounter += 1

##### Transform Z3 output to DIMACS CNF NFM #####
#print(f"p cnf {numvars} {maxrange}")
f.write(f"p cnf {totalvarsid} {maxrange+initconstraints}")
f.write("\n")

##### Add caluses of the second model if needed #####
if(booleanmodelname):
    with open(booleanmodelname) as input_file:
        input_file_content = input_file.read().splitlines()
        for input_line in input_file_content:
            if (input_line[0:1].isdigit()):
                f.write(input_line)
                f.write("\n")

for c in range (maxrange):
    aux = str(subgoal[0][c]).replace("Or(", "")
    aux = aux.replace("k!", "")
    aux = aux.replace("Not(", "-")
    aux = aux.replace("))", "")
    aux = aux.replace(")", "")
    aux = aux.replace(",", "")
    ##### Replace booleans by their ids #####
    for bv in booleanvarsids:
        aux = aux.replace(bv[0], str(bv[1]))

    aux = aux.replace("Fa", "1000")
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