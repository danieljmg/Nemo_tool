from z3 import *
import time
start = time.time()
g = Goal()
initvar = 1
auxinitvars = BitVec('auxinitvars', initvar)
#In Z3Py, the operators <, <=, >, >=, /, % and >> correspond to the signed versions. The corresponding unsigned operators are ULT, ULE, UGT, UGE, UDiv, URem and LShR
#NF_GZIP_FAST = BitVec('NF_GZIP_FAST', 1)
#g.add(ULE(a, b), b == 1)
vars = []
#stringvars = ['a', 'b']
#vars =  BitVecs('a b', 2)
stringvars = ['NF_FEATURE_SYSLOGD_READ_BUFFER_SIZE']
vars =  BitVecs('NF_FEATURE_SYSLOGD_READ_BUFFER_SIZE', 6)
#g.add(x == 1,UGT(vars[0],vars[1]), vars[1] == 0)
#g.add(auxinitvars == 1, ULE(vars[0], vars[1]), UGE(vars[0], vars[1]), vars[0] == 0)
g.add(auxinitvars == 1, ULE(vars[0], 32))
#g.add(UGE(a, 0), ULE(a, 10))
#And(NF_FIRST_SYSTEM_ID >= 0, NF_FIRST_SYSTEM_ID <= NF_LAST_ID)
#NF_FIRST_SYSTEM_ID, NF_LAST_ID = BitVecs('NF_FIRST_SYSTEM_ID NF_LAST_ID', 10)
#g.add(UGE(NF_FIRST_SYSTEM_ID, NF_LAST_ID))
t = Then('simplify', 'bit-blast', 'tseitin-cnf')
subgoal = t(g)
assert len(subgoal) == 1
# Traverse each clause of the first subgoal
maxrange = len(subgoal[0])
varcounter = 1
ordervars = 0
tempg = []
tempg.append(g[1])
for constraint in tempg:
    if not str(constraint) == "auxinitvars == 1":
        if "==" in str(constraint) or "!=" in str(constraint) or "ULE" in str(constraint) or "UGT" in str(constraint):
            ordervars = 1
        elif "ULT" in str(constraint) or "UGE" in str(constraint):
            ordervars = -1
        #elif "ULT" in constraint:
if ordervars == 1:
    counter = 0
    for literal in vars:
        aux = literal.size()
        for bit in range (1, aux+1):
            print(f"c {varcounter} {stringvars[counter]}_{bit}")
            varcounter += 1
        counter += 1
elif ordervars == -1:
    counter = len(stringvars)-1
    for literal in list(reversed(vars)):
        aux = literal.size()
        for bit in range (1, aux+1):
            print(f"c {varcounter} {stringvars[counter]}_{bit}")
            varcounter += 1
        counter -= 1
numvars = len(z3util.get_vars(subgoal.as_expr()))-initvar
tseitincounter = 1
for auxvarsid in range (varcounter, numvars+1):
    print(f"c {auxvarsid} tseitinvar_{tseitincounter}")
    tseitincounter += 1

print(f"p cnf {numvars} {maxrange}")
for c in range (initvar, maxrange):
    aux = str(subgoal[0][c]).replace("Or(", "")
    aux = aux.replace("k!", "")
    aux = aux.replace("Not(", "-")
    aux = aux.replace("))", "")
    aux = aux.replace(")", "")
    aux = aux.replace(",", "")
    print(aux+' 0')