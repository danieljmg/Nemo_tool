from z3 import *
#import time
#start = time.time()
g = Goal()

#It starts in tsetin variable '1'
#initvar = 1
#auxinitvars = BitVec('auxinitvars', initvar)

vars = []
bitvecsvars = ""

#Input model NFs initialisation
stringvars = ['a', 'b', 'c', 'd']
for modelnamevar in stringvars:
    bitvecsvars+= modelnamevar+' '
vars =  BitVecs(bitvecsvars[:-1], 3)

#Necessary to get rido of k!0 as the first variable involved (which we want to erase to start with variable 1)
#g.add(auxinitvars == 1) #necessary to get rid

#NFM Constraints
#g.add(ULE(vars[0], vars[1]), UGE(vars[1], vars[0]), vars[0] == 1, UGT(vars[2], vars[3]))
g.add(ULT(vars[3], 4), ULE(vars[0] + vars[1] + vars[2], vars[3]))
#g.add(vars[0] * (vars[1] + vars[2]) == vars[3], vars[0] == 1)
#g.add(vars[0] >= vars[1], vars[0] == 1, vars[2] != vars[3], vars[2] == 1)
#g.add(vars[0] + vars[1] == 2, vars[1] == 1)

t = Then('simplify', 'bit-blast', 'tseitin-cnf')
subgoal = t(g)
assert len(subgoal) == 1
print(subgoal[0])
print(g)